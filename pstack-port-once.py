"""Materialize the initial Codex port from the pinned upstream pstack tree."""
import json, re, subprocess
from pathlib import Path

p = Path('pstack')
upstream = '0b46ec399d55f2829e88822998f53b84944837d3'
assert subprocess.check_output(['git','diff',upstream,'HEAD','--','pstack']) == b''
def put(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(value, encoding='utf8', newline='\n')
def write_json(path, data):
    put(path,json.dumps(data,indent=2,ensure_ascii=False)+'\n')

put(Path('pstack-upstream.lock'),upstream+'\n')
write_json(p/'.codex-plugin/plugin.json',{
    'name':'pstack','version':'0.15.47','description':"Lauren Tan's pstack skills with a community-maintained Codex adapter.",
    'author':{'name':'Lauren Tan (upstream)'},'license':'MIT','skills':'./skills/','requires_local_executor':True,
    'homepage':'https://github.com/wwx814/plugins/tree/codex/pstack','repository':'https://github.com/wwx814/plugins',
    'interface':{'displayName':'pstack','shortDescription':'GitHub engineering workflows','longDescription':'Investigate code, compare designs, review changes and verify behavior with the pstack skills and playbooks. This independent Codex port maps tools, workspace paths and agent roles to the capabilities available in your session.',
    'developerName':'wwx814 (Codex port), Lauren Tan (upstream)','category':'Developer Tools','capabilities':['Code investigation','Change review','Behavior verification'],'composerIcon':'./assets/logo.png','logo':'./assets/logo.png'}})
write_json(Path('.agents/plugins/marketplace.json'),{'name':'pstack-plugins','interface':{'displayName':'pstack'},'plugins':[{'name':'pstack','source':{'source':'local','path':'./pstack'},'policy':{'installation':'AVAILABLE','authentication':'ON_INSTALL'},'category':'Developer Tools'}]})
put(p/'docs/harness/codex.md','''# Running pstack in Codex

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
''')
for f in sorted((p/'skills').rglob('*.md')):
    s = f.read_text(encoding='utf8'); old = s
    s = s.replace('~/.cursor/skills/','~/.agents/skills/').replace('.cursor/skills/','.agents/skills/')
    s = s.replace("Cursor's built-in "+chr(96)+'create-skill'+chr(96),"Codex's skill-creator")
    if f.name == 'SKILL.md':
        header, sep, rest = s.partition('\n---\n')
        assert sep, f
        link = 'In Codex, follow the [Codex adapter](../../docs/harness/codex.md) for tool names, agent roles, transcripts, and workspace paths throughout this workflow.'
        heading = re.search(r'^# .+$',rest,re.M)
        pos = heading.end() if heading else 0
        rest = rest[:pos]+'\n\n'+link+'\n'+rest[pos:]
        if f.parent.name == 'setup-pstack':
            header = header.replace('writes an always-applied rule that overrides the skill defaults','records workspace role preferences in AGENTS.md')
            rest = '\n# Configure pstack in Codex\n\n'+link+'\n\nAsk which roles need a different model or effort. Show only choices exposed by the session. Default to inheritance. Confirm the preferred scope and table. For persistent workspace preferences update only the pstack section of AGENTS.md. Preserve unrelated content and re-read the result. Explain when the host cannot select a requested model.\n'
        if f.parent.name == 'poteto-mode':
            start=rest.index('## Subagents'); end=rest.index('\n## ',start+4)
            rest=rest[:start]+'## Subagents\n\nUse workspace pstack preferences from AGENTS.md. Give each authorized worker a bounded task and verifiable return condition. Follow the Codex adapter for model selection, role briefs and returning results. Verify the actual output before integration.\n'+rest[end:]
        if f.parent.name == 'recall':
            rest=re.sub(r'^Transcripts live at .*$', 'Use the Codex chat list for the active project and read only matching chats. Cite the chat ID.',rest,flags=re.M)
        if f.parent.name == 'make-bot-ui':
            rest=rest.replace(link,link+' This workflow requires a separately provisioned Grok Bot webhook. Verify it exists before starting.')
        s = header+sep+rest
    if f.name=='autonomous-run.md':
        s=re.sub(r'^2\. Pick the wake mechanism.*$','2. Watch the relevant CI run, merge, or ref in the active Codex task. Recheck until its completion condition holds.',s,flags=re.M)
    if s!=old: put(f,s)
