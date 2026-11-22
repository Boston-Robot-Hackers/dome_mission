# I01 Explore session intermittently crashes explorer_manager_node

* **Symptom**: during a live sim `ExploreArea` session (`dome_nav`,
  `explorer_manager_node.py`), the node crashed and exited right as it
  reached "frontier exhaustion" (`NO_TARGETS_BLOCKED` completion path,
  `explorer_manager_node.py:497-512`). Traceback: `execute_explore`
  (`explorer_manager_node.py:304`) reached `goal_handle.abort()` —
  reachable only when its `while rclpy.ok():` loop
  (`explorer_manager_node.py:294-304`) exits because `rclpy.ok()` turned
  `False`, not through the normal `goal_handle.succeed()` return a few
  lines above. `goal_handle.abort()` then raised
  `RCLError: Failed get goal status array: feedback publisher is invalid`,
  which cascaded into `InvalidHandle: cannot use Destroyable because
  destruction was requested` in the main spin loop. Process exited; no
  `ExploreArea` result was ever sent to the client. On `dome_mission`'s
  side, `mission_node` survived but was left with an in-flight goal that
  will never resolve (`/explore_area` showed 1 client, 0 servers
  afterward) — `mission_node`'s FSM robustness against a server dying
  mid-goal is untested and likely needs a watchdog/timeout, tracked
  separately from this issue.
* **What tests have already been done**: reproduced live on the sim host
  (`semantic-exploration` branch, `simple_room` world) on 2026-08-02, not
  during a manual Ctrl-C or window close (confirmed with the user — no
  external interruption). Originally suspected specific to the
  `NO_TARGETS_BLOCKED`/patience-exhaustion completion branch
  (`explorer_manager_node.py:497-512`), based on the `FRONTIER EXHAUSTION`
  diagnostic banner appearing just before the crash. **Correction (same
  day, later run)**: a subsequent clean run hit the exact same log
  signature — `Goal #1`/`Goal #2` both reached, then
  `"Algorithm reports exploration complete."` (the *other* branch,
  `EXPLORED_DONE` at line 475-480) — followed by the identical-looking
  `FRONTIER EXHAUSTION — 0 raw clusters, patience=14` banner, and
  completed with no crash (`reached: 2, failed: 0`, `explorer_manager`
  still alive afterward). The banner is printed by `dump_exhaustion()`,
  called from *both* completion branches (lines 477 and 510) — its
  `patience=14` is a printed constant, not evidence of which branch fired.
  So the crash is **not** reliably tied to a specific completion branch;
  both branches have now been observed to complete cleanly, and only one
  (as yet unreproduced-on-demand) run crashed.
  **Second reproduction (same day, `multi_room` world)**: crashed again,
  identical signature (`execute_explore` → `goal_handle.abort()` at
  `explorer_manager_node.py:304` → the same `RCLError`/`InvalidHandle`
  cascade), but this time immediately after `"Goal #4 REACHED"` —
  **no** `FRONTIER EXHAUSTION`/`"Algorithm reports..."` message appeared
  before it at all. So this isn't session-completion-specific either; it
  can fire mid-session, between one goal's success and frontier
  reselection for the next. Confirmed on a second, larger/more complex
  world (`multi_room` vs `simple_room`), so it's not `simple_room`-specific.
  Same post-crash signature as before: `explorer_manager` process gone,
  `mission_node` survives with `/explore_area` at 1 client/0 servers.
* **Latest theory**: not completion-specific at all — the second
  reproduction fired mid-session, right after a goal-reached transition,
  before any completion/exhaustion check ran. That points more generally
  at an intermittent race between the 1Hz `explore_tick` timer callback
  and the blocking `execute_explore` goal callback, which run concurrently
  under a shared `MultiThreadedExecutor` + reentrant callback group
  (`explorer_manager_node.py:736-737`) — plausibly more likely right
  around a goal transition (new frontier selection, more state mutation
  per tick) than during a steady "still driving" tick, which would fit
  both observed crash points (session end, and a goal-reached moment).
  Neither completion path calls `rclpy.shutdown()` or raises directly, and
  `main()` (`explorer_manager_node.py:732-753`) only exits its spin loop
  on `KeyboardInterrupt` — so something inside that race is triggering
  node-context shutdown, timing-dependent enough that it hasn't reproduced
  on every run (2 crashes out of 4 observed sessions today, across two
  different worlds). Not investigated further this session; `dome_nav`'s
  to fix, not `dome_mission`'s.
