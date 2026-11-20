#!/usr/bin/env python3
"""Executable, deliberately non-production fixture for Relay's staged demo.

Every stage performs assertions on source or behavior.  The review stage is a
fixture structural check, not an AI review or a real module qualification.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import sys
import time


FIXTURES = {
    "math": {
        "add": "def add(a, b):\n    return a + b\n",
        "multiply": "def multiply(a, b):\n    return a * b\n",
    },
    "display": {
        "render": "def render(value):\n    return f'[{value}]'\n",
        "unwrap": "def unwrap(value):\n    if not (value.startswith('[') and value.endswith(']')):\n        raise ValueError('invalid display value')\n    return value[1:-1]\n",
    },
}


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt_data(result: dict) -> dict:
    """Unwrap both the interface's worker result and a stored receipt."""
    if not isinstance(result, dict):
        raise ValueError("dependency result must be an object")
    for key in ("receipt", "adapter_receipt", "adapter_result"):
        if isinstance(result.get(key), dict):
            return receipt_data(result[key])
    if isinstance(result.get("result"), dict) and "data" not in result:
        return receipt_data(result["result"])
    data = result.get("data")
    if not isinstance(data, dict):
        raise ValueError("dependency is missing adapter receipt data")
    if data.get("fixture_only") is not True:
        raise ValueError("the demonstration accepts only its own fixture artifacts")
    return data


def dependencies(packet: dict) -> list[dict]:
    values = packet.get("dependencies", {})
    if isinstance(values, dict):
        values = list(values.values())
    if not isinstance(values, list):
        raise ValueError("dependencies must be a mapping or list")
    return [receipt_data(value) for value in values]


def canonical_module(module: str) -> str:
    return "\n".join(FIXTURES[module].values())


def read_module(data: dict, expected_module: str | None = None) -> tuple[Path, dict]:
    module = data.get("module")
    if module not in FIXTURES or (expected_module is not None and module != expected_module):
        raise ValueError("wrong fixture module in dependency")
    path = Path(data["artifact"])
    source = path.read_text(encoding="utf-8")
    if source != canonical_module(module):
        raise ValueError("assembled source differs from the canonical fixture pieces")
    if data.get("artifact_sha256") != sha256(path):
        raise ValueError("artifact hash does not match dependency evidence")
    if set(data.get("pieces", [])) != set(FIXTURES[module]):
        raise ValueError("module has not assembled all of its required pieces")
    namespace: dict = {}
    # Source is checked byte-for-byte above against this file's four literals.
    exec(compile(source, str(path), "exec"), namespace)
    return path, namespace


def run_checks(module: str, namespace: dict, extra: list | None = None) -> int:
    if module == "math":
        cases = [("add", [2, 3], 5), ("add", [-4, 4], 0),
                 ("multiply", [6, 7], 42), ("multiply", [8, 0], 0)]
    else:
        cases = [("render", [42], "[42]"), ("render", [""], "[]"),
                 ("unwrap", ["[hello]"], "hello"), ("unwrap", ["[]"], "")]
    for item in extra or []:
        cases.append((item["function"], item["args"], item["expected"]))
    for function, arguments, expected in cases:
        if function not in FIXTURES[module]:
            raise ValueError("a check names a function outside the fixture contract")
        actual = namespace[function](*arguments)
        if actual != expected:
            raise AssertionError(f"{function}{tuple(arguments)!r}: {actual!r} != {expected!r}")
    if module == "display":
        try:
            namespace["unwrap"]("unframed")
        except ValueError:
            pass
        else:
            raise AssertionError("unwrap must reject unframed input")
        return len(cases) + 1
    return len(cases)


def module_data(path: Path, module: str, pieces: list[str], **extra) -> dict:
    return {
        "artifact": str(path.resolve()),
        "artifact_sha256": sha256(path),
        "module": module,
        "pieces": pieces,
        "fixture_only": True,
        **extra,
    }


