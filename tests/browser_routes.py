import os
import asyncio,json
from playwright.async_api import async_playwright
from browser_support import load_offline,ROOT
async def main():
 results=[];errors=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader'])
  page=await browser.new_page(viewport={'width':960,'height':540});page.on('pageerror',lambda e:errors.append(str(e)))
  await load_offline(page)
  for c in ('bubu','yier'):
   for n in (1,2,3):
    await page.evaluate('([n,c])=>{__BUBU_TEST__.go(n,c);__BUBU_TEST__.step(10);}',[n,c])
    result=await page.evaluate('''()=>{
      const d=__BUBU_TEST__,s=d.scene;let frames=0,lastJump=-100,stalls=0,lastX=s.actor.x,checkX=s.actor.x;
      const floors=s.surfaces.filter(p=>p.meta.ground).map(p=>p.body);
      function floor(x){return floors.find(p=>x>=p.left&&x<p.right)}
      for(;frames<11000;frames++){
        if(s.finished)break;
        const b=s.actor.body,grounded=b.blocked.down||b.touching.down;
        d.app.input.keys.add('ArrowRight');
        const ahead=floor(b.center.x+53),here=floor(b.center.x);
        const wall=b.blocked.right||b.touching.right;
        if(grounded&&frames-lastJump>20&&(!ahead||(ahead&&ahead.top<b.bottom-16)||wall)){
          d.app.input.jumpQueued=true;d.app.input.keys.add('Space');lastJump=frames;
        }
        if(grounded&&frames-lastJump>28)d.app.input.keys.delete('Space');
        d.fastStep(1);
        if(frames%180===0){if(Math.abs(s.actor.x-checkX)<20)stalls++;checkX=s.actor.x;}
        if(stalls>8)break;
      }
      return {frames,finished:s.finished,run:s.finalRun||null,state:d.state(),stalls,events:s.telemetry.events.slice(-6)};
    }''')
    results.append({'character':c,'level':n,**result});print(c,n,'finished',result['finished'],'frames',result['frames'],'state',result['state'],'stalls',result['stalls'],flush=True)
    if not result['finished']:
     await page.screenshot(path=str(ROOT/f'qa/route_fail_{c}_{n}.png'))
  (ROOT/'qa/main-routes.json').write_text(json.dumps({'routes':results,'errors':errors},ensure_ascii=False,indent=2));print('ERRORS',errors)
  await browser.close()
 assert len(results)==6 and all(r['finished'] for r in results),'Main route regression failed'
 assert not errors,errors
if __name__=='__main__':asyncio.run(main())
