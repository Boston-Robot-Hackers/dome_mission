# TF04 — Check-Targets Patrol for Feature F04

**Date Created:** 2026-11-22

Task file name: `TF04-check-targets-patrol.md`.

Each step is numbered `TF04.N`, starting at `.0`. For each step, add a test when
feasible; if not feasible, note why.

Only the live demo (TF04.9) is blocked, on I02. Everything else uses the
local `/semantic/targets` copy and Nav2 `Spin` (F05), so it can be built and
tested with mocks now.

## TF04.0 — Settle open questions

**Status**: not done

**Description**: Decide the filter set, the report message and its package,
the intent name and slots, the viewpoint geometry and the settle time. Record
the answers in F04.

**Test**: none — a decision step.

## TF04.1 — Define the report message

**Status**: not done

**Description**: Write the report message definition in the package chosen in
TF04.0. No semantic-layer or spin interfaces are needed: the semantic map is
already published, and Nav2 provides `Spin`.

**Test**: the definition builds and resolves with `ros2 interface show`.

## TF04.2 — Parse the patrol intent

**Status**: not done

**Description**: Add the patrol intent name and its `filter` slot to
`intent_parser`.

**Test**: unit tests for a valid request, a missing filter, and an unknown
filter key.

## TF04.3 — Pure target selection, viewpoints and route

**Status**: not done

**Description**: Pure functions that filter the local target list, compute a
viewpoint per target (reuse F07's `approach_pose`, TF07.1), order the viewpoints into a route from the robot's pose
(e.g. greedy nearest-next), and judge re-seen from `last_seen` and the arrival
time.

**Test**: unit tests for each: filter hits and misses, viewpoint geometry,
empty, single and multi-stop routes with a known order, and seen vs not seen
at the boundary.

## TF04.4 — Patrol sequence

**Status**: not done

**Description**: Write the patrol as plain sequential code (F05) that steps
through the stops (drive, spin, check, next), collects verdicts, skips
unreachable stops, and supports cancel. Keep the ROS calls behind an injected
interface so the sequence is testable without ROS.

**Test**: unit tests driving the sequence with scripted outcomes: all
confirmed, one missing, one unreachable, cancel mid-route.

## TF04.5 — Node: run the sequence without blocking

**Status**: not done

**Description**: In `mission_node`, run the patrol sequence on a worker thread
or as async callbacks on a multi-threaded executor, so `/intent` and action
callbacks keep flowing during a patrol.

**Test**: node test showing a cancel intent is handled mid-patrol.

## TF04.6 — Node: execute the stops

**Status**: not done

**Description**: Drive each stop via Nav2 `NavigateToPose`, run Nav2 `Spin`,
then run the re-seen check against the local target copy; feed each outcome
back into the sequence.

**Test**: node tests with mocked `NavigateToPose` and `Spin` servers and a
scripted `/semantic/targets`.

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
