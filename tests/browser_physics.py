import os
import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
from browser_support import load_offline,ROOT
async def main():
 report=[];errors=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader'])
  page=await browser.new_page(viewport={'width':1440,'height':810})
  page.on('pageerror',lambda e:errors.append(str(e)))
  await load_offline(page)
  async def go(n=1,c='bubu'):
   await page.evaluate('([n,c])=>{__BUBU_TEST__.go(n,c);__BUBU_TEST__.step(4);}',[n,c])
  await go()
  print('initial',await page.evaluate('__BUBU_TEST__.step(20)'))
  result=await page.evaluate('''()=>{const d=__BUBU_TEST__,s=d.scene,p=s.platforms.find(p=>p.object.name==='city-bus');s.placePlayer(p.body.center.x,p.body.top-3,{release:true});d.step(15);const before={x:s.actor.x,px:p.body.center.x,y:s.actor.body.bottom,py:p.body.top};d.step(300);return {before,after:{x:s.actor.x,px:p.body.center.x,y:s.actor.body.bottom,py:p.body.top},offsetDrift:(s.actor.x-p.body.center.x)-(before.x-before.px),state:d.state()}}''')
  report.append({'case':'horizontal_5s','result':result});print('HORIZ',json.dumps(result))
  await go(2)
  result=await page.evaluate('''()=>{const d=__BUBU_TEST__,s=d.scene,p=s.platforms.find(p=>p.object.name==='carousel-main-0');s.placePlayer(p.body.center.x,p.body.top-3,{release:true});d.step(15);let maxGap=0,airFrames=0;for(let i=0;i<300;i++){d.fastStep();maxGap=Math.max(maxGap,Math.abs(s.actor.body.bottom-p.body.top));if(!s.actor.body.touching.down)airFrames++;}return {maxGap,airFrames,state:d.state(),platformY:p.body.top}}''')
  report.append({'case':'vertical_5s','result':result});print('VERT',json.dumps(result))
  await go()
  result=await page.evaluate('''()=>{const d=__BUBU_TEST__,s=d.scene,p=s.platforms.find(p=>p.config.perfectEnabled&&p.object.name==='reward-0');s.placePlayer(p.body.center.x,p.body.top-100,{release:true});s.actor.setVelocityY(80);d.step(40);const first={perfect:s.perfect.count,combo:s.combo.count,y:s.actor.body.bottom,py:p.body.top};d.step(90);return {first,after:{perfect:s.perfect.count,combo:s.combo.count}}}''')
  report.append({'case':'perfect_once','result':result});print('PERFECT',result)
  result=await page.evaluate('''()=>{const d=__BUBU_TEST__,s=d.scene;s.combo.add(3);const before={t:s.simTime,combo:s.combo.remaining,x:s.actor.x};s.setPaused(true);d.step(240);const paused={t:s.simTime,combo:s.combo.remaining,x:s.actor.x};s.setPaused(false);d.step(2);return {before,paused,after:d.state()}}''')
  report.append({'case':'pause_freezes_time','result':result});print('PAUSE',result)
  result=await page.evaluate('''()=>{const d=__BUBU_TEST__,s=d.scene;s.respawnPoint={x:2360,y:668,facing:-1,order:1};s.damage.hearts=1;s.damage.invulnerableUntil=0;const t=s.simTime;s.damage.hit({damage:1,response:'knockback'});d.step(90);return {beforeTime:t,state:d.state(),alpha:s.avatar.alpha,flip:s.avatar.flipX}}''')
  report.append({'case':'exhausted_checkpoint','result':result});print('DEATH',result)
  for n in (2,3):
   await go(n);await page.evaluate('__BUBU_TEST__.step(40)');await page.screenshot(path=str(ROOT/f'qa/0{n+4}_{"park" if n==2 else "night"}.png'))
  print('ERRORS',errors)
  (ROOT/'qa/physics.json').write_text(json.dumps({'cases':report,'errors':errors},ensure_ascii=False,indent=2))
  await browser.close()
 r={case['case']:case['result'] for case in report}
 assert abs(r['horizontal_5s']['offsetDrift'])<2
 assert r['vertical_5s']['maxGap']<2 and r['vertical_5s']['state']['perfect']==0
 assert r['perfect_once']['first']['perfect']==r['perfect_once']['after']['perfect']==1
 assert r['pause_freezes_time']['before']==r['pause_freezes_time']['paused']
 assert r['exhausted_checkpoint']['state']['hearts']==3 and r['exhausted_checkpoint']['alpha']==1
 assert not errors,errors
if __name__=='__main__':asyncio.run(main())
