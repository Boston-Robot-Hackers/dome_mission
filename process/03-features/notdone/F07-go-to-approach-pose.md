# F07 — Go to a Target's Approach Pose

> **Rewritten 2026-11-23 after F05.** The 2026-11-22 draft ("go to a target by
> semantic query") replaced the local semantic map with a resolve query. F05
> rejected that. This version keeps `label_resolver` and the
> `/semantic/targets` subscription, and fixes where go-to drives to.

**Priority**: Medium

**Date Created:** 2026-11-22

**Done:** no

**Tasks File Created:** yes

**Tests Written:** no

**Test Passing:** no

**Description**: Go-to drives to a pose **next to** the target, facing it,
instead of to the target's own pose.

## The problem

Today `drive_to_label` (`mission_node.py`) sends Nav2 the target's position.
For orientation it uses the target's stored yaw, which comes from dome_semantic
and isn't a "face the object" heading.

That causes two problems:

- **The goal can be unreachable.** If the object shows up in the costmap, the
  goal sits on an occupied cell and Nav2 may reject it or fail. *Unverified*
  whether small objects like a can reach the costmap at DOME's lidar height.
- **The robot ends up facing an arbitrary way**, not looking at the object.

## Scope

- A **pure approach-pose function**. Given a target position, the robot's
  position and a stand-off distance, it returns a goal on the line from the
  target toward the robot, at the stand-off distance, with yaw facing the
  target.
- **`drive_to_label` uses it** instead of the target pose.
- **Candidate policy stays nearest-to-robot**, as in today's
  `SemanticTargetStore.resolve`.
- The stand-off distance is a **ROS parameter**.

F04's viewpoint step (TF04.3) reuses this function, so F07 comes first.

## Key decisions

- **dome_mission computes it.** Where to stand is a mission decision, not a
  fact about the world (F05). dome_semantic is unchanged.
- **No new interfaces.**
- **One goal, no fallback search.** If Nav2 can't reach the approach pose, the
  go-to fails with a reason, as today. Trying other angles waits until failures
  show it is needed.

## Open questions

- **No robot pose** (`/amcl_pose` silent, I02): fall back to today's behavior
  (target pose, stored yaw)? Or fail the go-to with a reason?
- **Stand-off default**: one value, or per class from dome_semantic's
  `class_profiles.yaml`? (A per-class value would read a dome_semantic config
  file.)
- **Robot already within the stand-off**: report success without moving, or
  just turn to face the target?

## Out of scope

- A semantic resolve query, opaque targets, rooms. Revisit only when a request
  can't be answered from `/semantic/targets`.
- Choosing among several candidates by anything other than distance.
- Retrying at other approach angles.

## Dependencies

- A live robot pose for the live demo (I02). Pure and node tests don't need it.

## How to Demo

**Setup**: sim stack localized, dome_semantic publishing at least one confirmed
can, robot at least 2 m away from it.

**Steps**:
1. Publish `navigation_go` with label `can`.
2. Watch the robot in RViz.

**Expected output**:

- The robot stops at about the stand-off distance from the can, facing it.
- `/mission/state` goes `GOING_TO_TARGET` → `IDLE`.

## Process Gate

After creating this feature file and the corresponding task file, **stop and present the plan to the user**. Do not write any code or content until the user gives explicit approval to proceed.
