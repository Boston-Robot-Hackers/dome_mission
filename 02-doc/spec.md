# dome_mission — Spec

## Purpose

Mission-sequencing layer for the DOME robot (extracted from dome_nav per F35).
dome_mission owns `/intent` and orchestrates high-level behaviors by composing
lower-level primitives; dome_nav becomes primitives-only and never depends on
`dome_semantic_msgs`.

## Behaviors

- **explore** — start autonomous frontier exploration, run until no frontiers
  (or stopped), report outcome.
- **locate targets** — explore/survey while the semantic-ingest pipeline runs
  (F33 Phase C); the stateful cross-package sequence.
- **go to target** — resolve a semantic label → pose (typed, incl. yaw) and
  drive there via Nav2.

## Interfaces

- **Input**: `/intent` (std_msgs/String, JSON) — the sole `/intent` handler in
  the system.
- **In**: `SemanticTargetArray` (`dome_semantic_msgs`) — the semantic map, for
  label → pose resolution.
- **Out**: `ExploreArea` action (`dome_nav_msgs`, on dome_nav) — explore
  start/stop/preempt with feedback + terminal outcome.
- **Out**: Nav2 `NavigateToPose` action — drive-to-pose (called directly; no
  dome_nav hop).

## Design

- Pure/ROS split: a ROS-free FSM (`mission_fsm.py`) + parser (`intent_parser.py`)
  hold all logic; `mission_node.py` is a thin ROS seam.
- Transport = ROS actions (FSM→BT forward-compatible; a later swap to
  `py_trees_ros` keeps the interface). See TF35 T01 rationale.
- Boundary: per-goal abort authority stays in dome_nav's explorer watchdog; the
  FSM owns only mission-level start/stop/preempt + the terminal action outcome.

## Non-goals

- No behavior tree yet — FSM is sufficient for Phase A/C (3 mostly-sequential
  verbs). BT is a Phase-B candidate (reactive vision-aware behaviors).
- dome_mission never touches Nav2's internal C++ BT.
