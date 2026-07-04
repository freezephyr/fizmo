# Fizmo CI/CD

Fizmo uses GitHub Actions for continuous integration and manual Raspberry Pi deployment.

## CI

CI runs on every push and pull request to `main`.

It performs:

- Python 3.12 setup.
- Editable package install.
- Unit tests.
- Mock hardware smoke checks.

The mock checks avoid touching real robot hardware.

## CD

Deployment is manual through the `Deploy to Raspberry Pi` GitHub Actions workflow.

The deploy workflow:

1. Runs CI checks again.
2. Connects to the Raspberry Pi over SSH.
3. Clones the repo if needed.
4. Fetches GitHub.
5. Checks out the exact selected ref/SHA.
6. Creates or updates `.venv`.
7. Installs Fizmo with Pi extras.
8. Runs tests and mock conversation smoke checks.
9. Restarts `fizmo.service` if it has been installed.

## GitHub Secrets

Configure these repository secrets in GitHub:

- `FIZMO_PI_HOST`: Raspberry Pi hostname or IP address.
- `FIZMO_PI_USER`: SSH user on the Pi.
- `FIZMO_PI_SSH_KEY`: Private SSH key that can log in as `FIZMO_PI_USER`.
- `FIZMO_PI_PORT`: SSH port. Optional; defaults to `22`.
- `FIZMO_APP_DIR`: App checkout path on the Pi, such as `/home/pi/fizmo`.

## Raspberry Pi Setup

Install base tools on the Pi:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv alsa-utils
```

The deploy workflow can clone and update the app directory by itself.

To install the systemd service after the first deploy:

```bash
cd /home/pi/fizmo
bash deploy/install-service.sh
```

The initial service command runs a harmless idle loop. Replace the service command when a real long-running runtime is ready.

## Deployment Model

The Pi pulls code from GitHub by commit SHA. GitHub Actions does not copy random local files to the Pi.

This keeps deploys reproducible and makes rollback straightforward:

```bash
cd /home/pi/fizmo
git fetch origin
git checkout <known-good-sha>
sudo systemctl restart fizmo
```
