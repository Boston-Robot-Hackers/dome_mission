# F05 — Redefine dome_mission as the Multi-Step Behavior Layer

**Priority**: Medium

**Date Created:** 2026-11-22

**Done:** no

**Tasks File Created:** yes

**Tests Written:** no

**Test Passing:** no

**Description**: Write down the new definition of dome_mission agreed on
2026-11-22, and the package boundaries that go with it. **Docs only — no code.**
F04, F06 and F07 are written against this definition.

## The definition

> dome_mission **composes primitives into multi-step behaviors** — patrol the
> house, explore a room, the *Mapping → Discovery → Command* phases of
> `process/02-doc/mission.md`. It owns `/intent` and the mission state, and
> decides which behavior runs, when it starts, and when it is done.

It composes capabilities it does not implement:

- **explore/map** — dome_nav;
- **navigate to a pose** — Nav2;
- **semantic query** — the semantic layer (dome_semantic, or its successor);
- other primitives as they appear (e.g. a small spin).

## Key decisions

- **No English parsing.** Intents arrive already parsed, probably by an LLM
  upstream.
- **Object references are opaque.** dome_mission passes a `target` through to
  the semantic layer without looking inside. The **semantic layer owns its
  schema** (string or structured — decided there, not here).
- **No copy of the semantic map.** dome_mission asks a query interface instead of
  subscribing to and storing targets.
- **Map maintenance is not dome_mission's.** Localization vs lifelong SLAM is
  dome_nav's mode; dome_mission at most requests one.
- **Primitives don't live here.** dome_mission sequences them; the
  `spin_survey` code leaving dome_control may or may not come here.

## What it supersedes

F03's settled point that **dome_mission holds all go-to-label / semantic
knowledge**. The rest of F03 stands: dome_nav is primitives only, transport is
ROS actions, drive-to-pose goes to Nav2 directly.

## Boundaries

| Package | Owns |
|---|---|
| dome_control | operator surface: CLI, safety halt; publishes `/intent` |
| dome_mission | multi-step behaviors: sequencing, stop conditions, policy |
| dome_nav | moving, mapping, localizing; explore within an extent |
| semantic layer | building the semantic map (incl. rooms) and answering queries |

## Out of scope

Any code change. Removing `label_resolver` is F07.

## How to Demo

**Setup**: none.

**Steps**:
1. Read `process/02-doc/spec.md`, `CLAUDE.md`, and `process/02-doc/notes.md`.

**Expected output**: all three state the definition above, consistently; F03
is marked as partly superseded; `mission.md` is reconciled with it.

## Process Gate

After creating this feature file and the corresponding task file, **stop and present the plan to the user**. Do not write any code or content until the user gives explicit approval to proceed.
