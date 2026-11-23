# TF04 — Check-Targets Patrol for Feature F04

**Date Created:** 2026-11-22

Task file name: `TF04-check-targets-patrol.md`.

Each step is numbered `TF04.N`, starting at `.0`. For each step, add a test when
feasible; if not feasible, note why.

**Blocked** until the semantic-layer queries and the small-spin primitive exist
(see F04 *Dependencies*). TF04.0 and TF04.1 can proceed before that.

## TF04.0 — Settle open questions

**Status**: not done

**Description**: Decide the filter set, the report message and its package, the
intent name and slots, and FSM vs behavior tree. Record the answers in F04.

**Test**: none — a decision step.

## TF04.1 — Define the interfaces

**Status**: not done

**Description**: Write the interface definitions dome_mission depends on: the
semantic-layer queries (list-by-filter, viewpoint, re-seen check), the
small-spin action, and the report message. Agree them with the owning packages.

**Test**: each definition builds and resolves with `ros2 interface show`.

## TF04.2 — Parse the patrol intent

**Status**: not done

**Description**: Add the patrol intent name and its `filter` slot to
`intent_parser`.

**Test**: unit tests for a valid request, a missing filter, and an unknown
filter key.

## TF04.3 — Pure route ordering

**Status**: not done

**Description**: A pure function that orders viewpoints into a route from the
robot's pose (e.g. greedy nearest-next).

**Test**: unit tests for empty, single, and multi-stop inputs, and a known
expected order.

## TF04.4 — Pure patrol sequencing

**Status**: not done

**Description**: Extend the mission logic (FSM or behavior tree per TF04.0)
with a patrolling state that steps through stops — drive, spin, check, next —
collects verdicts, skips unreachable stops, and supports cancel.

**Test**: unit tests driving the sequence with scripted outcomes: all
confirmed, one missing, one unreachable, cancel mid-route.

## TF04.5 — Node: semantic-layer clients

**Status**: not done

**Description**: In `mission_node`, call the semantic-layer queries without
blocking the executor, and map their results into the pure types.

**Test**: node tests with a mocked semantic server.

## TF04.6 — Node: execute the stops

**Status**: not done

**Description**: Drive each stop via Nav2, run the small-spin action, then run
the re-seen check; feed each outcome back into the sequencing logic.

**Test**: node tests with mocked Nav2, spin, and semantic servers.

## TF04.7 — Publish the report

**Status**: not done

**Description**: Publish the report message at the end of a patrol (including
after cancel, with remaining stops unchecked), and republish `/mission/state`
on every transition.

**Test**: node test asserting the report contents and the state sequence.

## TF04.8 — Test suite for F04

**Status**: not done

**Description**: Review coverage across TF04.2–TF04.7 and fill gaps, including
edge cases (no matching targets, all stops unreachable).

**Test**: full `/usr/bin/python3 -m pytest test/` passes.

## TF04.9 — Live demo in sim

**Status**: not done

**Description**: Run F04's *How to Demo* in sim and record command, setup,
expected and actual results.

**Test**: manual — needs the live sim stack; not part of the plain test run.
