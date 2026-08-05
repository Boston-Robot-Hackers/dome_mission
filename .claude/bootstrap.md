# Bootstrap Scaffold

When bootstrapping a new project, assume that you are inside the directory of the target. Check .claude folder is there and correct. Then create the following files and folders exactly as specified below.

## Folder structure to create

```
LICENSE
README.md
.gitignore
CLAUDE.md
01-literate/
02-doc/
  spec.md
  current.md
  history.md
  notes.md
03-features/
  notdone/
  done/
  deferred/
  template.md
04-tasks/
  notdone/
  done/
  deferred/
  chores.md
  template.md
05-issues/
  open/
  closed/
  deferred/
  template.md
run.bash
```
### LICENSE
Copy from `.claude/templates/LICENSE.template` and replace `<YEAR>` and `<AUTHOR NAME>`.

### README.md
Copy from `.claude/templates/README.md.template` and replace `<APP NAME>` and other placeholders.

### .gitignore
Copy from `.claude/templates/.gitignore.template` as-is.

### CLAUDE.md
```
# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

Read and follow all rules in the `.claude/` folder:
- @.claude/process.md — development workflow and feature/task tracking rules
- `02-doc/current.md` — session handoff; only the `## Open` section matters for
  new work, see `02-doc/history.md` for the completed-work log
- `02-doc/notes.md` — semi-permanent project notes

Before writing or reviewing code, read and follow `.claude/style_guide.md`
(coding standards, style rules, and review checklist) — apply it yourself
before committing; do not substitute a generic/plugin review for it.

We are developing an app called <APP NAME>. Literate docs are in `01-literate/`,
project docs are in `02-doc/`, features are in `03-features/`, tasks are in
`04-tasks/`, issues are in `05-issues/`, and the spec is in `02-doc/spec.md`.

## Agent model selection

Default subagent dispatches to haiku; upgrade only when the task needs
judgment, not just data-gathering:
- **haiku** — file/log discovery, "where is X defined", dependency-closure
  scans, counting, formatting. Use the `Explore` agent type for this.
- **sonnet** — analysis, code review, writing, moderate reasoning, synthesis
  across subagent findings.
- **opus** — architecture decisions, novel debugging, cross-cutting design
  tradeoffs.
```

### run.bash
Executable shell script containing the app's run command; set executable with `chmod +x run.bash`.

## After scaffolding

Prompt the user to:
1. Fill in `02-doc/spec.md` with the app description
2. Initialize `02-doc/current.md` as the session handoff file — keep it to just
   an `## Open` section (what's in progress/next); when work is marked done,
   move that entry out of `current.md` into `02-doc/history.md` rather than
   letting it accumulate in the always-read file
3. Create `02-doc/history.md` with a one-line header (e.g. "# History") — it
   starts empty and only grows as work is marked done
4. Add any durable architecture notes to `02-doc/notes.md`
5. Replace `<APP NAME>` in `CLAUDE.md`, `README.md`, and `LICENSE` with the actual app name, author, and year
6. Define the first feature and matching task file before writing any code
