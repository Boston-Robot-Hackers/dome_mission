# F07 — Go to a Target by Semantic Query (draft)

**Priority**: Medium

**Date Created:** 2026-11-22

**Done:** no

**Tasks File Created:** yes

**Tests Written:** no

**Test Passing:** no

**Description**: The *Command* phase's go-to. Given built maps, the robot
accepts a request like "go to the can in the living room" and drives there. The
maps may keep updating during the drive.

The change from today: dome_mission **asks the semantic layer** where the target
is, instead of keeping its own copy of the semantic map and matching labels
itself.

**Draft:** the open questions below must be settled before tasks start.

## Flow

1. `/intent` `navigation_go` arrives with an **opaque `target`** (already parsed
   upstream, probably by an LLM).
2. dome_mission calls the semantic layer's resolve query with the target and the
   robot pose.
3. It gets back **candidates** — each a drivable goal pose (an approach pose,
   not the object's centre), a confidence, and an id.
4. dome_mission applies its policy and sends the chosen pose to Nav2.

## Scope

- Remove `label_resolver.py`, `SemanticTargetStore`, and the
  `/semantic/targets` subscription.
- **Candidate policy**: zero → fail with a reason; one → go; several → pick by
  confidence or distance, or report the ambiguity.
- Call the query without blocking the executor (it may be slow with open-ended
  discovery).

## Not dome_mission's

- Matching, the `target` schema, approach-pose geometry and arrival yaw — the
  semantic layer's.
- Keeping the SLAM map current during the drive — dome_nav's map mode.
- Rooms ("in the living room") — resolved inside the semantic layer.

## Dependencies

- Semantic layer: the resolve query, returning approach poses.
- dome_nav: a live robot pose after mapping (I02).
- F05 definition.

## Open questions

- Several candidates: which policy?
- Query transport: action (cancellable, allows slow resolvers) vs async
  service.
- `target` schema: string or structured — the semantic layer's call, but it
  shapes the intent slot.

## How to Demo

**Setup**: sim stack localized; semantic layer serving the resolve query with
at least one known can.

**Steps**:
1. Publish `navigation_go` with target "can".
2. Watch the robot.

**Expected output**: the robot drives to a pose next to the can, facing it;
`/mission/state` goes `GOING_TO_TARGET` → `IDLE`.

## Process Gate

After creating this feature file and the corresponding task file, **stop and present the plan to the user**. Do not write any code or content until the user gives explicit approval to proceed.
