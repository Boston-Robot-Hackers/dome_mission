# dome_mission — Current Session Handoff

Concise cold-start orientation. Detailed history lives in git log and the
`04-tasks/` files — do **not** re-narrate it here.

**Date:** 2026-07-31 · **Origin:** extracted from dome_nav per F35 / TF35

## Status

New package, bootstrapped 2026-07-31. Skeleton + core sequencing landed; wiring
to real action clients still open.

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

- **T07** (explore action swap + top-level launch, done 2026-07-31) — explorer
  exposes the `ExploreArea` action (dropped `/intent`); `mission_node.start_explore`
  is its client (result → FSM `on_done`). `launch/mission_explore.launch.py`
  composes dome_nav's explore stack + mission_node. Single-`/intent`-handler
  invariant now met. Live smoke confirmed `/explore_area` advertised + no
  explorer `/intent`. Full sim bring-up pending a sim host (gz can't run on this Pi).

## Open

- **T08** — docs / literate / package-list updates.
- **Live sim bring-up** (T07 ROS2-runtime tail): drive a real explore +
  go-to-label in gz on a sim host.

## Architecture essentials

- Pure/ROS split (dome_nav L0/L1): `mission_fsm.py` + `intent_parser.py` pure;
  `mission_node.py` thin ROS seam.
- Commands emitted by the FSM (`START_EXPLORE / CANCEL_EXPLORE /
  DRIVE_TO_TARGET / CANCEL_DRIVE`) are executed by the node's action clients
  (currently logged; T05/T07 wire them).
- Depends on `dome_nav_msgs` + `dome_semantic_msgs`.

## Gotchas

- Test recipe: `/usr/bin/python3 -m pytest` (PATH `python` = platformio venv, no
  numpy/ROS).
- `colcon build --packages-select dome_mission` after every source edit.
