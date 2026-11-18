#!/usr/bin/env bash
# Fork code and collector share a runner identity. Receipts cover our fork only.
set -eu
here=$(cd -- "$(dirname -- "$0")" && pwd)
exec python3 -I "$here/gate_linux.py" "$@"
