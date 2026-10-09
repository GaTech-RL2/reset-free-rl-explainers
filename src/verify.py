"""Check the actual browser UI and independent mathematical edge cases."""
import asyncio,json,math
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:8769/'

async def main():
    checks=[];errors=[]
    def check(name,ok,detail=None):
        checks.append(dict(name=name,passed=bool(ok),detail=detail))
        if not ok:raise AssertionError(f'{name}: {detail}')
    async with async_playwright() as p:
        browser=await p.chromium.launch(channel='chrome',headless=True,args=['--disable-gpu'])
        page=await browser.new_page(viewport={'width':1440,'height':1100})
        page.on('pageerror',lambda e:errors.append(str(e)))
        await page.goto(BASE,wait_until='networkidle')
        check('six episode selectors',await page.locator('[data-episode]').count()==6)
        await page.screenshot(path=str(ROOT/'qa/desktop.png'),full_page=True)
        ids=['foundations','leave-no-trace','medal','risc','no-regret','morefree']
        for i,id in enumerate(ids):
            await page.locator(f'[data-episode="{i}"]').click()
            await page.locator('#tab-watch').click()
            await page.wait_for_function("document.querySelector('video').readyState>=1")
            duration=await page.locator('video').evaluate('(v)=>v.duration')
            check(id+' media duration',abs(duration-840)<.05,duration)
            check(id+' chapter count',await page.locator('.chapter-button').count()==12)
            await page.locator('[data-chapter="7"]').click()
            await page.wait_for_timeout(600)
            state=await page.locator('video').evaluate('(v)=>({t:v.currentTime,paused:v.paused,err:v.error?.message})')
            expected=await page.evaluate('EPISODES[Course.current].chapters[7].start')
            check(id+' chapter seeking',abs(state['t']-expected)<3,state)
            check(id+' playback started',not state['paused'] and not state.get('err'),state)
            await page.locator('video').evaluate('(v)=>v.pause()')
            await page.locator('#tab-lab').click()
            check(id+' live laboratory',await page.locator('#lab-metrics .metric').count()==3)
            before=await page.locator('#lab-metrics').inner_text()
            slider=page.locator('#laboratory input[type=range]').first
            await slider.evaluate("el=>{el.value=el.max;el.dispatchEvent(new Event('input',{bubbles:true}))}")
            after=await page.locator('#lab-metrics').inner_text()
            if id!='medal':check(id+' slider changes calculation',before!=after)
            else:
                await page.locator('#match-ten').click()
                check('MEDAL performs distribution updates','10' in await page.locator('#lab-metrics').inner_text())
                check('MEDAL binwise table',await page.locator('#lab-table tbody tr').count()==8)
            await page.locator('#main').scroll_into_view_if_needed()
            await page.screenshot(path=str(ROOT/'qa'/f'{id}-lab.png'),full_page=True)
            await page.locator('#tab-notes').click()
            check(id+' derivation count',await page.locator('.derivation').count()==36)
            await page.locator('.chapter-note').first.locator('img').first.wait_for(state='visible')
            ok=await page.locator('.chapter-note').first.locator('img').evaluate_all('(els)=>els.every(e=>e.complete&&e.naturalWidth>0)')
            check(id+' math SVGs load',ok)
        # Analytic edge cases with independently known outcomes.
        facts=await page.evaluate('''()=>{
          const M=LabModels;
          const f=M.foundations({gamma:.9,p:.2,r:1,next:10,term:false,trunc:true});
          const a=M.medal([.2,.8],[.2,.8]);
          const r0=M.risc({c:.8,beta:.7,zeta:0,m:10,M:100});
          const r1=M.risc({c:1,beta:0,zeta:1,m:10,M:100});
          const rb=M.risc({c:1,beta:1,zeta:1,m:10,M:100});
          const p=M.price({bonus:.3,p:.2,eta:.5,cap:4,K:100});
          const low=M.price({bonus:.3,p:.2,eta:.5,cap:1,K:100});
          const w=M.morefree({alpha:.2,horizon:30,bias:.1});
          return {f,a,r0:r0.expected,r1:r1.expected,rb:rb.expected,p,low,w};
        }''')
        check('continuing one-state value is ten',abs(facts['f']['truth']-10)<1e-10)
        check('false cutoff value is 25/7',abs(facts['f']['falseValue']-25/7)<1e-10)
        check('handoff preserves target ten',abs(facts['f']['target']-10)<1e-10 and facts['f']['falseTarget']==1)
        check('matched distributions have JS zero',abs(facts['a']['js'])<1e-12 and facts['a']['C']==[.5,.5])
        check('no eligibility reaches maximum',facts['r0']==100)
        check('unit hazard switches at minimum',facts['r1']==10)
        check('beta one disables early switching',facts['rb']==100)
        check('price reaches crossing after fifteen risky rounds',facts['p']['riskyCount']==15 and abs(facts['p']['resets']-3)<1e-10)
        check('insufficient cap leaves every round risky',facts['low']['riskyCount']==100)
        check('MoReFree exact default goal weights',facts['w']['weights']==[.1,.1,.8])
        check('paired call fraction is one third',abs(facts['w']['callFraction']-1/3)<1e-12)
        check('constant gain error is three',abs(facts['w']['error']-3)<1e-10)
        # Ensure all equation assets are valid even in closed details.
        assets=await page.evaluate('EPISODES.flatMap(e=>e.chapters.flatMap(c=>c.steps.map(s=>s.asset)))')
        for asset in set(assets):
            response=await page.request.get(BASE+asset)
            if response.status!=200:raise AssertionError(asset)
        check('all 216 equation references resolve',len(assets)==216)
        await page.set_viewport_size({'width':390,'height':844})
        for i,id in enumerate(ids):
            await page.evaluate(f'Course.selectEpisode({i});Course.selectTab("lab")')
            overflow=await page.evaluate('document.documentElement.scrollWidth>window.innerWidth+1')
            check(id+' mobile page fits viewport',not overflow)
        await page.screenshot(path=str(ROOT/'qa/mobile-lab.png'),full_page=True)
        await page.evaluate('Course.selectEpisode(0);Course.selectTab("watch")')
        await page.screenshot(path=str(ROOT/'qa/mobile-watch.png'),full_page=True)
        # Real offline entry point; no fetch() dependency, all equations local.
        offline=await browser.new_context(offline=True,viewport={'width':1280,'height':900})
        op=await offline.new_page()
        await op.goto((ROOT/'risc.html').as_uri())
        check('standalone companion selects its lesson',await op.evaluate('EPISODES[Course.current].id')=='risc')
        await op.locator('#tab-lab').click()
        check('offline laboratory computes',await op.locator('#lab-metrics .metric').count()==3)
        check('no JavaScript exceptions',not errors,errors)
        await browser.close()
    (ROOT/'qa/verification.json').write_text(json.dumps(dict(passed=len(checks),checks=checks,errors=errors),indent=2))
    print('Passed',len(checks),'browser and mathematical checks.')

if __name__=='__main__':asyncio.run(main())
