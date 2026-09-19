#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8000}"

if [[ -x "${ROOT_DIR}/.venv/bin/python" ]]; then
  PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"
else
  PYTHON_BIN="${PYTHON_BIN:-python3}"
fi

if [[ ! -d "${ROOT_DIR}/frontend/node_modules" ]]; then
  echo "Frontend dependencies are not installed. Run: npm --prefix frontend install" >&2
  exit 1
fi

cleanup() {
  trap - INT TERM EXIT
  [[ -n "${BACKEND_PID:-}" ]] && kill "${BACKEND_PID}" 2>/dev/null || true
  [[ -n "${FRONTEND_PID:-}" ]] && kill "${FRONTEND_PID}" 2>/dev/null || true
  wait 2>/dev/null || true
}

trap cleanup INT TERM EXIT

echo "Starting backend at http://${BACKEND_HOST}:${BACKEND_PORT}"
(
  cd "${ROOT_DIR}/backend"
  exec "${PYTHON_BIN}" manage.py runserver "${BACKEND_HOST}:${BACKEND_PORT}"
) &
BACKEND_PID=$!

echo "Starting frontend at http://localhost:5173"
(
  cd "${ROOT_DIR}"
  exec npm --prefix frontend run dev
) &
FRONTEND_PID=$!

wait -n "${BACKEND_PID}" "${FRONTEND_PID}"
EXIT_CODE=$?

echo "A development server exited; stopping the remaining server."
exit "${EXIT_CODE}"
