# F08 — Merge the Brain into dome_mission

**Priority**: Medium

**Date Created:** 2026-11-23

**Done:** no

**Tasks File Created:** yes

**Tests Written:** no

**Test Passing:** no

**Description**: Make dome_mission the only `/intent` consumer, as F05
defines. Move dome_control's `behavior_manager_node` duties into `mission_node`.
dome_control then stops subscribing to `/intent`.

**Parked, not approved for code.**

## Why

Two nodes split `/intent` by name today (dome_control F19), each with its own
parser. dome_control's `stop` is a motor halt that doesn't cancel dome_mission's
goals. It also can't interrupt motion inside `behavior_manager`, because motion
blocks that node's only executor thread. One consumer fixes both by
construction.

## What moves in

| Intent | Today (dome_control) | After (dome_mission) |
|---|---|---|
| `stop` | `RobotController.stop_robot()` (zero `/cmd_vel`) | cancel the active goal, whatever it is |
| `turn_left` / `turn_right` | blocking 90° turn via `RobotController` | Nav2 `Spin` ±90° |
| `drive_square` | scripted `/cmd_vel` square | 4 × (`DriveOnHeading` + `Spin` 90°), as sequential code |
| `get_status` | speeds from `RobotController` | from config/params, published as an `/announcement` |
| `describe_scene` | `/describe_scene` service → `/announcement` | same, moved as is |
| `list_objects` | caches `/oak/detections` | same, or answered from `/semantic/targets` (decide in TF08.0) |
| `count_objects` | stub | stub, or answered from `/semantic/targets` |
| `get_help` | fixed announcement | same |

## Key decisions

- **One parser.** Keep dome_mission's `intent_parser.py` and extend its name
  table. dome_control's `IntentParser` is no longer needed for `/intent`.
- **No `/cmd_vel` from dome_mission.** All motion goes through actions, so
  `stop` is a single "cancel active goal" path.
- **Behaviors run off the executor thread.** Use a worker thread, or async
  callbacks on a multi-threaded executor, so `stop` is always heard.
- **Nav2 must be up for motion intents.** Turning with Nav2 down falls back to
  dome_control's manual CLI movement, which stays an operator tool.

## Out of scope

- dome_control's side: deleting `behavior_manager_node`, its behaviors and its
  launch entry, and updating F19 and `control-architecture.md`. That is a
  dome_control feature, sequenced after this one.
- Patrol (F04) and explore-with-extent (F06).
- `spin_survey`: retire it or re-express it as `Spin` goals, separately.

## Dependencies

- F05 (the definition).
- Nav2's behavior server running in the stacks that dome_mission launches with.
  Its plugins are enabled in every dome_nav Nav2 params file. Whether the
  server is actually launched in each stack is *unverified*.
- The announcement contract (`AnnouncementMsg`, priorities) currently lives in
  `dome_control/announcement_contract.py`. TF08.0 decides whether dome_mission
  imports it or the contract moves to an interface package.

## How to Demo

**Setup**: sim stack with Nav2 (behavior server included), dome_semantic, and
`mission_node`. dome_control's `behavior_manager_node` is **not** running.

**Steps**:
1. `turn_left` intent, then `stop` mid-turn.
2. `exploration_start`, then `stop` while exploring.
3. `describe_scene`.

**Expected output**:

- The turn and the exploration both halt on `stop`, and `/mission/state`
  returns to `IDLE`.
- `describe_scene` produces an `/announcement`.
- `ros2 topic info /intent` shows one subscriber.

## Process Gate

After creating this feature file and the corresponding task file, **stop and present the plan to the user**. Do not write any code or content until the user gives explicit approval to proceed.
