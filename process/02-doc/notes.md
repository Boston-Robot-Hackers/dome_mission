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

## Layering

```
/intent ──► dome_mission (FSM) ──► ExploreArea action ──► dome_nav (explorer)
                    │
                    └──► NavigateToPose action ──► Nav2   (direct, no dome_nav hop)
            SemanticTargetArray (dome_semantic_msgs) ──► label→pose (dome_mission)
```

## Key decisions (from TF03 T01/T03)

- **Transport = ROS actions**, not topics/services. Long-running, cancellable,
  feedback/result; FSM→BT forward-compatible (`py_trees_ros` maps 1:1).
- **drive-to-pose talks to Nav2 directly** — dome_mission holds the semantic
  map, so routing the pose back through dome_nav would be a pointless hop.
- **Boundary**: per-goal abort (timeouts, stuck, blacklist) stays in dome_nav's
  explorer watchdog; the FSM owns mission-level start/stop/preempt + terminal
  `ExploreArea` outcome only.
- **FSM, not BT** for Phase A/C. BT is a Phase-B candidate (`py_trees_ros`,
  Python) — never Nav2's internal C++ BT.

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
