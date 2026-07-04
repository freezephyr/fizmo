# ADR 0004: Configuration Policy

## Status

Accepted

## Context

Fizmo hardware details will change during bring-up: servo channels, direction, logical zero, IMU mounting orientation, leg geometry, logging limits, display details, and wake word.

## Decision

Keep hardware mapping, calibration, and user-facing runtime settings in config files. Code may provide defaults for development, but robot-specific values should be loaded from config.

## Consequences

Hardware changes should not require code edits. Configuration review becomes part of bring-up and deployment.
