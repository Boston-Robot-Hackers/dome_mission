# TF06 — Explore with Extent for Feature F06 (draft)

**Date Created:** 2026-11-22

Task file name: `TF06-explore-with-extent.md`.

Each step is numbered `TF06.N`, starting at `.0`. Steps after TF06.0 are
provisional until the open questions in F06 are settled.

## TF06.0 — Settle open questions

**Status**: not done

**Description**: Decide the extent kinds and their order, whether capture is an
option or the default, and how a room extent is expressed. Record in F06.

**Test**: none — a decision step.

## TF06.1 — Agree the ExploreArea extent with dome_nav

**Status**: not done

**Description**: Check the current `ExploreArea.Goal` fields and agree the
extent fields dome_nav will enforce. The dome_nav change is that repo's feature.

**Test**: `ros2 interface show dome_nav_msgs/action/ExploreArea` shows the
agreed fields.

## TF06.2 — Parse explore options

**Status**: not done

**Description**: Extend `intent_parser` with extent and capture slots on the
explore intent; add an intent name that reaches `LOCATING` if capture stays a
separate behavior.

**Test**: unit tests for each slot, missing slots, and invalid values.

## TF06.3 — FSM and node: pass the extent, report the stop reason

**Status**: not done

**Description**: Carry the extent into the `ExploreArea` goal; map the new
terminal outcomes into the FSM; republish `/mission/state` on completion.

**Test**: FSM unit tests and node tests with a mocked `ExploreArea` server.

## TF06.4 — "Until found" condition (if kept)

**Status**: not done

**Description**: While exploring, re-query the semantic layer periodically and
cancel the explore when a candidate passes the threshold.

**Test**: node test with mocked semantic and explore servers.

## TF06.5 — Test suite for F06

**Status**: not done

**Description**: Fill coverage gaps across TF06.2–TF06.4.

**Test**: full `/usr/bin/python3 -m pytest test/` passes.

## TF06.6 — Live demo in sim

**Status**: not done

**Description**: Run F06's *How to Demo*; record command, setup, expected and
actual results.

**Test**: manual — needs the live sim stack.
