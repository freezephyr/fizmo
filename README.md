# Fizmo

Fizmo is a Raspberry Pi 5 robot with four servo-driven Technic legs, an MPU6050 IMU, a Raspberry Pi 5 MP camera, microphone, speaker, and a small status display. The wake word is a config entry, currently set in [config/robot.ini](config/robot.ini).

## High-Level Design

The agent chooses an intent. Tools own closed-loop behaviors. The state model reads the robot body and reports whether the requested state was reached.

```text
actor command + robot state
  -> agent chooses tool
  -> tool drives behavior
  -> actuators change hardware
  -> IMU/camera/audio update state
  -> tool returns success/failure
```

Each body tool delegates to a behavior model. The current behavior models are deterministic placeholders; later, each one can be replaced with a learned model without changing the agent-facing tool name.

```text
stand()     -> StandBehaviorModel
sit()       -> SitBehaviorModel
lie_down()  -> LieDownBehaviorModel
walk()      -> WalkBehaviorModel
run()       -> RunBehaviorModel
nod()       -> NodBehaviorModel
tilt_head() -> TiltHeadBehaviorModel
```

The first stand model targets all four legs at a logical `10 deg` stance, where `0 deg` means the leg is perpendicular to the ground. With the current 7-hole Technic leg estimate of `56 mm`, the target vertical body support height is:

```text
height = leg_length * cos(10 deg)
height = 56 mm * cos(10 deg)
height ~= 55.1 mm
```

The servo angle is only the actuator instruction. Success should be judged by body state: stable IMU roll/pitch plus the geometry-derived target height. The MPU6050 can confirm tilt/stability, but it cannot directly measure static absolute height without another reference sensor.

Logical leg angles are mapped to physical servo angles per leg in [config/robot.ini](config/robot.ini):

```ini
[servo.front_left]
logical_zero_deg = 0.0
logical_scale = 1.0
reversed = false
```

This lets each mounted servo define where logical `0 deg` actually is after calibration.

## Initial Tool Families

Body tools:

- `find_state()`
- `halt()`
- `stand()`
- `sit()`
- `lie_down()`
- `walk()`
- `run()`
- `nod()`
- `tilt_head(direction)`

Interaction tools:

- `show_face(expression, text=None)`
- `speak(text)`

Future tools:

- `look()`
- `listen()`
- `move_backward()`
- `turn_left()`
- `turn_right()`

## Hardware Notes

Servos may use a separate LiPo battery for power, but the Raspberry Pi ground and servo battery ground must be connected together so the control signal has a common reference.

Planned servo signal path:

```text
Raspberry Pi 5
  -> I2C
  -> PCA9685 servo driver
  -> channels 0-3
  -> four leg servos
```

Servo power is external and will be validated on the bench before walking. The software assumes separate servo power, common ground with the Pi, and PCA9685-generated PWM.

The current software package starts with mock hardware adapters. Real Raspberry Pi adapters should be added behind the same interfaces once the servo controller, microphone, and camera details are finalized.

## Servo Calibration

Tunable hardware values live in [config/robot.ini](config/robot.ini). Update that file as parts, channels, angles, or dimensions change.

The calibration CLI defaults to mock hardware:

```powershell
python -m fizmo.cli.calibrate_servos --center-all
python -m fizmo.cli.calibrate_servos --servo front_left --angle 90
```

Tool calls can also be smoke-tested with mock hardware:

```powershell
python -m fizmo.cli.run_tool stand
python -m fizmo.cli.run_tool walk --steps 2
python -m fizmo.cli.run_tool tilt_head --direction left
```

## IMU State

The MPU6050 path is split into raw samples and filtered state:

```text
MPU6050 raw accel/gyro
  -> ImuStreamFilter
  -> roll/pitch/yaw_rate
  -> StateEstimator
  -> RobotState
```

Mock IMU reads:

```powershell
python -m fizmo.cli.read_imu --samples 3
python -m fizmo.cli.read_imu --mock-roll 20 --mock-pitch 5 --samples 1
```

On the Raspberry Pi, after enabling I2C and installing `smbus2`:

```bash
python -m fizmo.cli.read_imu --real
```

## Behavior Logs

Behavior logs are JSONL files under the configured log directory. Retention is controlled by [config/robot.ini](config/robot.ini):

```ini
[logging]
enabled = true
directory = logs/behavior
max_files = 20
max_total_mb = 250
```

Run a tool and log its result:

```powershell
python -m fizmo.cli.run_tool stand --log
```

Manage logs:

```powershell
python -m fizmo.cli.logs list
python -m fizmo.cli.logs prune
python -m fizmo.cli.logs clear --confirm
```

On the Raspberry Pi, after installing the PCA9685 dependencies and wiring the board:

```bash
python -m fizmo.cli.calibrate_servos --real --servo front_left --angle 90
```

## Open Decisions

- Exact servo channel mapping and direction for each leg.
- Microphone hardware.
- Camera type: Raspberry Pi 5 MP camera.
- Whether `tilt_head()` remains a body gesture or gets a dedicated head actuator later.
