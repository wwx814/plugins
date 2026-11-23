# pstack for Codex

Download the ZIP and SHA-256 checksum from [Releases](https://github.com/wwx814/plugins/releases). The package name is **pstack**. For a custom workspace plugin, upload the ZIP through your workspace's plugin manager and open a new chat. For a Git marketplace, use the default branch of this fork: `codex plugin marketplace add wwx814/plugins`, then `codex plugin add pstack@pstack-plugins`. Choose the installation method you intend to maintain.

## Upstream updates

The [GitHub workflow](https://github.com/wwx814/plugins/actions/workflows/pstack-codex.yml) checks cursor/plugins every six hours at minute 17 UTC. The main branch tracks upstream. The default codex branch contains the port at the original pstack/ paths. pstack-upstream.lock records the last integrated upstream pstack commit. The Codex plugin has its own version in pstack/.codex-plugin/plugin.json.

A clean change opens a PR to codex. Download the candidate ZIP and three patches from the linked Actions run. The patches show the upstream change, the proposed change to your port, and the complete difference between the candidate and upstream. Review new tool names, model requirements and external integrations before merging. A conflict opens an Issue and leaves the released baseline in place. To resolve it, integrate the indicated upstream diff on a branch from codex, resolve conflicts, update the lock and bump the Codex manifest version in the same PR. Future runs resume from the merged baseline.

Merging the PR builds a tagged Release with the approved ZIP and checksum. For a port-only change, bump the Codex manifest version when package contents change. GitHub notifications for Issues, Pull requests and Releases can be delivered to your configured email. Workspace ZIP installations are updated by uploading the new release. See the [Codex tool mappings](pstack/docs/harness/codex.md) for runtime requirements.
