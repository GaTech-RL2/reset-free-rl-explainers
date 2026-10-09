import concurrent.futures,json
from render import render,ROOT

if __name__=='__main__':
    episodes=json.loads((ROOT/'content.json').read_text())
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:
        jobs=[pool.submit(render,ep,20) for ep in episodes]
        for job in jobs:job.result()
