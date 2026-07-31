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

33 tests pass (`/usr/bin/python3 -m pytest test/`).

## Open

- **T05** — go-to-target: subscribe `SemanticTargetArray`, resolve label → pose
  (typed, incl. yaw), issue `NavigateToPose`. Kills schemaless JSON.
- **T06** — dome_nav cleanup: remove `/intent` + label logic from dome_nav
  (`explorer_manager_node`, `nav_manager`). Completes the single-`/intent`-handler
  invariant (until then, running both double-handles `/intent`).
- **T07** — top-level launch composing the TF33 sub-stack + dome_mission.
- **T08** — docs / literate / package-list updates.

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
