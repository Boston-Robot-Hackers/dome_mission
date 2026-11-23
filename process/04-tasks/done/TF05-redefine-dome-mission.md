# TF05 — Redefine dome_mission for Feature F05

**Date Created:** 2026-11-22

Task file name: `TF05-redefine-dome-mission.md`.

Each step is numbered `TF05.N`, starting at `.0`. Docs only, so no step has an
automated test; each is checked by reading it against F05.

## TF05.0 — Rewrite the spec

**Status**: done

**Description**: Rewrite `process/02-doc/spec.md` (purpose, behaviors,
interfaces, design, non-goals) to F05's definition and package roles:

- the single `/intent` consumer;
- the `/semantic/targets` subscription;
- Nav2 `Spin`/`DriveOnHeading` among the outputs;
- plain sequential behaviors instead of the FSM-for-now non-goal.

Mark the merged-in intents (`stop`, turns, queries) as planned until the merge
feature lands.

**Test**: none (docs only); checked by review.

## TF05.1 — Update CLAUDE.md and notes

**Status**: done

**Description**: Change `CLAUDE.md`'s project paragraph and sibling list to
"the single brain", and add `dome_control` and Nav2's behavior server. Update
`process/02-doc/notes.md` (layering, key decisions, package relationships) to
the same boundaries.

**Test**: none (docs only); checked by review.

## TF05.2 — Mark F03 as partly superseded

**Status**: done

**Description**: Add a short banner to `F03-mission-layer.md` naming what F05
replaces: sole-handler status is pending the merge, and the FSM-for-now choice
is replaced. Point the banner to F05.

**Test**: none (docs only).

## TF05.3 — Reconcile mission.md

**Status**: done

**Description**: Fit `process/02-doc/mission.md`'s Mapping / Discovery /
Command phases to F05, written as sequential behaviors that dome_mission runs.
Fill in the empty Discovery and Command sections only with what has been
decided.

**Test**: none (docs only); checked by review.

## TF05.4 — Re-scope F04 and F07

**Status**: done

**Description**: Update F04 to use Nav2 `Spin` instead of a new primitive. Mark
F07 as largely moot (`label_resolver` stays) and propose deferring it. Adjust
their task files to match.

**Test**: none (docs only).

## TF05.5 — Record the follow-on merge feature

**Status**: done

**Description**: Add the "merge the brain" feature as the next `Fnn` in
`process/03-features/notdone/`, with its task file. It is parked, not approved
for code. Note the matching dome_control change in `current.md` under
**Needed from other repos**.

**Test**: none (docs only); the feature's own tasks carry the tests.
