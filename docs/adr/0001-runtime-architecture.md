# ADR 0001: Runtime Architecture

## Status

Accepted

## Context

Fizmo is a Raspberry Pi robot with four servo-driven Technic legs, an MPU6050 IMU, camera, microphone, speaker, and display. The robot needs to accept user intent, choose an action, actuate hardware, observe the resulting state, and report success or failure.

## Decision

Use a layered runtime:

- Agent chooses intent and calls tools.
- Tools own closed-loop behaviors.
- Behavior models produce actuator plans for a specific tool.
- Hardware adapters isolate real devices from mock/test implementations.
- State estimation consumes IMU, servo, camera, and audio state and reports robot state.
- Config owns hardware mapping, calibration, and user-facing settings such as wake word.
- Conversation flows from microphone capture to speech-to-text, text model response, and display output.

The agent does not command servos directly.

## Consequences

Tool names can stay stable while behavior implementations evolve from deterministic logic to learned models. The robot remains testable on a laptop through mock hardware, and Pi-specific device access stays behind adapters.
