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
primitives (drive, spin, query) with a result at the end. It is the
*check target locations* purpose of patrol; map-improvement and intruder
patrols are separate, later features.

## Flow

1. A request arrives on `/intent` carrying a **filter**.
2. dome_mission asks the semantic layer for the matching targets and a
   **viewpoint** for each.
3. dome_mission orders the viewpoints into a route.
4. For each stop: drive to the viewpoint (Nav2), do a **small spin**, then ask
   the semantic layer whether the target was **seen again** since arriving.
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

- **dome_mission judges nothing perceptual.** The semantic layer lists targets,
  proposes viewpoints, and says whether a target was re-seen. dome_mission only
  sequences, drives, and reports. This keeps the feature intact if open-ended
  discovery replaces today's tracker.
- **Rooms are not required.** The feature works on the flat target list; a
  room filter can be added once the hierarchical semantic map exists.
- **On request only.** No scheduling.

## Out of scope

- Scheduling or repeating patrols.
- Removing, ageing out, or editing targets.
- Deciding that an object *moved*.
- Map-improvement and intruder patrols.

## Dependencies

- **Semantic layer** (dome_semantic or its successor) must provide: list
  targets by filter, a viewpoint per target, and a re-seen check. None exist
  today.
- **Small-spin primitive** as an action. The `spin_survey` code leaving
  dome_control is a candidate source; its home is undecided.
- **Nav2** with a live robot pose — blocked today by I02 (no `amcl` in the
  explore stack).
- The **dome_mission redefinition** (multi-step behaviors over primitives,
  superseding parts of F03) should be written down first.

## Open questions

- **Filters**: by class, by time since last seen, by room (later) — others?
- **Report format**: a typed message (per target: id, label, verdict,
  last-seen) — and which interface package hosts it?
- **Intent name**: e.g. `patrol_check_targets` with a `filter` slot.
- **FSM or behavior tree**: a stop-by-stop loop is where the FSM starts to
  strain; `py_trees_ros` is the noted candidate.

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
