# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

Read and follow all rules in the `.claude/` folder:
- @.claude/process.md — development workflow, feature/task tracking rules, and
  agent model selection
- `process/02-doc/current.md` — session handoff; only the `## Open` section
  matters for new work, see `process/02-doc/history.md` for the completed-work
  log
- `process/02-doc/notes.md` — semi-permanent project notes

Before writing or reviewing code, read and follow `.claude/style_guide.md`
(coding standards, style rules, and review checklist) — apply it yourself
before committing; do not substitute a generic/plugin review for it.

We are developing dome_mission, **the DOME robot's brain** (F05). It is the
only node meant to consume `/intent`, and it alone owns what the robot is doing
now. It runs behaviors by calling motion actions in sequence: dome_nav's
`ExploreArea` (in `dome_nav_msgs`), and Nav2's `NavigateToPose`, `Spin` and
`DriveOnHeading`. It keeps a local copy of the semantic map from
`/semantic/targets` (`dome_semantic_msgs`) for label → pose, so dome_nav stays
primitives-only. It publishes no `/cmd_vel` and builds no world model. Package
roles and the "where does new code go" test are in `process/02-doc/spec.md`.

All process files live under `process/`: literate docs in
`process/01-literate/`, project docs in `process/02-doc/`, features in
`process/03-features/`, tasks in `process/04-tasks/`, issues in
`process/05-issues/`, and the spec at `process/02-doc/spec.md`.

## Sibling packages

- **dome_control**: the operator surface (CLI, status display, process
  management). Its `behavior_manager_node` still subscribes to `/intent` for
  `stop`, the turns and the queries, until F08 merges it here.
- **dome_semantic**: the world model. It publishes `/semantic/targets` and
  serves `/describe_scene`.
- **Nav2**: `NavigateToPose`, and the behavior server's `Spin` and
  `DriveOnHeading`.
- **dome_nav** — navigation/SLAM primitives (explorer, slam_manager). Exposes
  the `ExploreArea` action; no mission or semantic knowledge.
- **dome_nav_msgs** — `ExploreArea.action` (ament_cmake interface package).
- **dome_semantic_msgs** — `SemanticTarget` / `SemanticTargetArray` messages.

## Commands

This is a ROS 2 ament_python package, not a `uv` project; there is no Makefile.

- Build: `colcon build --packages-select dome_mission` (from the workspace root)
- Tests: `/usr/bin/python3 -m pytest test/`
- Lint: `ruff format` / `ruff check` on changed files only, never the whole repo
  (config in `ruff.toml`)

## Session Start

At session start, read `process/02-doc/current.md`'s `## Open` section for status and
next steps. If it is unreadable, fall back to `git log --oneline -15` and say
so. (The `/start` skill already does this in more depth — use it when
available; this is the fallback.)

## Workflow & Approval Gates

Do not run tests, commits, or multi-file changes until the user has explicitly
approved the plan. Present the plan, wait for "go", then execute. Never jump ahead
of a process gate.

- **Stuck-loop rule**: if the same tool call fails or returns unchanged output
  twice, stop retrying. Report the failure, what was tried, and a proposed
  workaround (e.g. `cat` via Bash instead of Read), then wait for direction.

## Accuracy Rules

Never state a fact about the environment (model backend, Docker availability,
schema semantics, file existence) from naming conventions or inference. Read the
config/file first, then state the finding and cite the source. If you cannot
verify, say "unverified" explicitly.

## Environment & Data Access

This checkout may not include required credentials or data files. Before any
live external-system or data-extract work, check for these and stop with a
short list of what's missing instead of improvising.

## Hazards before any edit

- **Test interpreter**: use `/usr/bin/python3` — the PATH `python` is a
  platformio venv without numpy/ROS (inherited from the dome_nav workspace).
- **Copy-install**: rebuild with `colcon build --packages-select dome_mission`
  after every source edit (not symlink-install), or the running node is stale.
- **Header hook**: `.githooks/pre-commit` stamps `Version`/`Created`/`Updated`;
  each clone needs `git config core.hooksPath .githooks` once.

## Write Safety

Treat any live external system (database, API, SaaS platform) as read-only by
default. Do not write, update, or delete data through a live integration
unless the user has explicitly approved it. If the project has a dedicated
read-only client/wrapper, use it exclusively — do not construct or reach
through to the raw client elsewhere. If a task seems to need a write, stop
and ask; it is rarely the right default.

## Tone

No flattery, no praise openers ("Great question!", "You're absolutely right").
Lead with the answer or the finding. Be direct and terse.
