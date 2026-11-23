# dome_mission — Notes

Semi-permanent project notes. Durable facts, not session narration.

## Origin

Extracted from dome_nav per **F03** (dome_nav's F35; mission-sequencing
layer). The extraction is tracked in dome_nav's
`04-tasks/notdone/TF35-mission-layer.md`, interleaved
with dome_nav's F33 (semantic exploration) Phase A.

Motivation: dome_nav had accreted mission/label logic (`nav_manager`,
`/intent` handling in `explorer_manager_node`). F03 pulls that up into a neutral
layer so dome_nav is primitives-only and never depends on `dome_semantic_msgs`.

## Role (F05)

dome_mission is **the brain**: the only node meant to consume `/intent`, and
the sole owner of what the robot is doing now. dome_control is the operator
surface, dome_semantic is the world model, and Nav2/dome_nav are the motion
primitives. The full role table is in `process/02-doc/spec.md`.

Until F08 lands, `/intent` is still split by name (dome_control F19):
dome_control's `behavior_manager_node` handles `stop`, turns, `get_status`,
`describe_scene` and `count_objects`. Its `stop` is a motor halt that doesn't
cancel dome_mission's goals.

## Layering

```
/intent ──► dome_mission ──► ExploreArea ──────────► dome_nav (explorer)
                 │
                 ├──► NavigateToPose ──────────────► Nav2   (direct, no dome_nav hop)
                 ├──► Spin / DriveOnHeading (F08) ─► Nav2 behavior server
                 └──► /mission/state, /announcement (F08)
/semantic/targets (SemanticTargetArray) ──► local copy ──► label → pose, filters
```

## Key decisions

- **One brain** (F05). The operator surface publishes intents and never
  handles them.
- **Subscribe to the semantic map; don't query it** (F05). The array is small.
  `SemanticTarget` carries `last_seen`, so "was it seen again?" checks are
  local. Add a service only when the array can't answer.
- **Turns and small spins use Nav2's behavior server** (F05). `spin` and
  `drive_on_heading` are already in every dome_nav Nav2 params file, so no new
  primitive is needed.
- **Behaviors are plain sequential code** (F05), not new FSM states per
  behavior and not a BT framework. *Hazard*: rclpy needs a worker thread per
  behavior, or async callbacks on a multi-threaded executor.
- **Transport = ROS actions** (TF03 T01). They are long-running, cancellable,
  and give feedback and a result.
- **drive-to-pose talks to Nav2 directly.** dome_mission holds the semantic
  map, so routing the pose back through dome_nav would be a pointless hop.
- **Boundary**: per-goal abort (timeouts, stuck, blacklist) stays in dome_nav's
  explorer watchdog. dome_mission owns only mission-level start/stop/preempt
  and the terminal `ExploreArea` outcome.

## Package relationships

- **dome_nav_msgs** (ament_cmake) — `ExploreArea.action`. Separate interface
  package because dome_nav is ament_python and can't host rosidl interfaces.
- **dome_semantic_msgs** (ament_cmake) — `SemanticTarget` / `SemanticTargetArray`.
- dome_mission is ament_python, depends on both.

## Architecture essentials

- **Pure/ROS split** (dome_nav L0/L1): `mission_fsm.py`, `intent_parser.py` and
  `label_resolver.py` are pure; `mission_node.py` is the thin ROS seam.
- FSM commands (`START_EXPLORE / CANCEL_EXPLORE / DRIVE_TO_TARGET /
  CANCEL_DRIVE`) are executed by the node's action clients: `ExploreArea` for
  explore, Nav2 `NavigateToPose` for drive-to-target.
- `mission_node` publishes FSM state on `/mission/state` (transient-local) for
  `dome_control`.
- The FSM (`mission_fsm.py`) covers explore and go-to only. Later behaviors are
  sequential code (see **Key decisions**).

## Task tracking

- The extraction's authority was dome_nav's `TF35-mission-layer.md`, now
  relocated here as `process/04-tasks/done/TF03-mission-layer.md`. This
  package's own `process/03-features/` and `process/04-tasks/` cover
  dome_mission-native work.

## Tooling

- `ruff` isn't preinstalled: `python3 -m pip install --user
  --break-system-packages ruff`. Config is `ruff.toml`, which ignores `EXE001`
  (the style guide mandates the shebang on every `.py` regardless of the
  executable bit).
