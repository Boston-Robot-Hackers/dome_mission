# dome_mission — Current Session Handoff

Concise cold-start orientation. Detailed history lives in git log and the
`04-tasks/` files — do **not** re-narrate it here.

**Date:** 2026-11-19 · **Origin:** extracted from dome_nav per F35 / TF35

## Status

Skeleton + core sequencing + explore action swap landed and **live-verified in
sim** (2026-08-01): `/intent` → `mission_node` → `ExploreArea` → Nav2 explore
ran end-to-end (`reached: 2, failed: 0`). Go-to-label wiring is done but
untestable until F33 lands (no live semantic publisher).

**Reminder for next session**: `dome_nav`'s `main` branch predates F35/TF35 —
build it from `origin/semantic-exploration` (not merged to `main` yet), or
the explorer silently reverts to its pre-T07 `/intent` handler with no
`ExploreArea` server. See F35's How-to-Demo setup step.

Task tracking authority for the extraction is **dome_nav's `TF35-mission-layer.md`**
(the extraction task file). This package's own `03-features/` / `04-tasks/` are
for dome_mission-native work going forward.

## Done (via dome_nav TF35)

- **T02** — package skeleton + `dome_nav_msgs` (`ExploreArea` action). Builds
  clean; `mission_node` boots + idles.
- **T03** — pure `mission_fsm.py`: states `IDLE / EXPLORING / LOCATING /
  GOING_TO_TARGET`; intent + completion driven; inapplicable events are no-ops.
  Boundary decision recorded (per-goal abort stays in dome_nav watchdog).
- **T04** — `intent_parser.py` (pure JSON → Intent) + `mission_node` owns
  `/intent`, drives the FSM. Command execution stubbed to logging.
- **T05** — go-to-target. `label_resolver.py` (pure): `TargetPose` +
  `SemanticTargetStore.resolve` (nearest match, typed successor to
  `find_nearest_confirmed`) + `yaw_from_quaternion`. `mission_node` subscribes
  `SemanticTargetArray` on `/semantic/targets` (schema_version gated),
  tracks `/amcl_pose`, and on `DRIVE_TO_TARGET` resolves label → drives via Nav2
  `NavigateToPose`; missing label → `on_done(DRIVE_FAILED)`. `nav_intent_check.py`
  retargeted to typed msg, moved into `tools/`. Explore command execution still
  stubbed (T07).

45 tests pass (`/usr/bin/python3 -m pytest test/`).

- **T06** (dome_nav cleanup, done 2026-07-31) — dome_nav deleted `nav_manager`
  + `nav_manager_node` + their tests/literate; go-to-target now lives here.
  F02/TF02 records relocated into this package. Explorer keeps `/intent` until
  T07 (the `/intent`→ExploreArea swap), so two `/intent` handlers coexist for now.

- **T07** (explore action swap + top-level launch, done 2026-08-01) — explorer
  exposes the `ExploreArea` action (dropped `/intent`); `mission_node.start_explore`
  is its client (result → FSM `on_done`). `launch/mission_explore.launch.py`
  composes dome_nav's explore stack + mission_node, gated by a new `sim_mode`
  str param (not `use_sim_time` — collides with a better_launch reserved
  global). Single-`/intent`-handler invariant now met **and live-verified**:
  full sim launch on a real sim host, `/explore_area` shows 1 client
  (`/mission`) / 1 server (`/explore_manager`), no stray `/intent` subs;
  `exploration_start` drove a real explore session to `DONE` (`reached: 2,
  failed: 0`). Required building `dome_nav` from `origin/semantic-exploration`
  — its `main` predates this feature and has none of T02–T08.

- **T08** (docs/literate, done 2026-07-31) — dome_nav docs updated (current.md,
  09-explorer literate v2.0, overview, README/CLAUDE); F35/TF35 records relocated
  here as this package's founding record. TF35 T01–T08 all done.

- **dome_mission `01-literate/`** (done 2026-08-02) — full literate doc set:
  `00-overview` + chapters for `mission_fsm` / `intent_parser` /
  `label_resolver` / `mission_node` / `mission_explore.launch.py`, plus
  `X01-nav_intent_check` appendix.

