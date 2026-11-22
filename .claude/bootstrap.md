# Bootstrap Scaffold

When bootstrapping a new project, assume that you are inside the directory of the target. Check .claude folder is there and correct. Then create the following files and folders exactly as specified below.

## Folder structure to create

```
LICENSE
README.md
.gitignore
ruff.toml
CLAUDE.md
process/
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
```
### process/*/template.md
Copy `.claude/templates/feature_template.md` to `process/03-features/template.md`,
`task_template.md` to `process/04-tasks/template.md`, and `issue_template.md` to
`process/05-issues/template.md`, each as-is.

### LICENSE
Copy from `.claude/templates/LICENSE.template` and replace `<YEAR>` and `<AUTHOR NAME>`.

### README.md
Copy from `.claude/templates/README.md.template` and replace `<APP NAME>` and other placeholders.

### .gitignore
Copy from `.claude/templates/.gitignore.template` as-is.

### ruff.toml
Copy from `.claude/templates/ruff.toml.template` as-is. This carries over the
calibrated ruff rule set mapped to `.claude/style_guide.md`'s checklist (see
the `[ruff: CODE]` markers in that file). Once the new project has real code,
recalibrate `select` and the `[lint.pylint]` thresholds against what
`ruff check` actually finds there — the template comments explain what to
drop and why.

### CLAUDE.md
Copy from `.claude/templates/CLAUDE.md.template` and replace `<APP NAME>`.

### Makefile
Copy from `.claude/templates/Makefile.template` and replace `<APP NAME>` in
the header comment. It starts with only `help` (the default target); user-facing
tool targets are added as features land. Development commands (`uv sync`,
`uv run pytest`, `uv run ruff`) are listed in CLAUDE.md's `## Commands`; add
Makefile targets for them only when something needs them. See the Makefile
rules in `.claude/style_guide.md`.

### .githooks/pre-commit
Copy from `.claude/templates/pre-commit.template` as-is, then
`chmod +x .githooks/pre-commit`. It stamps `Version`/`Created`/`Updated` into
the header of every staged `.py`, as required by the file-header rule in
`.claude/style_guide.md`.

Git will not use it until the repo is pointed at the directory — see step 1 of
"After scaffolding". `.git/hooks` is not version controlled, which is why the
hook is tracked here instead.

## After scaffolding

Prompt the user to:
1. Activate the header-stamping hook — a one-time local config, needed once per
   clone, that nothing else will do automatically:

   ```bash
   git config core.hooksPath .githooks
   ```

   Without it the hook is inert and headers silently stop updating, with no
   error to notice.
2. Fill in `process/02-doc/spec.md` with the app description
3. Initialize `process/02-doc/current.md` as the session handoff file — just
   an `## Open` section starting with `### Pick up here (YYYY-MM-DD)`, shaped
   and size-limited as `.claude/process.md`'s *current.md* rules say
4. Create `process/02-doc/history.md` with a one-line header (e.g. "# History")
   — it starts empty and only grows as work is marked done
5. Add any durable architecture notes to `process/02-doc/notes.md`
6. Replace `<APP NAME>` in `CLAUDE.md`, `README.md`, `Makefile`, and `LICENSE`
   with the actual app name, author, and year
7. Fill in `settings.json`'s `autoMode.environment` block with the real project
   purpose, package manager, the `uv run pytest` / `make help` commands, and source
   control location
8. Define the first feature and matching task file before writing any code
