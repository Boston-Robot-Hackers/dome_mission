---
description: Run tests, update docs, commit and push
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git push *) Bash(git diff *) Bash(git ls-files *) Bash(uv run pytest *) Bash(uv run ruff *) Read Edit Write Glob
---
Run a full checkpoint in this order:

- Run all tests: `uv run pytest`
- Run `uv run ruff check` and `uv run ruff format --check` on changed `.py` files
  only (staged, unstaged, and untracked — never the whole repo); fix any
  violations before continuing
- Update current.md's `## Open` section following `.claude/process.md`'s
  *current.md* rules: replace the `### Pick up here` subsection with this
  session's, fold the previous one's still-open items into the grouped lists,
  move completed items to `process/02-doc/history.md` and durable facts to
  `process/02-doc/notes.md`; keep the file within its size budget
- Review changed code against judgment rules in @.claude/style_guide.md (design, error handling, naming semantics)
- Update any changed literate md files
- If the project has a `CHANGELOG.txt`, propose one line for what is being
  pushed, per `.claude/process.md`'s *Changelog* rule, or say why none is
  needed; wait for the user to approve or rewrite it, then add it
- Create a commit (no need for a pull request)
- Push to github