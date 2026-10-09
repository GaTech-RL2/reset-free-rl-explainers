"""Create local, scalable equation assets without a CDN or a browser math dependency."""
import hashlib,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
from matplotlib.mathtext import math_to_image
from matplotlib.font_manager import FontProperties
from content import EPISODES,ROOT

def key(math,color):return hashlib.sha1((math+color).encode()).hexdigest()[:16]

def main():
    failures=[]
    for ep in EPISODES:
        for ch in ep['chapters']:
            for step in ch['steps']:
                k=key(step['math'],ep['color'])
                for fmt in ('svg','png'):
                    path=ROOT/'assets/math'/f'{k}.{fmt}'
                    try:
                        math=step['math'].replace(r'\mathrel{?}',r'\;?\;').replace(r'\tfrac12',r'\frac{1}{2}').replace(r'\frac1c',r'\frac{1}{c}').replace(r'\sqrt K',r'\sqrt{K}').replace(r'\mathbin{\|}',r'\Vert').replace(r'\overline Q',r'\overline{Q}')
                        math_to_image('$'+math+'$',str(path),prop=FontProperties(size=27),dpi=180,format=fmt,color=ep['color'])
                    except Exception as e:
                        failures.append((ep['id'],ch['title'],step['math'],str(e)))
                        break
    if failures:
        for f in failures:print(f)
        raise SystemExit(f'{len(failures)} equations failed')
    print('Rendered',sum(len(c['steps']) for e in EPISODES for c in e['chapters']),'equations as SVG + PNG')

if __name__=='__main__':main()
