# dome_mission — Spec

## Purpose

**dome_mission is the DOME robot's brain** (F05). It is the only node that
consumes `/intent`, and it alone owns what the robot is doing now. It turns
each intent into either a query answer or a behavior. It runs a behavior by
calling motion actions in sequence, and `stop` cancels whatever is running.

It implements no motion and builds no world model. It talks to no human
directly.

## Package roles

| Package | Role | Owns |
|---|---|---|
| dome_control | operator surface | CLI/REPL, operator input → `/intent`, status display, process/launch management |
| **dome_mission** | **brain** | intent parsing, arbitration, `/mission/state`, query answers, behaviors |
| dome_semantic | world model | the object map, its persistence, `/semantic/targets`, `/describe_scene` |
| dome_nav, Nav2 | motion primitives | `ExploreArea`, `NavigateToPose`, `Spin`, `DriveOnHeading` |

**Where does new code go?**

- It decides what happens next, or when something is finished → dome_mission.
- It is a fact about the world → dome_semantic.
- It moves the robot on its own → a primitive action (Nav2 or dome_nav).
- The robot would behave the same without it, given intents some other way →
  dome_control.

## Behaviors

Today:

- **explore**: run frontier exploration until no frontiers remain or it is
  stopped, then report the outcome.
- **go to target**: resolve a semantic label to a pose (including yaw) and
  drive there with Nav2.

Planned. These arrive with the brain merge (F08), when
dome_control's `behavior_manager_node` moves in:

- **stop**: cancel the active goal, whatever it is.
- **turn left/right**: Nav2 `Spin`.
- **queries** (`describe_scene`, `count_objects`, `get_status`): call the
  service, publish an `/announcement`.

Later: patrol (F04), explore within an extent (F06), and the
Mapping → Discovery → Command phases (`process/02-doc/mission.md`).

## Interfaces

- **In**: `/intent` (`std_msgs/String`, JSON). dome_mission is meant to be the
  only subscriber. Until F08 lands, dome_control's `behavior_manager_node`
  also subscribes and handles a disjoint set of names.
- **In**: `/semantic/targets` (`SemanticTargetArray`, `dome_semantic_msgs`).
  This is a local copy of the object map, used for label → pose and for filters
  over targets.
- **Out**: `ExploreArea` action (`dome_nav_msgs`, served by dome_nav).
- **Out**: Nav2 `NavigateToPose` action. It is called directly, with no
  dome_nav hop.
- **Out** (planned, F08): Nav2 behavior-server `Spin` and `DriveOnHeading`
  actions. They are already enabled in every dome_nav Nav2 params file.
- **Out**: `/mission/state` (`std_msgs/String`, transient-local).
- **Out** (planned, F08): `/announcement` (dome_control's announcement
  contract).

## Design

- **Pure/ROS split**: pure modules hold the logic, and `mission_node.py` is a
  thin ROS seam.
- **Behaviors are plain sequential code.** Each step waits on an action, so a
  patrol is a loop. Today's FSM (`mission_fsm.py`) covers explore and go-to; new
  behaviors don't each add FSM states. *Hazard*: in rclpy, sequential code
  needs a worker thread per behavior or async callbacks on a multi-threaded
  executor.
- **Subscribe to the semantic map; don't query it.** The array is small, and a
  local lookup needs no async round trip. Add a service only when a question
  can't be answered from the array.
- **Boundary**: per-goal abort authority (timeouts, stuck, blacklist) stays in
  dome_nav's explorer watchdog. dome_mission owns only start/stop/preempt and
  the terminal outcome.

## Non-goals

- No English parsing; intents arrive structured.
- No `/cmd_vel`; all motion goes through actions.
- No world model; dome_semantic builds it.
- No map maintenance; localization vs lifelong SLAM is a dome_nav mode.
- No behavior-tree framework for now. `py_trees_ros` is a candidate only if
  reactive interrupts multiply. dome_mission never touches Nav2's internal
  C++ BT.
