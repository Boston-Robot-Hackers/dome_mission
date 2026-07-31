# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

Read and follow all rules in the `.claude/` folder:
- `.claude/process.md` — development workflow and feature/task tracking rules
- `.claude/style_guide.md` — coding standards, style rules, and review checklist
- `02-doc/current.md` — session handoff and current status
- `02-doc/notes.md` — semi-permanent project notes

We are developing dome_mission, the mission-sequencing layer for the DOME robot.
It owns `/intent` and drives a pure mission FSM that composes dome_nav
primitives (`ExploreArea` action, in `dome_nav_msgs`) and Nav2 `NavigateToPose`.
dome_mission holds all go-to-label / semantic knowledge (via `dome_semantic_msgs`)
so dome_nav stays primitives-only (F35).

Literate docs are in `01-literate/`, project docs are in `02-doc/`, features are
in `03-features/`, tasks are in `04-tasks/`, issues are in `05-issues/`, and the
spec is in `02-doc/spec.md`.

## Sibling packages

- **dome_nav** — navigation/SLAM primitives (explorer, slam_manager). Exposes
  the `ExploreArea` action; no mission or semantic knowledge.
- **dome_nav_msgs** — `ExploreArea.action` (ament_cmake interface package).
- **dome_semantic_msgs** — `SemanticTarget` / `SemanticTargetArray` messages.

## Gotchas

- **Test recipe**: use `/usr/bin/python3 -m pytest test/` — the PATH `python` is
  a platformio venv without numpy/ROS (inherited from the dome_nav workspace).
- **Copy-install**: `colcon build --packages-select dome_mission` after every
  source edit (not symlink-install).
