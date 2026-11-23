# dome_mission — Current

## Open

### Pick up here (2026-11-23)

**F05 closed**: dome_mission is **the single brain**, the only `/intent`
consumer. The package roles and the "where does new code go" test are in
`process/02-doc/spec.md`.

Two features are ready to pick up, neither approved for code yet:

- **F07 (go-to approach pose)**: small, testable now. F04 reuses its function.
- **F08 (merge the brain)**: moves `behavior_manager`'s intents in and fixes
  the uncoordinated `stop`.

### Next

- **F08 (merge the brain)**: Medium, parked. Moves `behavior_manager_node`'s
  intents into dome_mission; fixes the uncoordinated `stop`.
- **F04 (check-targets patrol)**: Low. No longer blocked except for the live
  demo (I02).
- **F06 (explore with extent and capture)**: Medium, draft. Needs dome_nav's
  extent fields.
- **F07 (go-to approach pose)**: Medium. Small, testable now, no other-repo
  dependency. F04 reuses its function.
- **F02 (typed intent status)** is parked in `deferred/`. Its task file names
  the pre-F03 `nav_manager_node`, so it needs re-scoping before it is picked up.

### Decisions pending

- **`spin_survey`**: retire it, or re-express it as `Nav2 Spin` goals.
  *Unverified* whether pause-and-capture fits.
- **I03**: collapse `intent_parser.py`'s four-guard LBYL validation into one
  EAFP `try`/`except`? Two sub-questions are open: broad-except masking risk,
  and where the specific failure reason gets logged.

The two parked `mission_node` bugs (state not republished after `on_done`, a
late result clobbering a newer goal handle) are now TF08.2 and TF08.5.

### Needed from other repos

Not dome_mission features.

- **dome_control**: after F08, delete `behavior_manager_node`, its behaviors
  and its launch entry. Retire F19's split table, and point
  `control-architecture.md`'s "brain" at dome_mission.
- **dome_nav**: extent fields on `ExploreArea.Goal` (F06). Also a map mode
  after mapping (localization vs lifelong SLAM), which resolves I02.
- **dome_semantic**: nothing new required. A hierarchical map with rooms waits
  until a behavior needs it.

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
