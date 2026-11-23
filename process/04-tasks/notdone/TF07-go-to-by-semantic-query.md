# TF07 — Go to a Target by Semantic Query for Feature F07 (draft)

**Date Created:** 2026-11-22

Task file name: `TF07-go-to-by-semantic-query.md`.

Each step is numbered `TF07.N`, starting at `.0`. Steps after TF07.0 are
provisional until the open questions in F07 are settled.

## TF07.0 — Settle open questions

**Status**: not done

**Description**: Decide the multi-candidate policy and the query transport;
take the `target` schema from the semantic layer. Record in F07.

**Test**: none — a decision step.

## TF07.1 — Agree the resolve interface

**Status**: not done

**Description**: Agree the resolve query's definition with the semantic layer
(request: target, robot pose; response: candidates with approach pose,
confidence, id).

**Test**: the interface builds and resolves with `ros2 interface show`.

## TF07.2 — Opaque target in the intent

**Status**: not done

**Description**: Change `navigation_go`'s slot from `label` to an opaque
`target` in `intent_parser`.

**Test**: unit tests for present, missing, and malformed targets.

## TF07.3 — Pure candidate policy

**Status**: not done

**Description**: A pure function choosing among candidates per the TF07.0
policy.

**Test**: unit tests for zero, one, and several candidates.

## TF07.4 — Node: query, then drive

**Status**: not done

**Description**: Replace `drive_to_label` with a non-blocking resolve call
followed by the Nav2 drive; remove `label_resolver`, the store, and the
`/semantic/targets` subscription; republish `/mission/state` on completion.

**Test**: node tests with mocked resolve and Nav2 servers.

## TF07.5 — Test suite for F07

**Status**: not done

**Description**: Fill coverage gaps across TF07.2–TF07.4, and delete tests for
removed code.

**Test**: full `/usr/bin/python3 -m pytest test/` passes.

## TF07.6 — Live demo in sim

**Status**: not done

**Description**: Run F07's *How to Demo*; record command, setup, expected and
actual results.

**Test**: manual — needs the live sim stack.
