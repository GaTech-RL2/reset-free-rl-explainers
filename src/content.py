import importlib
from schema import ROOT
EPISODES = sorted([importlib.import_module(p.stem).EPISODE for p in (ROOT/'src').glob('episode_*.py')], key=lambda e:e['number'])

if __name__ == '__main__':
    import json
    for ep in EPISODES:
        print(ep['id'], len(ep['chapters']), sum(len(c['narration'].split()) for c in ep['chapters']))
    (ROOT/'content-draft.json').write_text(json.dumps(EPISODES,ensure_ascii=False,indent=2))
