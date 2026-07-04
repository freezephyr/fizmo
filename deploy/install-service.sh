#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${FIZMO_APP_DIR:-$HOME/fizmo}"
SERVICE_NAME="${FIZMO_SERVICE_NAME:-fizmo}"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
TEMPLATE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$APP_DIR" ]; then
  echo "App directory does not exist: $APP_DIR" >&2
  exit 1
fi

sudo install -m 0644 "$TEMPLATE_DIR/fizmo.service" "$SERVICE_FILE"
sudo sed -i "s|__FIZMO_APP_DIR__|$APP_DIR|g" "$SERVICE_FILE"
sudo sed -i "s|__FIZMO_USER__|$(id -un)|g" "$SERVICE_FILE"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"
sudo systemctl status "$SERVICE_NAME" --no-pager
