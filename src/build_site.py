import json,re
from pathlib import Path
from prepare_math import key
ROOT=Path(__file__).resolve().parents[1]

def main():
    data=json.loads((ROOT/'content.json').read_text())
    for ep in data:
        for ch in ep['chapters']:
            for step in ch['steps']:
                step['asset']='assets/math/'+key(step['math'],ep['color'])+'.svg'
                path=ROOT/step['asset']
                assert path.exists(),path
                # Remove Matplotlib's canvas fill to make equation SVGs transparent.
                s=re.sub(r'<g id="patch_1">.*?</g>','',path.read_text(),flags=re.S)
                path.write_text(s)
    (ROOT/'content.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    template=(ROOT/'src/index.template.html').read_text()
    for marker,file in [('CSS','style.css'),('LABS','labs.js'),('APP','app.js')]:template=template.replace('/* INLINE_'+marker+' */',(ROOT/'src'/file).read_text())
    template=template.replace('/* INLINE_DATA */','window.EPISODES = '+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+';')
    (ROOT/'index.html').write_text(template)
    for ep in data:(ROOT/(ep['id']+'.html')).write_text(template.replace('<body>',f'<body data-initial="{ep["id"]}">'))
    (ROOT/'.nojekyll').touch()
    print('Built seven offline-capable HTML entry points with embedded code and data.')

if __name__=='__main__':main()
