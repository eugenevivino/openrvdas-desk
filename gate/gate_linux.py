"""Collect Linux gate evidence with the system Python in isolated mode."""
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from xml.etree.ElementTree import ParseError

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # -I excludes the current directory.
import gate_lib as lib  # noqa: E402


def unique_keys(pairs):
    obj = dict(pairs)
    lib.require(len(obj) == len(pairs), "duplicate JSON evidence field")
    return obj


def invalid_number(token):
    raise ValueError(f"invalid JSON number in pytest collection: {token}")


def capture(argv, *, cwd=None, env=None, stdin=None):
    result = subprocess.run(argv, cwd=cwd, env=env, stdin=stdin,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lib.require(result.returncode == 0,
                f"{argv[0]} {argv[1]} exited {result.returncode}: "
                + result.stderr.decode(errors="replace").strip())
    return result.stdout


def logged(argv, log, cwd, env):
    with log.open("wb") as stream:
        return subprocess.run(argv, cwd=cwd, env=env, stdout=stream,
                              stderr=subprocess.STDOUT).returncode


def parse_lint(raw, path):
    # In a one-file invocation the benchmark identifies whether this exact
    # argument reached the checker. --count is the last line on completion.
    lines = raw.decode().split("\n")
    reason = f"flake8 did not complete for {path}"
    lib.require(len(lines) >= 4 and lines[-1] == "" and
                re.fullmatch(r"0|[1-9][0-9]*", lines[-2]), reason)
    benchmarks = ["seconds elapsed"]
    for unit in ("logical lines", "physical lines", "tokens", "files"):
        benchmarks.extend([f"total {unit} processed",
                           f"{unit} processed per second"])
    start = len(lines) - 2 - len(benchmarks)
    lib.require(start >= 0, reason)
    metrics = {}
    for label, line in zip(benchmarks, lines[start:-2]):
        number, separator, observed = line.partition(" ")
        lib.require(separator and observed.lstrip() == label, reason)
        pattern = (r"[0-9]+(?:\.[0-9]+)?(?:e[+-]?[0-9]+)?"
                   if label == "seconds elapsed" else r"0|[1-9][0-9]*")
        lib.require(re.fullmatch(pattern, number), reason)
        metrics[label] = number
    return {"findings": lines[:start], "count": int(lines[-2]),
            "processed": int(metrics["total files processed"])}


def collect(f, fork_arg, rec, rows):
    env = os.environ.copy()
    for key in ("GITHUB_ENV", "GITHUB_OUTPUT", "GITHUB_PATH", "GITHUB_STATE",
                "GITHUB_STEP_SUMMARY", "PYTEST_ADDOPTS", "PYTEST_PLUGINS"):
        env.pop(key, None)
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_NO_REPLACE_OBJECTS="1")
    sha = f["requested"]
    lib.require(re.fullmatch("[0-9a-f]{40}", sha), "need a full 40-hex sha")
    f["system"] = capture(["uname", "-s"]).decode().strip()
    lib.require(f["system"] == "Linux", "Linux runner required")
    version = subprocess.run(["python3", "-I", "-c",
                              "import sys; print(sys.version.split()[0])"],
                             stdout=subprocess.PIPE, check=False)
    f["python"] = version.stdout.decode().strip()
    lib.require(version.returncode == 0, "Python 3.12 required")
    release = capture(["bash", "-c", 'source /etc/os-release && '
                       'printf "%s\\n%s\\n" "$ID" "$VERSION_ID"'])
    f["distribution"], f["release"] = release.decode().splitlines()
    (rec / "meta.txt").write_text(
        f"sha={sha}\nhost={socket.gethostname()}\npython={f['python']}\n"
        f"ID={f['distribution']}\nVERSION_ID={f['release']}\n")
    lib.platform_proof(f)
    lib.require(fork_arg and Path(fork_arg).is_dir(),
                "fork checkout unavailable")
    fork = Path(fork_arg).resolve()

    def git(*args):
        return capture(["git", "-C", str(fork), *args], env=env)

    f["origin"] = git("remote", "get-url", "origin").decode().strip()
    f["head"] = git("rev-parse", "--verify", "HEAD").decode().strip()
    lib.require(sha == f["head"], "fork HEAD does not match request")
    ref = git("for-each-ref", "--contains", sha, "--count=1",
              "--format=%(refname)", "refs/remotes/origin/")
    f["ref"] = ref.decode().strip()
    lib.runner_proof(f)
    f["expected"] = []
    for line in (HERE / "expected-failures.txt").read_text().splitlines():
        name = line.partition("#")[0].strip()
        if name:
            f["expected"].append(name)
    base = git("merge-base", sha, "refs/remotes/origin/dev").decode().strip()
    raw = git("diff", "--name-only", "-z", "--no-renames", "--no-relative",
              "--ignore-submodules=none", base, sha, "--")
    (rec / "changed.txt").write_bytes(raw)
    changes = lib.nul_records(raw)
    f["paths"] = list(map(os.fsdecode, changes))

    def tree(commit):
        return lib.tree_entries(git("ls-tree", "-r", "-t", "-z",
                                    "--full-tree", commit))

    head = tree(sha)
    f["changed"] = lib.changed_entries(changes, tree(base), head)
    paths = lib.lint_paths(f["changed"])
    (rec / "lint-paths.txt").write_bytes(b"".join(os.fsencode(path) + b"\0"
                                                  for path in paths))
    for path in paths:
        candidate = fork / path
        lib.require(candidate.is_file() and not candidate.is_symlink(),
                    f"changed Python path is not a regular file: {path}")

    index = git("ls-files", "-s", "-z")
    tracked = f["tracked"] = {}

    def snapshot(stage, location=fork):
        try:
            if location == fork:
                actual = git("rev-parse", "--verify", "HEAD").decode().strip()
                lib.require(actual == sha, "fork HEAD changed")
                git("diff", "--quiet", "--no-ext-diff",
                    "--ignore-submodules=none", "HEAD", "--")
                changes = git("status", "--porcelain=v1",
                              "--untracked-files=no",
                              "--ignore-submodules=none")
                lib.require(not changes and
                            git("ls-files", "-s", "-z") == index,
                            "tracked index changed")
            tracked[stage] = lib.tracked_hash(head, location)
        except (OSError, ValueError) as exc:
            msg = f"tracked files differ after {stage}: {exc}"
            raise ValueError(msg) from exc
        with (rec / "tracked.txt").open("a") as stream:
            print(stage, tracked[stage], sep="\t", file=stream)

    snapshot("before")
    for name in ("database/settings.py", "database/influxdb/settings.py",
                 "django_gui/settings.py"):
        path = fork / name
        dist = fork / (name + ".dist")
        if dist.is_file() and not path.exists():
            shutil.copyfile(dist, path)
    python = str(rec / "venv/bin/python")
    lib.require(logged(["python3", "-m", "venv", str(rec / "venv")],
                       rec / "venv.log", fork, env) == 0, "venv setup failed")
    pins = ["flake8==7.5.0", "pytest-timeout==2.4.0"]
    f["install"] = logged([python, "-m", "pip", "install", "-e", ".[dev,mqtt]",
                           *pins], rec / "pip.log", fork, env)
    lib.require(f["install"] == 0, "dependency install failed (see pip.log)")
    snapshot("installed")
    freeze = subprocess.run([python, "-m", "pip", "freeze"], env=env, cwd=fork,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (rec / "pip-freeze.txt").write_bytes(freeze.stdout)
    with (rec / "pip.log").open("ab") as log:
        log.write(freeze.stderr)
    f["freeze"] = freeze.returncode
    lib.require(freeze.returncode == 0, "could not record pip freeze")
    f["pins"] = sorted(line for line in freeze.stdout.decode().splitlines()
                       if line.partition("==")[0].lower() in
                       ("flake8", "pytest-timeout"))
    snapshot("frozen")

    cmd = lib.pytest_command(str(rec))
    pytest_env = dict(env, PYTHONPATH=str(HERE),
                      ORV_COLLECTION=str(rec / "collection.json"))
    status = logged(cmd, rec / "pytest.log", fork, pytest_env)
    snapshot("pytest")
    pytest = f["pytest"] = {"argv": cmd, "status": status}
    pytest["junit"] = (rec / "pytest.xml").read_bytes().decode()
    pytest["modules"] = sorted(os.fsdecode(p) for p in head
                               if lib.pytest_module(os.fsdecode(p)))
    # Retain the original observation on refusal, even for invalid JSON.
    raw = (rec / "collection.json").read_bytes().decode()
    pytest["collection"] = raw
    collection = json.loads(raw, object_pairs_hook=unique_keys,
                            parse_float=invalid_number,
                            parse_constant=invalid_number)
    # Keep malformed, potentially unbounded JSON out of the sealed document.
    suite = dict(pytest, collection=collection)
    pytest_rows = lib.pytest_rows(suite, str(rec))
    f["pytest"] = suite
    (rec / "pytest.tsv").write_text(lib.tsv(pytest_rows))
    django_file = rec / "django.tsv"
    cmd = [python, "manage.py", "test", "test.django_gui", "--noinput",
           "--testrunner=orv_django_runner.Runner"]
    django_env = dict(env, PYTHONPATH=str(HERE), ORV_DJ_ROWS=str(django_file))
    status = logged(cmd, rec / "django.log", fork, django_env)
    snapshot("django")
    f["django"] = dict(status=status, tsv=django_file.read_bytes().decode())
    rows.extend(pytest_rows + lib.django_rows(f["django"]))

    export = rec / "lint-export"
    export.mkdir()
    with tempfile.TemporaryFile() as archive:
        cmd = ["git", "-C", str(fork), "archive", "--format=tar", sha]
        subprocess.run(cmd, env=env, stdout=archive, check=True)
        archive.seek(0)
        capture(["tar", "-xf", "-", "-C", str(export)], stdin=archive)
    snapshot("export_before", export)
    snapshot("before_lint")
    workdir = export
    if not paths:
        # flake8 defaults an empty positional list to ".". Run that exact
        # empty list in a new empty directory and require zero processed files.
        workdir = rec / "lint-empty"
        workdir.mkdir()
    f["lint"] = []
    with (rec / "flake8.log").open("wb") as log:
        for path in paths or [None]:
            cmd = lib.lint_command(str(rec), path)
            run = subprocess.run(cmd, env=env, cwd=workdir,
                                 capture_output=True)
            result = dict(argv=cmd, cwd=str(workdir), status=run.returncode)
            f["lint"].append(result)
            (rec / "flake8.out").write_bytes(run.stdout)
            log.write(run.stderr + run.stdout)
            lib.require(run.returncode == 0 and not run.stderr,
                        f"flake8 did not complete for {path} (see flake8.log)")
            result.update(parse_lint(run.stdout, path))
            row = lib.lint_result(result, str(rec), path)
            if row is not None:
                rows.append(row)
    snapshot("export_after", export)
    snapshot("after")
    rows.extend([("flake8::__COMPLETE__", "PASS"), (lib.END, "PASS")])


def publish(path, data):
    # Rename only a fully written, read-only artifact into its public name.
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        stream.write(data)
        os.fchmod(stream.fileno(), 0o444)
    os.replace(stream.name, path)


def main(args):
    if len(args) != 3:
        print("usage: gate-linux.sh <sha> <fork> <new receipt dir>",
              file=sys.stderr)
        return 2
    sha, fork, output = args
    rec = Path(output).resolve()
    try:
        rec.mkdir()
    except OSError as exc:
        print(f"could not create a new receipt directory: {exc}",
              file=sys.stderr)
        return 2
    facts = {"requested": sha, "directory": str(rec), "error": ""}
    rows = []
    try:
        collect(facts, fork, rec, rows)
    except (OSError, ValueError, TypeError, RecursionError, ParseError,
            subprocess.CalledProcessError) as exc:
        facts["error"] = str(exc) or type(exc).__name__
    candidate = rec / "rows.pending"
    publish(candidate, lib.tsv(rows).encode())
    # Capture the actual publication once. decide compares it to independently
    # reconstructed rows. The receipt hashes precisely these observed bytes.
    stored = candidate.read_bytes()
    try:
        facts["results"] = stored.decode()
    except UnicodeDecodeError as exc:
        facts["error"] = f"invalid results.tsv: {exc}"
    evidence = dict(facts=facts, sha256=lib.sha256(lib.canonical(facts)))
    payload = lib.canonical(evidence)
    publish(rec / "evidence.json", payload)
    verdict = lib.decide(evidence)
    if verdict.label == "REFUSED":
        if verdict.reason != "missing __END__ as last row":
            publish(rec / "REFUSED.txt", (verdict.reason + "\n").encode())
        if stored != lib.tsv(rows).encode() or (lib.END, "PASS") in rows:
            # Preserve complete stage rows for diagnostics, without a terminal
            # marker that could be mistaken for a complete receipt.
            stored = lib.tsv(row for row in rows if row[0] != lib.END).encode()
            publish(candidate, stored)
    os.replace(candidate, rec / "results.tsv")
    receipt = dict(sha=sha,
                   host=os.environ.get("RUNNER_NAME", socket.gethostname()),
                   utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   verdict=verdict.label, reason=verdict.reason,
                   counts=verdict.counts,
                   unexcused_failures=verdict.failures,
                   results_sha256=lib.sha256(stored),
                   evidence_sha256=lib.sha256(payload))
    publish(rec / "receipt.json", lib.canonical(receipt))
    print(f"VERDICT {verdict.label} sha={sha[:12]} {verdict.reason}")
    return {"GREEN": 0, "RED": 1, "REFUSED": 2}[verdict.label]


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except OSError as exc:
        print(f"could not publish gate evidence: {exc}", file=sys.stderr)
        sys.exit(2)
