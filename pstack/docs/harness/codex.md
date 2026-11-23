# Running pstack in Codex

Select the installed pstack skill from the picker, for example $pstack:how. Upstream slash names refer to those skills or the named playbooks in poteto-mode. Apply these mappings to all examples and linked playbooks.

| Upstream instruction | Codex execution |
| --- | --- |
| Task, TaskOutput, agent mode, background workers | Use the available subagent tools when current instructions permit delegation. Provide a bounded brief, wait for the result and inspect the evidence. Work sequentially when delegation is unavailable. |
| poteto-agent, comment-sicko, generalPurpose | Supply the requested role as a brief. The bundled agents/poteto-agent.md and agents/comment-sicko.md are role references. Omit unsupported agent type parameters. |
| Vendor model lists or budgets | Inherit the parent model unless the user or applicable skill selects an available override. Report the actual reviewers. Multiple reviews on the same model represent one model family. |
| /loop | Poll the relevant condition within the active task. Create a persistent schedule only on an explicit scheduling request. |
| /deslop | Review the diff for unrelated edits, redundant code and generated filler. Run the project's applicable checks. |
| control-ui, control-cli | Use the session's browser, desktop, or shell tools to drive the actual interface. Record the observed outcome. |
| AskQuestion | Use an available user-input tool or ask in chat when a decision is necessary. |
| Cursor transcript paths and agent-transcripts | Use the current chat and authorized Codex history scoped to the named project. If history is unavailable, use the supplied context and disclose the gap. |
| Cursor rules, model profile | Store requested workspace preferences in a scoped section of AGENTS.md. Preserve other content. |
| Bugbot, Grok Bot webhooks and cloud agents | Verify the requested external integration exists and is authorized. If it is unavailable, identify that specific missing capability. |

Work within the permissions of the current task. Examples do not authorize external messages, deployments, scheduling, or reading other workspaces.
