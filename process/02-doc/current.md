# dome_mission — Current

## Open

### Pick up here (2026-11-22)

A design discussion **redefined dome_mission**: it composes primitives into
**multi-step behaviors** (patrol, explore a room, the Mapping → Discovery →
Command phases of `process/02-doc/mission.md`). It no longer owns semantic
knowledge — it will ask a semantic query interface instead.

It's captured in four parked features, none approved for code:

- **F05** — write the definition down (docs only).
- **F06** — explore with extent (draft).
- **F07** — go-to by semantic query (draft).
- **F04** — check-targets patrol.

Start with **F05**. Everything else is written against it, and most of it waits
on other repos (see **Needed from other repos**).

### Next

- **F05 (redefine dome_mission)** — Medium. Docs only, decided enough to
  start: spec, CLAUDE.md, notes, `mission.md`; mark F03 partly superseded.
- **F06 (explore with extent and capture)** — Medium, draft. Open questions
  are listed in the feature; TF06.0 settles them.
- **F07 (go-to by semantic query)** — Medium, draft. Replaces
  `label_resolver`; open questions are in the feature.
- **F04 (check-targets patrol)** — Low. Blocked on semantic-layer queries and
  a small-spin primitive.
- **F02 (typed intent status)** is parked in `deferred/` — revive it, or leave
  it parked. Its task file still names the pre-F03 `nav_manager_node`, so it
  needs re-scoping before it is picked up.

### Decisions pending

- **FSM or behavior tree?** Patrols and the phases strain the FSM;
  `py_trees_ros` is the noted candidate. Needed before F04/F06/F07 code.
- **Semantic `target` schema** (string or structured) — the semantic layer's
  call; it shapes F07's intent slot.
- **Where `spin_survey` goes** — it's leaving dome_control; might come here.
- **Two `mission_node` bugs, parked by choice**: `/mission/state` isn't
  republished after `on_done`, and a late action result can clobber a newer
  goal handle. Details are in `process/01-literate/04-mission_node.md`.
- **I03**: collapse `intent_parser.py`'s four-guard LBYL validation into one
  EAFP `try`/`except`? Two sub-questions are undecided: broad-except masking
  risk, and where the specific failure reason gets logged.

### Needed from other repos

Not dome_mission features; each is a dependency of F04/F06/F07.

- **dome_semantic**: a query interface (resolve a target to approach-pose
  candidates; list targets by filter; viewpoint per target; re-seen check).
  Also a hierarchical map with rooms (outline, name, adjacency). Check its
  existing `/describe_scene` service first.
- **dome_nav**: extent fields on `ExploreArea.Goal`. Also a map mode after
  mapping (localization vs lifelong SLAM), which resolves I02.
- **A small-spin primitive** as an action. Its home is undecided.

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
