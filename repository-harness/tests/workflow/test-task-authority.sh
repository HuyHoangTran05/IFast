#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
temp=$(mktemp -d)
trap 'rm -rf "$temp"' EXIT
fixture="$temp/repository"
mkdir -p "$fixture/docs/product" "$fixture/docs/plans/active" "$fixture/src"

printf 'A refund over USD 500 requires finance approval.\n' +  >"$fixture/docs/product/refunds.md"
printf 'unchanged application\n' >"$fixture/src/app.txt"

fingerprint() {
  find "$fixture" -type f -print0 | LC_ALL=C sort -z |
    xargs -0 shasum -a 256 | shasum -a 256 | awk '{print $1}'
}

assert_no_hidden_control_plane() {
  [[ ! -e "$fixture/harness.db" ]]
  [[ ! -e "$fixture/.harness" ]]
  [[ ! -e "$fixture/scripts/bin/harness-cli" ]]
  [[ -z "$(find "$fixture" -type f \( -name '*.changeset.jsonl' -o -name '*.sqlite' \) -print -quit)" ]]
}

# Read-only discovery changes nothing and needs no lifecycle record.
before=$(fingerprint)
grep -Fq 'requires finance approval' "$fixture/docs/product/refunds.md"
[[ "$before" == "$(fingerprint)" ]]
assert_no_hidden_control_plane

# A bounded, authorized repository change writes only its requested artifact.
printf 'Refunds at or below USD 500 may be approved by support leads.\n' +  >>"$fixture/docs/product/refunds.md"
grep -Fq 'support leads' "$fixture/docs/product/refunds.md"
[[ -z "$(find "$fixture/docs/plans/active" -type f -print -quit)" ]]
assert_no_hidden_control_plane

# A materially ambiguous request stops before application mutation.
before_app=$(shasum -a 256 "$fixture/src/app.txt" | awk '{print $1}')
grep -Fq 'materially different choices remain' "$root/docs/WORKFLOW.md"
grep -Fq 'stop and request the smallest decision' "$root/docs/WORKFLOW.md"
after_app=$(shasum -a 256 "$fixture/src/app.txt" | awk '{print $1}')
[[ "$before_app" == "$after_app" ]]
assert_no_hidden_control_plane

# Durable work uses one Git-native plan and no parallel task database.
plan="$fixture/docs/plans/active/refund-provider-migration.md"
printf '%s\n' +  '# Execution Plan: Refund Provider Migration' +  '## Status' 'Active' +  '## Outcome' 'Move refunds without losing accepted requests.' +  '## Context' 'Current provider contract.' +  '## Scope' 'Provider boundary only.' +  '## Approach' 'Freeze, migrate, verify.' +  '## Risks And Recovery' 'Retain the old provider until reconciliation passes.' +  '## Progress' '- [ ] Reconciliation proof.' +  '## Decisions' '- No task-local decision yet.' +  '## Validation' '- Focused proof pending.' +  '## Result' 'Pending.' >"$plan"
[[ -f "$plan" ]]
assert_no_hidden_control_plane

echo "read-only, bounded, ambiguity-stop, durable-plan, and no-hidden-control-plane effects passed"
