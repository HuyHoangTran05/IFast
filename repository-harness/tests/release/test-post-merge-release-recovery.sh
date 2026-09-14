#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)

release_scripts=(
  "$root/scripts/promote-harness-release-tag.sh"
  "$root/scripts/verify-harness-release-identity.sh"
  "$root/scripts/build-harness-release.sh"
  "$root/scripts/harness-release-changed.sh"
)
for script in "${release_scripts[@]}"; do
  bash -n "$script"
done

"$root/tests/release/test-harness-release-workflow-contract.sh"
"$root/tests/release/test-harness-release-identity-guard.sh"
"$root/tests/maintenance/test-harness-release-classification.sh"

workflow="$root/.github/workflows/post-merge-maintenance.yml"
grep -Fq 'scripts/harness-release-changed.sh <<<"$changed_files"' "$workflow"
grep -Fq 'uses: ./.github/workflows/harness-release.yml' "$workflow"
! grep -Fq 'harness-cli-release.yml' "$workflow"
! grep -Fq 'cli_changed' "$workflow"

echo "core-only post-merge release recovery contract passed"
