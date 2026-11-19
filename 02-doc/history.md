# History — dome_mission

Newly-completed items moved out of `current.md`'s `## Open` section, per
checkpoint policy.

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

- **Clean stop on launch shutdown (2026-11-19, `789e361`)**: `mission_node`'s
  `main()` treats `ExternalShutdownException` (the launcher's SIGTERM) as a
  normal stop, like Ctrl-C, instead of printing a traceback. Test:
  `test/test_main_shutdown.py`. Full suite: 49/49 passing.
