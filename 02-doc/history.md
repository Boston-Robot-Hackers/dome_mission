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
