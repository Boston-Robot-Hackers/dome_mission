#!/usr/bin/env bash
# PostToolUse hook (Edit|Write): run ruff via uv on the file just touched, if
# it's Python and uv is installed. Reports violations back to Claude via
# stderr; never blocks -- PostToolUse can't, the edit already happened.

command -v jq >/dev/null 2>&1 || exit 0
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

[[ "$file_path" == *.py ]] || exit 0
command -v uv >/dev/null 2>&1 || exit 0
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

# Judge by exit status: ruff prints "All checks passed!" even on clean files.
status=0
check_out=$(uv run ruff check "$file_path" 2>&1) || status=1
format_out=$(uv run ruff format --check "$file_path" 2>&1) || status=1
if (( status )); then
  printf '%s\n%s\n' "$check_out" "$format_out" >&2
  exit 2
fi
exit 0
