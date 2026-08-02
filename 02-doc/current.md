# dome_mission — Current Session Handoff

Concise cold-start orientation. Detailed history lives in git log and the
`04-tasks/` files — do **not** re-narrate it here.

**Date:** 2026-08-01 · **Origin:** extracted from dome_nav per F35 / TF35

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

## Open

- **dome_nav branch merge**: `origin/semantic-exploration` (has T02–T08,
  including T07's `ExploreArea` server) is still unmerged into `dome_nav`'s
  `main`. Not dome_mission's to fix, but blocks anyone building from `main`.
- **dome_mission literate**: `mission_fsm` / `intent_parser` / `label_resolver` /
  `mission_node` have no `01-literate/` yet — a native dome_mission task.
- **Upstream blocker for live go-to-label**: F33/TF33 (dome_semantic pkg +
  dome_vision publisher of `/semantic/targets`) is uncoded; `/semantic/targets`
  has 0 publishers. Explore leg is verified; go-to-label leg is not (blocked,
  not broken).
- **Non-blocking noise**: slam_toolbox's legacy `.pgm`/`.yaml` map export
  intermittently fails (`dome_nav/slam_manager_node.py:161-176`, "Failed to
  spin map subscription" → `result=255` `WARNING`). Pose graph save (the real
  persisted SLAM state) is unaffected. Not fixed; dome_nav's to pick up if the
  legacy artifact is ever needed.

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
