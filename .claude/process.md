# General
* No code without a task; no task without a feature; no feature contradicting the spec.
* After creating a feature + task file, stop and present the plan — no code until approved.
* An unapproved feature parked after that stop does not block unrelated work elsewhere in the project — it just sits in `notdone/` until it's explicitly picked up.
* Don't close a feature until its full test suite exists and passes.
* Exception: simple bug fixes/refactors (no spec/behavior change) skip the feature/task pair — log as a chore.
* Any bug fix or regression gets a test.
* Switching between task/feature/chore: stop and ask permission first.
* Fix visible, low-risk follow-on inconsistencies from a change in the same pass — an unfilled template placeholder, a stale cross-reference, mismatched numbering — rather than pausing to ask permission for each one separately.

# current.md
* `process/02-doc/current.md` is read at every session start, so its size costs every session. Budget: **about 8 KB / 150 lines**.
* It holds only `## Open`. The first subsection is `### Pick up here (YYYY-MM-DD)`: the latest session's handoff, replaced each checkpoint. The SessionStart hook prints only that subsection.
* After it, grouped lists of what is still open, one or two lines per item, e.g. `### Next`, `### Waiting on people`, `### Decisions pending`, `### Chores`, `### Blocked`, `### Open issues`.
* Done → `history.md` (newest first). Durable facts (how things work, hazards, commands, architecture) → `notes.md`. Detail lives in feature, task and issue files; current.md points to them.
* Hazards that must be known before *any* edit go in CLAUDE.md, which is always loaded, not in current.md or notes.md.

# chores
* One running file, `process/04-tasks/chores.md`: `- [ ] <what and why>` → `- [x]` when applied.

# features
* `FNN-<slug>.md` in `process/03-features/{notdone,done,deferred}/`; a mini-spec — scope/intent, not task detail.
* `Tasks File Created: yes` only once a matching `process/04-tasks/TFNN-*.md` exists. `template.md` shows the format.
* `Date Created:` in the header, absolute ISO `YYYY-MM-DD`, set when the file is first written and never changed afterwards — not even when the feature moves between `notdone`/`done`/`deferred`.

# tasks
* Full task list before any design/code. `TFNN-<slug>.md` (`NN` matches the feature) in `process/04-tasks/{notdone,done,deferred}/`; `template.md` shows the format.
* Each step is numbered `TFNN.N`, matching the file's own `TFNN` (e.g. `TF03.0`, `TF03.1`, ...), starting at `.0` — not a bare `T0N`.
* `Date Created:` in the header, absolute ISO `YYYY-MM-DD`, set when the file is first written and never changed afterwards. It is the task file's own creation date, which may be later than its feature's.
* Every step gets a test where feasible (else record why); every feature gets a dedicated test-writing task.
* Task lists must never include a "regenerate literate docs" task — literate docs are refreshed later, at checkpoint, not as part of a feature's task list.
* Last task done → move the task file to `done/`, set the feature's Done/Tests Written/Test Passing to yes, move the feature file to `done/`.
* A repo-wide convention change (a new required header field, a renumbering scheme) applies retroactively to `done/`-archived feature and task files too, not just active `notdone/` ones, so the whole history stays on one convention.

# issues
* `process/05-issues/{open,closed,deferred}/`, numbered, follow the template.
* New → `open/`; resolved or absorbed into a feature/task → `closed/`; explicitly deferred → `deferred/`.

# writing .md files
* Applies to `process/03-features/`, `process/04-tasks/`, `process/05-issues/`, and any hand-written doc — not `process/01-literate/` (own prompt in `literate.md`).
* Blank line between paragraphs, always. Short paragraphs; bullets for anything enumerable; **bold** for key decisions; *italics* for emphasis or naming a pattern. Several short, headed subsections beat one block.
* Applies every time a file is rewritten, not just on first authoring.
* Applies everywhere I write markdown in this project, even if this project's own copy of `.claude/` predates or omits a rule the canonical `j3` kit has since gained — a stale local copy is not license to write worse markdown.

# agent model selection
* Default subagent dispatch to haiku; upgrade only when the task needs judgment, not just data-gathering.
* **haiku** — file/log discovery, "where is X defined", dependency-closure scans, counting, formatting. Use the `explorer` agent (`.claude/agents/explorer.md`).
* **sonnet** — analysis, code review, writing, moderate reasoning, synthesis across subagent findings. Use the `reviewer` agent (`.claude/agents/reviewer.md`).
* **opus** — architecture decisions, novel debugging, cross-cutting design tradeoffs. Use the `architect` agent (`.claude/agents/architect.md`).

# bootstrap
* `.claude/bootstrap.md` is the scaffold spec. Run `/bootstrap` to bootstrap a new project — don't follow it ad hoc from a mention in conversation.
* Never copy `settings.local.json` when copying `.claude/` into a new project — it's machine-local and gitignored, and its permission entries (paths, per-machine allowances) don't generalize.
* If a project's `.claude/` predates the canonical `j3` kit's current state, flag it as stale and offer to sync, rather than silently working from the old copy.

# github
* Literate docs: apply `.claude/literate.md`'s prompt to each changed source module (Python, JavaScript, or other), save as `process/01-literate/<module>.md`.
* Run tests and regenerate literate docs before committing/pushing.
* File headers stamp themselves: `.githooks/pre-commit` sets `Version`/`Created`/`Updated` on every staged `.py`. Never hand-edit those three fields — see the file-header rule in `.claude/style_guide.md`.
* The hook is only active once per clone: `git config core.hooksPath .githooks`. Without it headers silently stop updating, so check it after cloning.
* **No pull requests.** Single-developer repo: run the tests, commit, push. No review branch, no PR.
* That sequence belongs to `/checkpoint`, which runs tests and ruff, updates `current.md`, refreshes changed literate docs, then commits and pushes. Prefer it over doing the steps by hand.
* Commit or push only when asked, with a good message.
* **Changelog** (projects with a `CHANGELOG.txt`): before every checkpoint or push, propose one line (newest first, `YYYY-MM-DD  one sentence`), or say why none is needed. The user approves or rewrites it. Nothing goes in the file without that approval. Unattended scheduled jobs are exempt. CLAUDE.md says who the sentence is written for.
