#!/usr/bin/env bash
# SessionStart hook (startup|resume): surface only the newest subsection of
# process/02-doc/current.md's ## Open section, so orientation happens even if
# /start is never run, without loading the whole file twice when it is.
# Silent no-op if the project hasn't been bootstrapped or has no ## Open.

project_dir="${CLAUDE_PROJECT_DIR:-.}"
current_md="$project_dir/process/02-doc/current.md"
max_lines=60

[[ -f "$current_md" ]] || exit 0

awk -v max="$max_lines" '
  /^## Open/ { in_open=1; next }
  in_open && /^## / { exit }
  in_open && /^### / { subsections++; if (subsections > 1) exit }
  in_open && subsections == 1 { print; printed++; if (printed >= max) exit }
' "$current_md"

echo
echo "(Newest handoff only. Run /start for the full open list in process/02-doc/current.md.)"
exit 0
