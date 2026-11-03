#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PY="$PWD/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo 'Missing virtual environment; run make setup first.' >&2
  exit 1
fi
if [[ ! -f frontend/.next/BUILD_ID ]]; then
  (cd frontend && npm install && npm run build)
fi
"$PY" -m benchmarks.generate_cases
SOURCE_DB="${NANO_DB:-$PWD/runtime/nanoforensics.db}"
RUN_DIR=$(mktemp -d "$PWD/runtime/e2e-XXXXXX")
export NANO_E2E_DIR="$RUN_DIR"
export NANO_DB="$RUN_DIR/test.db"
export NANO_BACKEND_URL=http://127.0.0.1:8000
# Keep study jobs/results isolated from the published preregistered dataset.
DEMONSTRATION_SOURCE_DB="${NANO_DEMONSTRATION_DB:-$PWD/runtime/demonstration/v3/study.db}"
if [[ -f "$DEMONSTRATION_SOURCE_DB" ]]; then
  "$PY" - "$DEMONSTRATION_SOURCE_DB" "$RUN_DIR/demonstration.db" <<'PYCLONE'
import sqlite3,sys
with sqlite3.connect(sys.argv[1]) as source,sqlite3.connect(sys.argv[2]) as target:
    source.backup(target)
    target.execute('DELETE FROM jobs')
    target.execute('DELETE FROM states')
PYCLONE
fi
export NANO_DEMONSTRATION_DB="$RUN_DIR/demonstration.db"
export NANO_LIVE_MUSE_DB="$RUN_DIR/live-muse.db"
export NANO_E2E_LIVE=1
export META_MUSE_API_KEY=""
export NANO_ADMIN_TOKEN=""
"$PY" - "$SOURCE_DB" "$NANO_DB" <<'PY'
import sqlite3,sys
with sqlite3.connect(sys.argv[1]) as source,sqlite3.connect(sys.argv[2]) as target:
    source.backup(target)
    target.execute('DELETE FROM jobs')
    target.execute('DELETE FROM states')
PY
cleanup() {
  "$PY" scripts/e2e_servers.py stop "$RUN_DIR" || true
}
trap cleanup EXIT INT TERM
"$PY" - <<'PY'
import socket
for port in [8000,3000]:
    with socket.socket() as sock:
        if sock.connect_ex(('127.0.0.1',port))==0:
            raise SystemExit(f'Port {port} is already in use; stop the existing local preview before running the managed E2E gate.')
PY
"$PY" scripts/e2e_servers.py start "$RUN_DIR"
"$PY" - <<'PY'
import httpx,time
for url in ['http://127.0.0.1:8000/api/health','http://127.0.0.1:3000']:
    deadline=time.monotonic()+60
    while time.monotonic()<deadline:
        try:
            if httpx.get(url,timeout=2).status_code==200:break
        except httpx.HTTPError:pass
        time.sleep(.25)
    else:raise SystemExit(f'Server readiness failed: {url}')
print('Both real servers are ready; running live E2E acceptance tests.')
PY
.venv/bin/pytest tests/test_e2e_fullstack.py -v -s | tee "$RUN_DIR/pytest.log"
cp "$RUN_DIR/pytest.log" docs/E2E_LAST_RUN.txt
echo "E2E process logs and isolated SQLite database: $RUN_DIR"
