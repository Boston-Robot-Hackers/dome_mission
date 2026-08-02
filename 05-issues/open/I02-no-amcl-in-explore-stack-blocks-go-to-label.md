# I02 mission_node's /amcl_pose has no publisher in the explore/sim launch

* **What the symptom is**: `mission_node` subscribes `/amcl_pose`
  (`dome_mission/mission_node.py:71-72`,
  `geometry_msgs/msg/PoseWithCovarianceStamped`) and uses it as the robot's
  live pose for go-to-target resolution (T05: nearest-match label lookup,
  yaw, drive-to-pose). The top-level launch this package actually runs
  (`launch/mission_explore.launch.py` → `dome_nav`'s
  `sim_nav_full.launch.py` → `sim_nav2.launch.py`) loads
  `nav2_params_explore_sim.yaml`, whose header comment states "amcl/
  map_saver/loopback dropped" — this stack uses `slam_toolbox` for SLAM
  (build map + localize together) instead of `amcl`. Confirmed no remap
  anywhere makes `slam_toolbox` publish onto `/amcl_pose`. Result: in the
  explore stack, `mission_node.on_amcl_pose` never fires — `mission_node`
  has no live robot pose. This is independent of and in addition to the
  F33/TF33 blocker (`/semantic/targets` has no publisher yet): even once
  F33 lands, go-to-label would still fail because there is no pose to
  resolve/drive from in this launch configuration.
* **What tests have already been done**: confirmed live on the sim host
  2026-08-02 — `ros2 topic info /amcl_pose` style checks and a full grep of
  `dome_nav` for any `amcl_pose` remap turned up nothing outside the old,
  deleted `nav_manager_node` (F06/TF06, superseded by this package per T06
  cleanup). `dome_nav/02-doc/spec.md:64-67` documents `amcl` +
  `map_server` as the intended localization stack for label-based
  navigation, distinct from the explore/mapping stack.
* **What the latest theory is**: the implied design is a mode handoff —
  run `slam_toolbox`-based explore/mapping first, then switch to
  `map_server` + `amcl` against the just-built map for subsequent
  label-driven navigation. That handoff was never actually wired at the
  launch level: `dome_nav/launch/` has no `localization_launch.py` despite
  `config/nav2_params_localization_real.yaml` existing for exactly this
  purpose. Fix likely needs a `dome_nav` launch file for localization mode
  plus a `dome_mission`-side decision on how/when to trigger the switch
  (e.g. after `ExploreArea` completes) — not investigated further this
  session.
