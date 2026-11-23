# TF07 — Go to a Target's Approach Pose for Feature F07

**Date Created:** 2026-11-22

> **Rewritten 2026-11-23** with F07. The earlier steps assumed a semantic
> resolve query, which F05 dropped.

Task file name: `TF07-go-to-approach-pose.md`.

Each step is numbered `TF07.N`, starting at `.0`. For each step, add a test when
feasible; if not feasible, note why.

## TF07.0 — Settle open questions

**Status**: not done

**Description**: Decide three things and record them in F07:

- the no-robot-pose behavior;
- the stand-off default (single value or per class);
- what happens when the robot is already within the stand-off.

**Test**: none (a decision step).

## TF07.1 — Pure approach-pose function

**Status**: not done

**Description**: Add `approach_pose(target_xy, robot_xy, standoff_m)` to
`label_resolver.py`. It returns a `TargetPose`-like goal on the target→robot
line, `standoff_m` from the target, with yaw facing the target.

**Test**: unit tests for:

- the robot on each axis and on a diagonal (position and yaw);
- a stand-off larger than the distance (per TF07.0);
- the robot exactly at the target (degenerate direction).

## TF07.2 — Use it in `drive_to_label`

**Status**: not done

**Description**: Declare the stand-off ROS parameter. Build the Nav2 goal from
`approach_pose`, and apply the TF07.0 no-pose rule.

**Test**: node test with a mocked Nav2 server, asserting the goal's position
and orientation for a known target and robot pose. A second test covers the
no-pose case.

## TF07.3 — Test suite for F07

**Status**: not done

**Description**: Review coverage across TF07.1–TF07.2 and fill gaps. Update
existing `test_mission_node.py` cases that assert the old target-pose goal.

**Test**: full `/usr/bin/python3 -m pytest test/` passes.

## TF07.4 — Live demo in sim

**Status**: not done

**Description**: Run F07's *How to Demo*. Record command, setup, expected and
actual results.

**Test**: manual (needs the live sim stack and I02).
