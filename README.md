# dome_mission

Mission-sequencing layer for the DOME robot. Owns `/intent` and drives a pure
mission FSM that composes dome_nav primitives (`ExploreArea` action) and Nav2
`NavigateToPose` — keeping dome_nav free of mission and semantic knowledge (F35).

## Architecture

Pure/ROS split (dome_nav L0/L1 convention):

- **`mission_fsm.py`** — pure, ROS-free FSM. States `IDLE / EXPLORING /
  LOCATING / GOING_TO_TARGET`; intent + behavior-completion driven; emits
  primitive `Command`s.

- **`intent_parser.py`** — pure `/intent` JSON → mission `Intent` mapping.

- **`mission_node.py`** — thin ROS seam: subscribes `/intent`, drives the FSM,
  executes commands (ExploreArea / NavigateToPose action clients).

## Build

```bash
colcon build --packages-select dome_nav_msgs dome_mission
```

## Test

```bash
/usr/bin/python3 -m pytest test/
```

## Run

```bash
ros2 run dome_mission mission_node
```

## License

MIT — see [LICENSE](LICENSE)
