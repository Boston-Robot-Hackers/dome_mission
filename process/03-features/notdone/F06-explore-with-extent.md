# F06 — Explore and Map, with Extent and Capture Options (draft)

**Priority**: Medium

**Date Created:** 2026-11-22

**Done:** no

**Tasks File Created:** yes

**Tests Written:** no

**Test Passing:** no

**Description**: The *Mapping* phase. On request, the robot drives into
unmapped space and builds the SLAM map. Two options shape the run:

- **Extent** — how far it explores and when it stops.
- **Capture** — whether it is also recording semantic targets as it goes.

**Draft:** the open questions below must be settled before tasks start.

## What exists today

- dome_nav's explorer does frontier exploration via the `ExploreArea` action;
  verified end to end in sim.
- It stops only when frontiers run out (`EXPLORED_DONE`) or all are blocked
  (`NO_TARGETS_BLOCKED`).
- The FSM has a `LOCATING` state (explore while semantic ingest runs), but no
  `/intent` name reaches it.

## Scope

- **Extent / stop conditions** — some mix of: a region (polygon, radius from
  start, named room), a time or distance budget, a coverage threshold, or
  "until a requested object is found".
- **Split of responsibility**: area and budget limits are enforced by dome_nav
  (passed on the `ExploreArea` goal); "until found" is a mission-level condition
  owned here, using the semantic query interface.
- **Capture**: make `LOCATING` reachable from `/intent`. Semantic ingest is
  always-on, so this is mainly mission state plus launch composition.

## Dependencies

- dome_nav: extent fields on `ExploreArea.Goal` (not checked which fields exist
  today besides `map_name`).
- Semantic layer query interface — only for "until found".
- F05 definition.

## Open questions

- Which extent kinds: area, budget, coverage, "until found" — and which first?
- Is capture an option on explore, or the default (with plain explore the
  exception)?
- What does a named-room extent need, given rooms come from the semantic
  layer's hierarchical map?

## How to Demo

**Setup**: sim stack; an unexplored world larger than the chosen extent.

**Steps**:
1. Publish an explore intent with an extent (e.g. a budget or region).
2. Watch exploration.

**Expected output**: the robot stops at the extent, not at frontier
exhaustion; the `ExploreArea` result and `/mission/state` report it.

## Process Gate

After creating this feature file and the corresponding task file, **stop and present the plan to the user**. Do not write any code or content until the user gives explicit approval to proceed.
