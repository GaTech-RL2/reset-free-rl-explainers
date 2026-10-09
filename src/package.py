"""Package original viewing assets and rebuild sources; omit downloaded research and caches."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def files():
    paths=[ROOT/x for x in ['index.html','README.md','requirements.txt','serve.py','content.json','.nojekyll','.gitignore','sources/manifest.json','qa/verification.json','qa/media-verification.json']]
    for pattern in ['src/*.py','src/*.js','src/*.css','src/*.html','assets/math/*.svg','assets/math/*.png','media/*.mp4','captions/*.vtt','captions/*.srt','transcripts/*.txt','previews/*.jpg']:paths.extend(sorted(ROOT.glob(pattern)))
    for ep in json.loads((ROOT/'content.json').read_text()):paths.append(ROOT/(ep['id']+'.html'))
    return sorted(set(paths))

if __name__=='__main__':
    paths=files()
    assert all(p.exists() for p in paths)
    checksums={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (ROOT/'checksums.json').write_text(json.dumps(checksums,indent=2))
    archive=ROOT/'reset-free-rl-explainers.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in paths+[ROOT/'checksums.json']:z.write(p,ROOT.name+'/'+str(p.relative_to(ROOT)))
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    print('Verified archive:',len(paths)+1,'files;',round(archive.stat().st_size/1e6,1),'MB')
