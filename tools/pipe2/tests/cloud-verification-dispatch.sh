#!/bin/bash
set -eu
cd "$(dirname "$0")/../../.."
export TMPDIR=${DS_PIPE2_TEST_TMPDIR:-/private/tmp/deepsignal/cloud-verification-dispatch/tmp}
export PYTHONDONTWRITEBYTECODE=1
exec /opt/homebrew/bin/python3.12 tools/pipe2/tests/cloud-verification-fixture.py "$@"