- **dome_nav branch merge** (done 2026-08-02) — `origin/semantic-exploration`
  fast-forward-merged into `dome_nav`'s `main` at `894c799`; anyone building
  from `main` now gets T02–T08. Same commit also carries the **I01 fix**:
  `explorer_manager_node`'s racy on-demand `fetch_grid` (dynamic
  create/destroy of grid subscriptions, colliding with the executor's own
  wait-set rebuild) replaced by standing `start_grids`/`stop_grids`
  subscriptions, lifecycle-matched to the TF listener. Not live-verified —
  the regression test written for it never reproduced the race either
  before or after the fix — but the racy mechanism itself is gone.

- **F33/TF33 underway in a new sibling package, `dome_semantic`**
  (bootstrapped 2026-08-02, `Boston-Robot-Hackers/dome_semantic`). **T01**
  (`dome_semantic_msgs`) was already done. **T02**: `world_tracker.py` + its
  pure dependency closure ported from `dome_vision`, behavior-preserving
  (`dome_vision`'s originals untouched — its `semantic_map_node.py` is still
  the live tracker). **T03**: `map`-frame TF transform + re-basing on
  `map→odom` jumps — new logic, not a port; `dome_vision` only ever
  transformed to `odom` and had no re-basing at all. 110 tests pass. **T04**
  (typed `/semantic/targets` publishing) is next — that's what unblocks
  go-to-label live-verify below. See `dome_semantic/02-doc/current.md` and
  its "Watch list" note in `notes.md` (four not-done `dome_vision` features
  target the same ported code and stay `dome_vision`'s concern until its
  originals are deleted).

## Open

- **dome2 F05 (launch-file cleanup)**: TF05.2 skipped this package.
  `launch/mission_explore.launch.py` is a known exception to the two-level
  launch convention (it includes `dome_nav`, and DOME packages may not
  include each other) and is blocked on `dome_nav` I13 (Nav2 params not yet
  migrated to Kilted). It still has to be split or moved to dome2 once I13
  lands. See `dome2/process/03-features/notdone/F05-launch-file-cleanup.md`.
- **I01 still in `05-issues/open/`** even though the fix landed in
  `dome_nav` `894c799`. It isn't live-verified; close it once it is.
- **I02** (`05-issues/open/`): the explore/sim launch stack has no `amcl` —
  `mission_node`'s `/amcl_pose` subscription has zero publishers there, so
  go-to-label has no live pose even once F33 lands. Needs a localization-mode
  handoff after explore that doesn't exist yet.
- **I03** (`05-issues/open/`): `intent_parser.py`'s four-guard LBYL
  validation could collapse to a single EAFP `try`/`except`, but two open
  sub-questions (broad-except masking risk; where a more specific failure
  reason should be logged) are undecided — no code touched yet.
- **Go-to-label not live-verified yet**: `dome_semantic`'s
  `semantic_map_node` now publishes `SemanticTargetArray` on
  `/semantic/targets`, so the producer exists. The remaining blockers are I02
  (no live `/amcl_pose`) and the Nav2 stack being blocked on `dome_nav` I13.
  The explore leg is verified; go-to-label is blocked, not broken.
- **Non-blocking noise**: slam_toolbox's legacy `.pgm`/`.yaml` map export
  intermittently fails (`dome_nav/slam_manager_node.py:161-176`, "Failed to
  spin map subscription" → `result=255` `WARNING`). Pose graph save (the real
  persisted SLAM state) is unaffected. Not fixed; dome_nav's to pick up if the
  legacy artifact is ever needed.
Newly-completed items are recorded in `02-doc/history.md`, not here.

## Architecture essentials

- Pure/ROS split (dome_nav L0/L1): `mission_fsm.py` + `intent_parser.py` pure;
  `mission_node.py` thin ROS seam.
- Commands emitted by the FSM (`START_EXPLORE / CANCEL_EXPLORE /
  DRIVE_TO_TARGET / CANCEL_DRIVE`) are executed by the node's action clients
  (`ExploreArea` for explore, Nav2 `NavigateToPose` for drive-to-target; wired
  by T05/T07).
- Depends on `dome_nav_msgs` + `dome_semantic_msgs`.

## Gotchas

- Test recipe: `/usr/bin/python3 -m pytest` (PATH `python` = platformio venv, no
  numpy/ROS).
- `colcon build --packages-select dome_mission` after every source edit.
- `ruff` isn't preinstalled; `python3 -m pip install --user --break-system-packages
  ruff`. Repo config is `ruff.toml` (ignores `EXE001` — style guide mandates
  the shebang on every `.py` regardless of executable bit).
