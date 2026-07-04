# ADR 0003: Repository Structure

## Status

Accepted

## Context

The workspace contains both current Fizmo runtime code and earlier prototype/simulation files. The public repository should present a clean project while preserving useful experiments.

## Decision

Use this structure:

- `fizmo/` for production runtime package code.
- `config/` for robot configuration and calibration values.
- `docs/adr/` for architectural decision records.
- `experiments/` for prototype, ML, and simulation work that is not production runtime.
- `scripts/` for operational helper scripts that should not be imported by the runtime.
- `tests/` for automated tests.

## Consequences

Public repo contents stay understandable. Experiments can continue without becoming accidental production dependencies.