def perform(stage: str, packet: dict, directory: Path) -> tuple[dict, list[str], str]:
    inputs = packet["spec"].get("inputs", {})
    delay = float(inputs.get("delay_s", 0))
    if not 0 <= delay <= 5:
        raise ValueError("fixture delay must be between zero and five seconds")
    if delay:
        time.sleep(delay)
    module = inputs.get("module", packet["spec"].get("module"))
    if stage != "batch" and module not in FIXTURES:
        raise ValueError("module must be the fixture 'math' or 'display'")

    if stage == "piece":
        piece = inputs["piece"]
        source = FIXTURES[module][piece]
        if "source" in inputs and inputs["source"] != source:
            raise ValueError("provided source must match the canonical demonstration piece")
        path = directory / f"{module}_{piece}.py"
        path.write_text(source, encoding="utf-8")
        compile(source, str(path), "exec")
        return module_data(path, module, [piece]), [str(path)], f"Built fixture piece {module}/{piece}"

    records = dependencies(packet)
    if stage == "assemble":
        collected = {}
        for data in records:
            if data.get("module") != module or len(data.get("pieces", [])) != 1:
                raise ValueError("assembly requires one matching piece per dependency")
            piece = data["pieces"][0]
            if piece in collected:
                raise ValueError("duplicate piece in module assembly")
            path = Path(data["artifact"])
            source = path.read_text(encoding="utf-8")
            if source != FIXTURES[module].get(piece) or sha256(path) != data.get("artifact_sha256"):
                raise ValueError("piece source or evidence hash has changed")
            collected[piece] = source
        if set(collected) != set(FIXTURES[module]):
            raise ValueError("assembly is missing required module pieces")
        path = directory / f"{module}.py"
        path.write_text("\n".join(collected[piece] for piece in FIXTURES[module]), encoding="utf-8")
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
        return module_data(path, module, list(FIXTURES[module])), [str(path)], f"Assembled all pieces of fixture module {module}"

    if stage in ("test", "review"):
        matching = [record for record in records if record.get("module") == module]
        if stage == "test" and len(matching) != 1:
            raise ValueError("test requires exactly one assembled module dependency")
        if stage == "review":
            if not matching:
                raise ValueError("review requires the assembled module and its test evidence")
            identities = {(str(Path(record["artifact"]).resolve()), record.get("artifact_sha256"))
                          for record in matching}
            if len(identities) != 1:
                raise ValueError("review evidence does not refer to the same artifact and hash")
            if not any(record.get("stage") == "test" and record.get("checks_passed", 0) > 0
                       for record in matching):
                raise ValueError("review requires successful executable test evidence")
            for record in matching:
                read_module(record, module)
        path, namespace = read_module(matching[0], module)
        checks = run_checks(module, namespace, inputs.get("checks"))
        report = directory / f"{stage}-report.json"
        label = "fixture structural review; not AI or production acceptance" if stage == "review" else "fixture executable tests"
        if stage == "review":
            tree = ast.parse(path.read_text(encoding="utf-8"))
            functions = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
            if set(functions) != set(FIXTURES[module]) or len(functions) != len(tree.body):
                raise AssertionError("structural fixture contract failed")
        atomic_json(report, {"module": module, "stage": stage, "checks_passed": checks,
                             "label": label, "fixture_only": True, "artifact_sha256": sha256(path)})
        data = module_data(path, module, list(FIXTURES[module]), checks_passed=checks, stage=stage,
                           review_kind="fixture_only" if stage == "review" else None)
        return data, [str(path), str(report)], f"Passed {label} for {module}"

    if stage == "batch":
        modules = {}
        evidence = []
        batch_directory = directory / "combined-candidate"
        batch_directory.mkdir(exist_ok=True)
        checks = 0
        for data in records:
            name = data.get("module")
            if name in modules:
                raise ValueError("duplicate module in integration batch")
            source, namespace = read_module(data)
            if data.get("review_kind") != "fixture_only":
                raise ValueError("batch requires the explicit fixture-review receipt")
            destination = batch_directory / f"{name}.py"
            destination.write_bytes(source.read_bytes())
            copied_data = module_data(destination, name, list(FIXTURES[name]))
            _, copied_namespace = read_module(copied_data)
            checks += run_checks(name, copied_namespace)
            modules[name] = copied_namespace
            evidence.append(str(destination))
        if not modules:
            raise ValueError("batch must contain at least one ready module")
        cross_module = "math" in modules and "display" in modules
        if cross_module:
            computed = modules["math"]["add"](modules["math"]["multiply"](6, 7), 1)
            rendered = modules["display"]["render"](computed)
            assert rendered == "[43]", "integrated output mismatch"
            assert int(modules["display"]["unwrap"](rendered)) == 43, "integrated round trip mismatch"
            checks += 2
        report = directory / "batch-report.json"
        atomic_json(report, {"modules": sorted(modules), "module_count": len(modules),
                             "batch_invocations": 1, "checks_passed": checks,
                             "cross_module_check": cross_module, "fixture_only": True,
                             "published": False})
        evidence.append(str(report))
        return {"artifact": str(report), "artifact_sha256": sha256(report), "module": None,
                "modules": sorted(modules), "pieces": [], "fixture_only": True,
                "batch_invocations": 1, "cross_module_check": cross_module,
                "checks_passed": checks, "published": False}, evidence, f"Passed one fixture integration batch containing {len(modules)} module(s)"
    raise ValueError(f"unknown fixture stage: {stage}")


def main() -> int:
    input_path = Path(os.environ["RELAY_INPUT_FILE"])
    output_path = Path(os.environ["RELAY_RESULT_FILE"])
    directory = Path(os.environ.get("RELAY_ATTEMPT_DIR", str(output_path.parent))).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    packet = json.loads(input_path.read_text(encoding="utf-8"))
    started = time.monotonic_ns()
    try:
        data, evidence, summary = perform(sys.argv[1], packet, directory)
        data["duration_ms"] = (time.monotonic_ns() - started) / 1_000_000
        outcome = "pass"
        code = 0
    except Exception as error:
        failure = directory / "failure.txt"
        failure.write_text(f"{type(error).__name__}: {error}\n", encoding="utf-8")
        data, evidence = {"fixture_only": True}, [str(failure)]
        summary, outcome, code = f"Fixture failed: {error}", "fail", 1
    atomic_json(output_path, {"schema": 1, "outcome": outcome,
                              "input_digest": packet["input_digest"], "summary": summary,
                              "evidence": evidence, "data": data})
    print(summary)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
