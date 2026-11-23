"""Build the Codex plugin from committed Git contents."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import hashlib, io, json, re, subprocess, sys, tarfile

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'dist')
root.mkdir(exist_ok=True, parents=True)
paths = ['pstack/'+p for p in ['skills','agents','assets','docs','.codex-plugin','LICENSE','README.md']]
raw = subprocess.check_output(['git','-c','core.autocrlf=false','archive','--format=tar','HEAD','--',*paths])
files = {}
with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
    for f in tar:
        if f.isdir():
            continue
        assert f.isfile() and f.name.startswith('pstack/') and '..' not in f.name.split('/') and chr(92) not in f.name, f.name
        files[f.name] = (tar.extractfile(f).read(), f.mode)
assert len(files) == len({name.casefold() for name in files})
m = json.loads(files['pstack/.codex-plugin/plugin.json'][0])
assert m['name'] == m['interface']['displayName'] == 'pstack' and m['skills'] == './skills/'
for key in ('longDescription','shortDescription','developerName'):
    assert m['interface'][key].strip(), key
for key in ('logo','composerIcon'):
    assert files['pstack/'+m['interface'][key].removeprefix('./')][0].startswith(bytes.fromhex('89504e470d0a1a0a'))
assert files['pstack/LICENSE'][0] and files['pstack/docs/harness/codex.md'][0]
skills = [n for n in files if re.fullmatch(r'pstack/skills/[^/]+/SKILL.md',n)]
assert 'pstack/skills/correct/SKILL.md' in skills
for n in skills:
    header = files[n][0].decode().split('---',2)[1]
    assert re.search(r'^name:\s*'+re.escape(n.split('/')[2])+r'\s*$',header,re.M) and 'description:' in header,n
version = m['version']
assert re.fullmatch(r'\d+\.\d+\.\d+',version)
package = root / f'pstack-{version}.zip'
with ZipFile(package,'w') as z:
    for name,(data,mode) in sorted(files.items()):
        entry = ZipInfo(name)
        entry.create_system = 3
        entry.external_attr = (0o100755 if mode & 0o111 else 0o100644) << 16
        z.writestr(entry,data,compress_type=ZIP_DEFLATED,compresslevel=9)
with ZipFile(package) as z:
    assert z.testzip() is None
sha = hashlib.sha256(package.read_bytes()).hexdigest()
package.with_suffix('.zip.sha256').write_text(f'{sha}  {package.name}\n',encoding='ascii',newline='\n')
print(f'{package}: {len(skills)} skills; {len(files)} files; sha256 {sha}')
