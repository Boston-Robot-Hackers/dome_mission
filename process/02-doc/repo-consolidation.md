# Consolidating the dome_* repos into one

**Status**: plan liked, **not started** (2026-11-23). This applies to the whole
workspace; it is written here because the analysis happened in dome_mission.

## Why

The process has a fixed cost per repo: current.md, history, notes, spec, a
`.claude/` copy (about 1,100 lines × 10 repos), the hook and the templates.
Measured on 2026-11-23 from git history:

- About **⅔ of all churn is markdown**, and about **half of all commits touch
  no `.py`**.
- **Small repos are worst.** dome_mission's churn is 85% markdown, dome_pad's
  76%.
- **About 60 commits are process maintenance**: kit syncs, renumbering,
  convention changes applied in every repo.
- **Cross-repo work is costly.** Every cross-package feature needs feature and
  task files in each repo, plus "Needed from other repos" bookkeeping.

A ROS repo can hold many packages, and colcon finds them at any depth. One repo
keeps the package boundaries but has one process tree, one kit and one
current.md.

**Cheaper alternative, if this is never done**: share one canonical `.claude/`
(user-level `~/.claude/` or `@path` imports in CLAUDE.md) instead of copying
it. That removes the sync commits without merging repos.

## Tool: `git subtree add`

`git subtree add --prefix=<dir> <repo-path-or-url> <branch>` copies a repo into
`<dir>/` with its full history, as one merge commit.

- **Old commits keep their hashes, authors and dates.** `git log` and
  `git blame` still work.
- **Old commits keep their old paths** (no `<dir>/` prefix), so
  `git log -- <dir>/` shows only the merge commit. Running
  `git filter-repo --to-subdirectory-filter <dir>` on each repo first gives
  clean paths, but it means redoing the whole merge.
- **It copies only the named branch.** No other branches, tags, remotes or
  GitHub issues.
- **The source repo is only read**, never changed.
- **Don't use `--squash`**: it drops the history.

## State right after the merge

- **One subdirectory per old repo, unchanged.** That includes ten `.claude/`
  folders, ten `process/` trees and ten CLAUDE.md files. Consolidating them is
  manual work afterwards.
- **The header hooks stop running.** Nested `.githooks/` are inert. One root
  `core.hooksPath` and one hook covering every subdirectory are needed.
- **Nested `.gitignore` files still work**, and colcon builds the same.
- **Feature and issue numbers collide** (every repo has its own F01…).
  Renumber them under the process's import rule (banner mapping old → new).
  This is the largest manual part of the job.

## Step 1: trial run (throwaway, nothing pushed)

Use the local clones as sources, in a folder outside `~/ros2_ws`.

```
mkdir -p ~/subtree_trial/src && cd ~/subtree_trial/src
git init combined && cd combined
git commit --allow-empty -m "Start combined repo"
git subtree add --prefix=dome_mission       ~/ros2_ws/src/dome_mission       main
git subtree add --prefix=dome_nav_msgs      ~/ros2_ws/src/dome_nav_msgs      main
git subtree add --prefix=dome_semantic_msgs ~/ros2_ws/src/dome_semantic_msgs main
```

Check each repo's branch name first:
`git -C ~/ros2_ws/src/<repo> branch --show-current`.

**Checks**:

```
git log --oneline --graph | head -40       # merges with old history beneath
git log --oneline -- dome_mission/ | head  # only the merge: old-paths caveat
git blame dome_mission/process/02-doc/spec.md | head
git config core.hooksPath                  # empty: nested hooks inert
cd ~/subtree_trial && source /opt/ros/$ROS_DISTRO/setup.bash && colcon build
/usr/bin/python3 -m pytest src/combined/dome_mission/test/ -q
```

The trial workspace's `src/` holds only the combined repo, so there are no
duplicate-package errors. If the build fails on a missing dependency, add that
repo too.

**Put the `subtree add` lines in a script during the trial**, so a redo is one
command.

## Step 2: go live (the trial repo becomes the real one; no redo needed)

1. **Freeze the old repos.** Commit and push everything. From the final pull
   until they are archived, don't commit to them.
