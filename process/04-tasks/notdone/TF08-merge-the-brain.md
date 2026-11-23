# TF08 — Merge the Brain for Feature F08

**Date Created:** 2026-11-23

Task file name: `TF08-merge-the-brain.md`.

Each step is numbered `TF08.N`, starting at `.0`. For each step, add a test when
feasible; if not feasible, note why.

**Parked**: F08 is not approved for code.

## TF08.0 — Settle open points

**Status**: not done

**Description**: Decide four things and record them in F08:

- the threading model (worker thread or multi-threaded executor with async
  callbacks);
- where the announcement contract lives;
- whether `list_objects` and `count_objects` answer from `/semantic/targets`;
- where `get_status` gets its speeds.

Also check that Nav2's behavior server is launched in each stack dome_mission
runs with.

**Test**: none (a decision step).

## TF08.1 — Extend the intent parser

**Status**: not done

**Description**: Add `stop`, `turn_left`, `turn_right`, `drive_square` (with a
`meters` slot), `get_status`, `describe_scene`, `list_objects`,
`count_objects` and `get_help` to `intent_parser.py`.

**Test**: unit tests for each name, the `meters` slot (default and given), and
an unknown name.

## TF08.2 — Single active-goal and stop

**Status**: not done

**Description**: One place that tracks the active goal across all action
clients (`ExploreArea`, `NavigateToPose`, `Spin`, `DriveOnHeading`). A new
motion intent preempts it, and `stop` cancels it. This also closes the parked
"late result clobbers a newer goal handle" bug.

**Test**: unit tests with fake clients: stop while idle, stop during each goal
type, preempt, late result after preempt.

## TF08.3 — Motion behaviors

**Status**: not done

**Description**: Turns as Nav2 `Spin` ±90°, and `drive_square` as sequential
`DriveOnHeading` + `Spin` steps, run off the executor thread per TF08.0.

**Test**: tests with mocked action servers: a full square, stop mid-square,
and a rejected goal.

## TF08.4 — Query handlers

**Status**: not done

**Description**: Port `describe_scene`, `list_objects`, `count_objects`,
`get_status` and `get_help` from dome_control's `PerceptionBehavior` and
`MotionBehavior`. Answer each as an `/announcement`.

**Test**: node tests with a mocked `/describe_scene` and a scripted
`/semantic/targets`, asserting the announcement text and priority.

## TF08.5 — Republish state on every transition

**Status**: not done

**Description**: Make `/mission/state` follow every behavior, including after
`on_done`. This closes the parked "state not republished" bug.

**Test**: node test asserting the state sequence for a turn and for a stop.

## TF08.6 — Test suite for F08

**Status**: not done

**Description**: Review coverage across TF08.1–TF08.5 and fill gaps.

**Test**: full `/usr/bin/python3 -m pytest test/` passes.

## TF08.7 — Live demo in sim

**Status**: not done

**Description**: Run F08's *How to Demo* with dome_control's
`behavior_manager_node` stopped. Record command, setup, expected and actual
results.

**Test**: manual (needs the live sim stack).
