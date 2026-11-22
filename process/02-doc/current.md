# dome_mission — Current

## Open

### Pick up here (2026-11-22)

`.claude/` was synced to the j3 kit this session, and the process folders moved
under `process/`. No feature or task is in progress; `notdone/` is empty.

Pick the next piece of work from **Next** below. The go-to-label path is
blocked, not broken (see **Blocked**).

### Next

- **F08 (typed intent status)** is parked in `deferred/` — revive it, or leave
  it parked. Its task file still names the pre-F35 `nav_manager_node`, so it
  needs re-scoping before it is picked up.

### Decisions pending

- **I03**: collapse `intent_parser.py`'s four-guard LBYL validation into one
  EAFP `try`/`except`? Two sub-questions are undecided: broad-except masking
  risk, and where the specific failure reason gets logged.

### Blocked

- **Go-to-label live-verify**: the producer exists (`dome_semantic` publishes
  `/semantic/targets`). Still blocked on I02 (no live `/amcl_pose`) and on
  `dome_nav` I13 (Nav2 params not migrated to Kilted).
- **dome2 F05 (launch-file cleanup)**: `launch/mission_explore.launch.py`
  includes `dome_nav`, which the two-level launch convention forbids. Split it
  or move it to dome2 once `dome_nav` I13 lands. See
  `dome2/process/03-features/notdone/F05-launch-file-cleanup.md`.

### Open issues

- **I01**: the explore-manager crash fix landed in `dome_nav` `894c799` but
  isn't live-verified. Close it once it is.
- **I02**: the explore/sim stack has no `amcl`, so `/amcl_pose` has no
  publisher. Needs a localization-mode handoff after explore.
- **I03**: see **Decisions pending**.

### Non-blocking noise

- slam_toolbox's legacy `.pgm`/`.yaml` map export intermittently fails
  (`dome_nav/slam_manager_node.py:161-176`, `result=255` `WARNING`). The pose
  graph save is unaffected. It's dome_nav's to fix if anyone needs the legacy
  file.