2. **Add the remaining repos** with more `subtree add` lines.
3. **Catch up** any repo that changed since the trial:
   `git subtree pull --prefix=<dir> ~/ros2_ws/src/<repo> main`.
4. **Publish**: create an empty GitHub repo, then `git remote add origin <url>`
   and `git push -u origin main`.
5. **Swap it into the workspace**:
   - move the old clones out of `~/ros2_ws/src` (colcon refuses duplicate
     packages);
   - clone the combined repo in;
   - `rm -rf build install log` and `colcon build`.
6. **Repeat step 5 on every other machine**, e.g. the robot. *Unverified*
   whether the robot has its own clones.
7. **Move open GitHub issues** (`gh issue transfer`), then **archive** each old
   repo with a README pointer to the new one. Archive rather than delete, so
   old links keep working.

A redo is needed only for a `filter-repo` history rewrite, or to restart after
a botched consolidation. It takes about a minute per repo with the script.

## Step 3: consolidate the process (after go-live)

- One root `.claude/`, CLAUDE.md, current.md, history and notes.
- One `process/` tree, laid out as in **Target layout**. Move each package's
  old `process/` to `process/archive/<repo>/`, and renumber only the open
  features and issues (see **Numbering after the merge**).
- Package subdirectories end up holding code only. Their old CLAUDE.md and
  `.claude/` go; anything package-specific in them, like hazards and commands,
  moves to the root CLAUDE.md or that package's spec.
- One root hook for header stamping.
- Update anything that names repos or repo paths: clone scripts, robot setup
  docs, cross-repo doc links, `.repos` files.

## Target layout

There is **one `process/` at the root**. Package subdirectories hold only
code.

```
dome/                          ← combined repo
├── CLAUDE.md                  ← one, always loaded
├── .claude/                   ← one kit
├── .githooks/                 ← one hook for all packages
├── process/
│   ├── 01-literate/
│   │   ├── dome_mission/      ← literate docs, grouped by package
│   │   ├── dome_control/
│   │   └── …
│   ├── 02-doc/
│   │   ├── current.md         ← one handoff
│   │   ├── history.md
│   │   ├── notes.md
│   │   └── specs/
│   │       ├── dome_mission.md   ← one spec per package
│   │       └── …
│   ├── 03-features/           ← one sequence: F01, F02, …
│   ├── 04-tasks/
│   ├── 05-issues/
│   └── archive/               ← frozen, never renumbered
│       ├── dome_mission/      ← the old process/ tree, untouched
│       └── …
├── dome_mission/              ← code only: package.xml, dome_mission/, test/, launch/
├── dome_control/
└── …
```

The `.claude/` kit's paths (`process/02-doc/spec.md`, `/checkpoint`'s
literate step) need updating for `specs/<package>.md` and
`01-literate/<package>/`.

## Numbering after the merge

Every repo numbers from F01/I01, so the numbers collide. Counted on
2026-11-23:

- **Features**: 33 open, 71 archived.
- **Issues**: 17 open, 14 archived. dome_control's I01–I14 aren't in its
  `05-issues/`, so the real count is higher.

Old numbers also live on in commit messages and history entries, which can't
be changed.

**Recommended: freeze history, renumber only open items.**

- **Archive** each old repo's `process/` untouched under
  `process/archive/<repo>/`. Old numbers are always qualified by repo, e.g.
  "dome_mission F05", as cross-repo references already are.
- **Start one new sequence** (F01/I01) for the open items only. Each carries a
  banner such as `was dome_voice F12`, per the existing import rule.
- **Literate docs are grouped by package** under the root
  `process/01-literate/<package>/` (see **Target layout**).
- **Add a process.md exception**: "the pre-merge archive keeps its repo-local
  numbering and is never renumbered." Otherwise the retroactive-convention
  rule would require renumbering it.

**Rejected**:

- *Renumber everything* (about 135 files plus every cross-reference). A bare
  "F05" would then mean different things in docs and in git history.
- *Per-package prefixes* (`M-F05`): this brings back the per-repo bookkeeping
  the merge removes.

## What does not change

Package names, `ros2 launch` / `ros2 run`, `package.xml` dependencies, Python
imports and message packages. ROS sees packages, not repos.
