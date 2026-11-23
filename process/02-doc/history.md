# History — dome_mission

Completed items moved out of `current.md`'s `## Open` section, newest first.

- **`.claude/` synced to the j3 kit (2026-11-22)**: style guide v4.1 → v4.4,
  new process rules, commands, hooks and templates. Process folders moved
  under `process/`, `.githooks/pre-commit` header stamper installed,
  `current.md` reshaped to the `## Open`-only format, `Date Created:` added to
  feature and task files.

- **Clean stop on launch shutdown (2026-11-19, `789e361`)**: `mission_node`'s
  `main()` treats `ExternalShutdownException` (the launcher's SIGTERM) as a
  normal stop, like Ctrl-C, instead of printing a traceback. Test:
  `test/test_main_shutdown.py`. Full suite: 49/49 passing.

- **`dome_control` F22/T02 landed (2026-08-05)**: `mission_node.py` gained a
  `/mission/state` publisher (`std_msgs/String`, transient-local QoS),
  publishing `self.fsm.state.name` once at startup and again on every
  `on_intent`-driven FSM transition. Lets `dome_control`'s `robot subsystems`
  command show live mission state without its own FSM access. Tests:
  `test_mission_state_published_on_startup`,
  `test_mission_state_published_on_transition` in
  `test/test_mission_node.py`. Full suite: 47/47 passing.

- **`dome_control` coordination gap resolved (2026-08-04)**: `dome_control`'s
  F19 decided on **no automatic coordination**. `stop` stays a pure
  `dome_control` motor halt with no knowledge of this package's FSM; cancelling
  a mission goal stays this package's explicit `navigation_cancel` /
  `exploration_stop` intents. `"stop"` is intentionally not in
  `intent_parser.py`'s `NAME_TO_INTENT`. Live-verified on the Pi: no
  double-dispatch.

- **F33/TF33 started in sibling package `dome_semantic` (2026-08-02)**:
  bootstrapped as `Boston-Robot-Hackers/dome_semantic`. T01
  (`dome_semantic_msgs`), T02 (`world_tracker.py` ported from `dome_vision`)
  and T03 (`map`-frame transform + re-basing on `map→odom` jumps) done; its
  `semantic_map_node` now publishes `SemanticTargetArray` on
  `/semantic/targets`. Tracked in `dome_semantic/02-doc/current.md`.

- **dome_nav branch merge + I01 fix (2026-08-02)**: `origin/semantic-exploration`
  fast-forward-merged into `dome_nav`'s `main` at `894c799`. Same commit
  replaces `explorer_manager_node`'s racy on-demand `fetch_grid` with standing
  `start_grids`/`stop_grids` subscriptions. Not live-verified (the regression
  test never reproduced the race either before or after).

- **dome_mission `01-literate/` (2026-08-02)**: full literate doc set —
  `00-overview` + chapters for `mission_fsm` / `intent_parser` /
  `label_resolver` / `mission_node` / `mission_explore.launch.py`, plus the
  `X01-nav_intent_check` appendix.

- **TF03 T07 — explore action swap + top-level launch (2026-08-01)**: explorer
  exposes the `ExploreArea` action (dropped `/intent`); `mission_node.start_explore`
  is its client (result → FSM `on_done`). `launch/mission_explore.launch.py`
  composes dome_nav's explore stack + mission_node, gated by a `sim_mode` str
  param (not `use_sim_time` — collides with a better_launch reserved global).
  **Live-verified in sim**: `/explore_area` has 1 client (`/mission`) / 1
  server (`/explore_manager`), no stray `/intent` subs; `exploration_start`
  drove a real explore session to `DONE` (`reached: 2, failed: 0`).

- **TF03 T06 + T08 (2026-07-31)**: dome_nav deleted `nav_manager` +
  `nav_manager_node` (go-to-target now lives here); F01/TF01 and F03/TF03
  records relocated into this package; dome_nav docs updated.

- **TF03 T02–T05 (extraction from dome_nav)**: package skeleton +
  `dome_nav_msgs`; pure `mission_fsm.py` (`IDLE / EXPLORING / LOCATING /
  GOING_TO_TARGET`); `intent_parser.py` + `/intent` ownership; go-to-target via
  `label_resolver.py` (`SemanticTargetStore.resolve`, `yaw_from_quaternion`)
  and Nav2 `NavigateToPose`, with `/semantic/targets` gated on
  `schema_version`.
