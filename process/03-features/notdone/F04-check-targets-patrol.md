# F04 — Check-Targets Patrol

**Priority**: Low

**Date Created:** 2026-11-22

**Done:** no

**Tasks File Created:** yes

**Tests Written:** no

**Test Passing:** no

**Description**: On request, the robot visits a filtered set of known semantic
targets, takes a look at each one, and publishes a report saying which are still
where the map says and which are missing.

This is dome_mission's first true **multi-step behavior**: a sequence of
actions (drive, spin) and checks against the local semantic map, with a result
at the end. It is written as plain sequential code (F05). It is the
*check target locations* purpose of patrol; map-improvement and intruder
patrols are separate, later features.

## Flow

1. A request arrives on `/intent` carrying a **filter**.
2. dome_mission filters its local copy of `/semantic/targets` and computes a
   **viewpoint** for each match (a stand-off pose facing the target).
3. dome_mission orders the viewpoints into a route.
4. For each stop: drive to the viewpoint (Nav2 `NavigateToPose`), do a
   **small spin** (Nav2 `Spin`), then check whether the target's `last_seen`
   is later than the arrival time, i.e. it was **seen again**.
5. A stop whose viewpoint can't be reached is **skipped**.
6. After the last stop, publish the **report on a topic**.

## Verdicts

- **confirmed** — re-observed at its location.
- **missing** — not re-observed. **Reported only**; dome_mission changes
  nothing on the map.
- **unchecked** — viewpoint unreachable, skipped.

A sighting somewhere else is *not* a verdict. The semantic layer records it as a
**new target** in its normal way, and the original reports as missing.

## Key decisions

- **dome_mission judges nothing perceptual.** dome_semantic decides what was
  observed and stamps `last_seen`. dome_mission only compares timestamps,
  sequences, drives, and reports.
- **No new semantic-layer interfaces** (F05). Filtering, viewpoints and the
  re-seen check all use the published `SemanticTargetArray`.
- **Rooms are not required.** The feature works on the flat target list; a
  room filter can be added once the hierarchical semantic map exists.
- **On request only.** No scheduling.

## Out of scope

- Scheduling or repeating patrols.
- Removing, ageing out, or editing targets.
- Deciding that an object *moved*.
- Map-improvement and intruder patrols.

## Dependencies

- **Nav2** with a live robot pose. This is blocked today by I02 (no `amcl` in
  the explore stack).
- **Nav2 `Spin`**: already enabled in dome_nav's Nav2 params; no new
  primitive is needed.
- **F07** first: its `approach_pose` function is the viewpoint.
- **F05** (the definition) first. F08 (the brain merge) is not required:
  `navigation_cancel` cancels a patrol today, and the universal `stop` does
  so once F08 lands.

## Open questions

- **Filters**: by class, by time since last seen, by room (later) — others?
- **Report format**: a typed message (per target: id, label, verdict,
  last-seen) — and which interface package hosts it?
- **Intent name**: e.g. `patrol_check_targets` with a `filter` slot.
- **Viewpoint geometry**: the stand-off distance, and which side of the
  target to stand on.
- **Settle time**: how long after the spin to wait before checking
  `last_seen`.

## How to Demo

**Setup**: sim stack with Nav2 localized, the semantic layer running with at
least three confirmed targets of one class, and one of them removed from the
world after it was mapped.

**Steps**:
1. Publish a `patrol_check_targets` intent filtered to that class.
2. Watch the robot visit each viewpoint and spin.
3. Echo the report topic.

**Expected output**: the robot visits every reachable viewpoint; the report
lists the present targets as *confirmed* and the removed one as *missing*;
`/mission/state` returns to `IDLE`.

## Process Gate

After creating this feature file and the corresponding task file, **stop and present the plan to the user**. Do not write any code or content until the user gives explicit approval to proceed.
