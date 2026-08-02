# I03 intent_parser.py's validation could be simpler — open design question

* **What the symptom is**: not a bug — `parse_intent`
  (`dome_mission/intent_parser.py:43-61`) is ~53% validation code: four
  separate `LBYL`-style guards (bad JSON, wrong top-level shape, unknown
  `name`, wrong `slots` shape), each an explicit `isinstance`/`is None`
  check plus a `return None`. Discussed as a simplification candidate: an
  `EAFP`-style single `try`/`except (json.JSONDecodeError, TypeError,
  KeyError, AttributeError): return None` around the happy path would cut
  this to roughly 12 lines from 19, with identical external behavior
  (still returns `None` uniformly on any malformed input, still never
  raises out to the caller).
* **What tests have already been done**: none — this is an open design
  discussion, not yet a decided change. No code has been touched.
* **What the latest theory is**: two open sub-questions before making this
  change:
  1. **Broad-except risk**: a single `try` wrapping the whole happy path
     (JSON parse, dict lookup, `ParsedIntent` construction) would also
     catch a genuine bug accidentally introduced later inside that block
     (e.g. a typo'd attribute access) and misreport it identically to
     "malformed input," where the current four explicit guards each only
     fire on the exact condition they check. Worth weighing before
     adopting the terser form.
  2. **Where should the log line live?** `mission_node.on_intent` already
     logs a `WARNING` whenever `parse_intent` returns `None` — nothing is
     silently swallowed today. But that log is generic ("Malformed or
     unknown intent: ...") since `parse_intent` doesn't currently expose
     *why* parsing failed. Moving a more specific log inside
     `parse_intent` itself would need Python's stdlib `logging` module
     (not `rclpy`'s `self.get_logger()`) to preserve the module's
     deliberate ROS-free/pure-and-unit-testable design
     (`intent_parser.py`'s own docstring) — but stdlib-logged output
     wouldn't appear on `/rosout` the way `mission_node`'s own logging
     does, which may or may not matter for how this gets debugged live.
  Not decided: whether to (a) leave the four explicit guards as-is, (b)
  switch to the single broad `except` and accept the masking risk, or
  (c) do (b) but also thread through a more specific reason string so
  `mission_node`'s existing call-site log can be more useful without
  moving logging into the pure module at all.
