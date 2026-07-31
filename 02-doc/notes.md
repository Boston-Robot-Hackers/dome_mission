# dome_mission — Notes

Semi-permanent project notes. Durable facts, not session narration.

## Origin

Extracted from dome_nav per **F35** (mission-sequencing layer). The extraction
is tracked in dome_nav's `04-tasks/notdone/TF35-mission-layer.md`, interleaved
with dome_nav's F33 (semantic exploration) Phase A.

Motivation: dome_nav had accreted mission/label logic (`nav_manager`,
`/intent` handling in `explorer_manager_node`). F35 pulls that up into a neutral
layer so dome_nav is primitives-only and never depends on `dome_semantic_msgs`.

## Layering

```
/intent ──► dome_mission (FSM) ──► ExploreArea action ──► dome_nav (explorer)
                    │
                    └──► NavigateToPose action ──► Nav2   (direct, no dome_nav hop)
            SemanticTargetArray (dome_semantic_msgs) ──► label→pose (dome_mission)
```

## Key decisions (from TF35 T01/T03)

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
