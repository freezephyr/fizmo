# ADR 0005: CI/CD Pipeline

## Status

Accepted

## Context

Fizmo will run on Raspberry Pi hardware, but most development happens on a laptop. The project needs automated checks and a repeatable way to deploy a known-good version to the Pi.

## Decision

Use GitHub Actions for CI and manual CD.

CI runs on push and pull request to `main` using standard GitHub-hosted Linux runners. It installs the package, runs unit tests, and executes mock hardware smoke checks.

CD is manually triggered. The workflow connects to the Raspberry Pi over SSH, then the Pi pulls the selected Git ref from GitHub, installs the package locally, runs smoke checks, and restarts `fizmo.service` if installed.

The Raspberry Pi deploys a known commit SHA from GitHub rather than receiving copied files from the workflow workspace.

## Consequences

CI can run without robot hardware. Deployment is reproducible and rollback-friendly. Secrets stay in GitHub Actions repository secrets. Real hardware checks and automatic deployment can be added later after the Pi service and safety model are mature.
