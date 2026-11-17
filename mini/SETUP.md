# Mac Mini setup for the OpenRVDAS gate

One-time. Everything lives in `~/OpenRVDAS-Work/` and touches nothing of
Kalon's. Eugene's yes to this file covers exactly these steps: two git clones,
one Python venv, and pip packages installed into that venv. No launchd, no
services, no Homebrew changes, no system settings.

Run each block in a shell on the Mini. From the MacBook, open one first:

```
ssh kalon-mini
```

## 0. Right machine, and read-only inventory

```
[ "$(scutil --get LocalHostName)" = "EugeneMacMini" ] && echo RIGHT MACHINE || echo "WRONG MACHINE: stop"
```

```
ls /opt/homebrew/bin/python3.12 && /opt/homebrew/bin/python3.12 -V
```

```
df -h ~ | tail -1
```

```
ls -d ~/KalonWork/lock-w* 2>/dev/null; pgrep -fl mini-gate-suite.sh; echo "(empty above means Kalon is idle)"
```

If `python3.12` is missing, stop and tell the lead. Installing it with
Homebrew is a separate yes.

## 1. Folders and clones

```
mkdir -p ~/OpenRVDAS-Work/receipts ~/OpenRVDAS-Work/wt
```

```
git clone https://github.com/eugenevivino/openrvdas ~/OpenRVDAS-Work/openrvdas
```

```
git clone https://github.com/eugenevivino/openrvdas-desk ~/OpenRVDAS-Work/openrvdas-desk
```

## 2. Python 3.12 venv and dependencies (the deps step)

```
/opt/homebrew/bin/python3.12 -m venv ~/OpenRVDAS-Work/venv-3.12
```

```
~/OpenRVDAS-Work/venv-3.12/bin/python -m pip install -q --upgrade pip "setuptools>=77" wheel
```

```
cd ~/OpenRVDAS-Work/openrvdas && git checkout -q origin/dev && ~/OpenRVDAS-Work/venv-3.12/bin/python -m pip install -q -e ".[dev,mqtt]" flake8 pytest-timeout
```

```
shasum -a 256 ~/OpenRVDAS-Work/openrvdas/pyproject.toml | awk '{print $1}' > ~/OpenRVDAS-Work/venv-3.12/.orv-deps-stamp
```

```
cd ~/OpenRVDAS-Work/openrvdas && git checkout -q master
```

When upstream changes `pyproject.toml`, the gate refuses with "pyproject.toml
changed". Rerun the three commands of this step from `git checkout -q
origin/dev` on, using the commit the gate refused on.

## 3. Prove it

```
python3 -I ~/OpenRVDAS-Work/openrvdas-desk/gate/tests/test_gate.py
```

```
bash ~/OpenRVDAS-Work/openrvdas-desk/gate/gate.sh "$(git -C ~/OpenRVDAS-Work/openrvdas rev-parse origin/dev)"
```

Expected today: verdict RED with one row,
`django::test.django_gui.test_django_server_api.TestDjangoServerAPI.test_basic`
(seen in the cloud dry run). If it is RED on that row only, the gate works.
Then decide whether to list that row in `gate/expected-failures.txt` while an
upstream issue is filed (your call, rule 10).

## 4. From the MacBook afterwards

```
bash ~/openrvdas-desk/gate/remote.sh origin/dev
```

## Undo

Everything is in one folder. Removing it is a delete, so it needs your yes:

```
rm -rf ~/OpenRVDAS-Work
```
