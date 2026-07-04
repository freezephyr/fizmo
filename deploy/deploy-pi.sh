#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${FIZMO_APP_DIR:-$HOME/fizmo}"
DEPLOY_REF="${FIZMO_DEPLOY_REF:?FIZMO_DEPLOY_REF is required}"
REPO_URL="${FIZMO_REPO_URL:-https://github.com/freezephyr/fizmo.git}"
SERVICE_NAME="${FIZMO_SERVICE_NAME:-fizmo}"

if ! command -v git >/dev/null 2>&1; then
  echo "git is required on the Raspberry Pi" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required on the Raspberry Pi" >&2
  exit 1
fi

if [ ! -d "$APP_DIR/.git" ]; then
  mkdir -p "$(dirname "$APP_DIR")"
  git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"
git fetch origin
git checkout --detach "$DEPLOY_REF"

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[pi]"

python -m unittest discover -s tests
python -m fizmo.cli.converse --duration 0.1 --mock-rms 0.02

if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files "${SERVICE_NAME}.service" --no-legend | grep -q "^${SERVICE_NAME}.service"; then
  sudo systemctl restart "$SERVICE_NAME"
  sudo systemctl is-active "$SERVICE_NAME"
else
  echo "systemd service ${SERVICE_NAME}.service is not installed; deploy completed without restart"
fi
