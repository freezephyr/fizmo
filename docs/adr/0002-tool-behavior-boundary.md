# ADR 0002: Tool and Behavior Boundary

## Status

Accepted

## Context

Each robot skill, such as `stand()`, `sit()`, `lie_down()`, `walk()`, `run()`, `nod()`, or `tilt_head()`, ultimately changes actuator state. Fizmo also needs to add learned behavior over time without changing the agent contract.

## Decision

Expose robot skills as tools. Each tool delegates motion planning to a behavior model with the same stable purpose. Start with deterministic behavior models and replace them with trained models only after enough real or simulated data exists.

## Consequences

The agent calls high-level tools instead of servo-level actions. Model training can proceed per behavior, and tool-level success can be measured through state estimation rather than through raw actuator commands.
