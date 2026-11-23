#!/usr/bin/env bash
# Compare the upstream pstack path and open at most one review at a time.
set -euo pipefail
export GH_REPO="$GITHUB_REPOSITORY"
mkdir -p dist
git fetch --no-tags https://github.com/cursor/plugins.git refs/heads/main
tip=$(git rev-parse FETCH_HEAD)
raw=$(git log -1 --format=%H "$tip" -- pstack)
old=$(cat pstack-upstream.lock)
git merge-base --is-ancestor "$old" "$raw"
git fetch --no-tags origin main
mirror=$(git rev-parse FETCH_HEAD)
if [[ "$mirror" != "$tip" ]]; then
  git merge-base --is-ancestor "$mirror" "$tip"
  if ! gh api -X POST "repos/$GH_REPO/merge-upstream" -f branch=main >/dev/null; then
    echo '::warning::GitHub could not advance the fork mirror. Comparing the fetched upstream commit directly.'
    echo 'The fork main mirror needs attention. The pstack check uses the fetched upstream commit.' >> "$GITHUB_STEP_SUMMARY"
  fi
fi
if [[ "$old" == "$raw" ]]; then
  echo "pstack already tracks $raw" >> "$GITHUB_STEP_SUMMARY"
  exit 0
fi
branch="sync/pstack-$raw"
if [[ -n "$(gh pr list --base codex --state open --json headRefName --jq '.[] | select(.headRefName | startswith("sync/pstack-")) | .headRefName')" ]]; then
  echo 'An upstream update is already in review.' >> "$GITHUB_STEP_SUMMARY"
  exit 0
fi
base=$(git rev-parse HEAD)
run="$GITHUB_SERVER_URL/$GH_REPO/actions/runs/$GITHUB_RUN_ID"
git diff --binary "$old" "$raw" -- pstack > dist/01-upstream.patch
if [[ -s dist/01-upstream.patch ]] && ! git apply --3way --index dist/01-upstream.patch; then
  title="Port conflict for pstack ${raw:0:12}"
  if [[ -z "$(gh issue list --state open --search "$title in:title" --json title --jq '.[].title' | grep -Fx "$title" || true)" ]]; then
    gh issue create --title "$title" --body "Upstream [$old...$raw](https://github.com/cursor/plugins/compare/$old...$raw) overlaps the Codex port. See the patch and conflicting paths in the [workflow run]($run). The released baseline remains $old."
  fi
  exit 1
fi
if git ls-files -s -- pstack | grep -E '^(120000|160000) ' >/dev/null; then
  echo 'Unexpected symlink or gitlink in pstack' >&2; exit 1
fi
printf '%s\n' "$raw" > pstack-upstream.lock
python - <<'PY'
import json
from pathlib import Path
p=Path('pstack/.codex-plugin/plugin.json')
m=json.loads(p.read_text())
a,b,c=map(int,m['version'].split('.'))
m['version']=f'{a}.{b}.{c+1}'
p.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
PY
git add pstack-upstream.lock pstack/.codex-plugin/plugin.json
git commit -m "Integrate upstream pstack ${raw:0:12} for Codex"
git diff --binary "$base" HEAD -- pstack pstack-upstream.lock > dist/02-codex-update.patch
git diff --binary "$raw" HEAD -- pstack > dist/03-port-vs-upstream.patch
python pstack-package.py dist
if git ls-remote --exit-code --heads origin "$branch" >/dev/null; then
  git fetch --no-tags origin "refs/heads/$branch"
  git diff --exit-code HEAD FETCH_HEAD
else
  git push origin "HEAD:refs/heads/$branch"
fi
gh pr create --base codex --head "$branch" --title "Update pstack to upstream ${raw:0:12}" --body "Upstream [$old...$raw](https://github.com/cursor/plugins/compare/$old...$raw). The [run artifacts]($run) contain the candidate ZIP, checksum, upstream patch, proposed Codex update and full port diff. Review new host-specific instructions before merging. Merge to publish the reviewed package."
