import os
"""Actual Chromium/Phaser lifecycle regressions. Fixtures select positions, not outcomes."""
import asyncio,json
from playwright.async_api import async_playwright
from browser_support import load_offline,ROOT

async def main():
 results=[];errors=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader'])
  page=await browser.new_page(viewport={'width':960,'height':540})
  page.on('pageerror',lambda e:errors.append(str(e)))
  await load_offline(page)
  async def go(n=1,c='bubu'):
   await page.evaluate('([n,c])=>{__BUBU_TEST__.go(n,c);__BUBU_TEST__.step(15);}',[n,c])
  async def check(name,code,judge):
   result=await page.evaluate(code);ok=judge(result);results.append({'case':name,'passed':bool(ok),'result':result});print(name,ok,result,flush=True)
  await go()
  await check('two fingers, release outside, pointercancel',r'''()=>{const i=__BUBU_TEST__.app.input,right=document.querySelector('[data-control=right]'),jump=document.querySelector('[data-control=jump]');
   right.dispatchEvent(new PointerEvent('pointerdown',{pointerId:11,bubbles:true}));jump.dispatchEvent(new PointerEvent('pointerdown',{pointerId:22,bubbles:true}));const both={direction:i.direction,jump:i.held('jump'),pointers:i.pointers.size};
   window.dispatchEvent(new PointerEvent('pointerup',{pointerId:11,bubbles:true}));const one={direction:i.direction,jump:i.held('jump'),pointers:i.pointers.size};
   window.dispatchEvent(new PointerEvent('pointercancel',{pointerId:22,bubbles:true}));return {both,one,none:{direction:i.direction,jump:i.held('jump'),queued:i.jumpQueued,pointers:i.pointers.size}};}''',lambda r:r['both']['direction']==1 and r['both']['jump'] and r['one']['direction']==0 and r['one']['jump'] and r['none']=={'direction':0,'jump':False,'queued':False,'pointers':0})
  await go()
  await check('hold right + press jump keeps horizontal movement in takeoff and air',r'''()=>{const d=__BUBU_TEST__,i=d.app.input,right=document.querySelector('[data-control=right]'),jump=document.querySelector('[data-control=jump]');
   right.dispatchEvent(new PointerEvent('pointerdown',{pointerId:31,bubbles:true}));d.fastStep(8);const run={dir:i.direction,vx:d.scene.actor.body.velocity.x};
   jump.dispatchEvent(new PointerEvent('pointerdown',{pointerId:32,bubbles:true}));d.fastStep(3);const takeoff={dir:i.direction,vx:d.scene.actor.body.velocity.x,vy:d.scene.actor.body.velocity.y,pointers:i.pointers.size};
   jump.dispatchEvent(new PointerEvent('pointerup',{pointerId:32,bubbles:true}));d.fastStep(10);const air={dir:i.direction,vx:d.scene.actor.body.velocity.x,vy:d.scene.actor.body.velocity.y,pointers:i.pointers.size};
   right.dispatchEvent(new PointerEvent('pointerup',{pointerId:31,bubbles:true}));return {run,takeoff,air,end:{dir:i.direction,pointers:i.pointers.size}};}''',lambda r:r['run']['dir']==1 and r['run']['vx']>200 and r['takeoff']['dir']==1 and r['takeoff']['vx']>200 and r['takeoff']['vy']<0 and r['takeoff']['pointers']==2 and r['air']['dir']==1 and r['air']['vx']>200 and r['air']['pointers']==1 and r['end']=={'dir':0,'pointers':0})
  await go()
  await check('keyboard right + jump also preserves horizontal velocity',r'''()=>{const d=__BUBU_TEST__,i=d.app.input;i.keys.add('ArrowRight');d.fastStep(8);i.keys.add('Space');i.jumpQueued=true;d.fastStep(3);const takeoff={dir:i.direction,vx:d.scene.actor.body.velocity.x,vy:d.scene.actor.body.velocity.y};i.keys.delete('Space');d.fastStep(10);const air={dir:i.direction,vx:d.scene.actor.body.velocity.x,vy:d.scene.actor.body.velocity.y};i.keys.delete('ArrowRight');return {takeoff,air};}''',lambda r:r['takeoff']['dir']==1 and r['takeoff']['vx']>200 and r['takeoff']['vy']<0 and r['air']['dir']==1 and r['air']['vx']>200)
  await check('window blur clears all inputs, freezes play, Escape resumes',r'''()=>{const d=__BUBU_TEST__,s=d.scene;d.keys(['ArrowRight','Space']);d.app.input.jumpQueued=true;window.dispatchEvent(new Event('blur'));const before=s.simTime;d.fastStep(120);const paused={paused:s.paused,t:s.simTime-before,keys:d.app.input.keys.size,queue:d.app.input.jumpQueued};window.dispatchEvent(new KeyboardEvent('keydown',{code:'Escape',bubbles:true}));return {paused,resumed:!s.paused,keys:d.app.input.keys.size};}''',lambda r:r['paused']=={'paused':True,'t':0,'keys':0,'queue':False} and r['resumed'])
  await go()
  await check('one-way ledge passes from below, catches from above',r'''()=>{const d=__BUBU_TEST__,s=d.scene,p=s.platforms.find(p=>p.object.name==='step-0');s.placePlayer(p.body.center.x,650,{release:true});d.fastStep(20);d.jump();let min=999,headBlocks=0;for(let k=0;k<65;k++){d.fastStep();min=Math.min(min,s.actor.body.bottom);headBlocks+=s.actor.body.blocked.up?1:0;}return {min,top:p.body.top,end:s.actor.body.bottom,headBlocks,perfect:s.perfect.count};}''',lambda r:r['min']<r['top'] and abs(r['end']-r['top'])<2 and r['headBlocks']==0)
  await go(3)
  await check('wind changes gravity in zone and immediately restores on leaving',r'''()=>{const d=__BUBU_TEST__,s=d.scene,m=s.modifiers.find(m=>m.modifierKind==='wind');s.placePlayer(m.rect.x+40,420,{release:true});d.fastStep(2);const inside=s.actor.body.gravity.y;s.placePlayer(100,420,{release:true});d.fastStep(2);return {inside,outside:s.actor.body.gravity.y};}''',lambda r:r['inside']==-175 and r['outside']==0)
  await go(3)
  await check('repeatable main star bridge: first entry, expiry, second entry',r'''()=>{const d=__BUBU_TEST__,s=d.scene,sw=s.switches.find(x=>x.id==='bridge-switch'),group=s.temporary.filter(p=>p.config.groupId===sw.groupId);
   s.placePlayer(sw.x,sw.y+25,{release:true});d.fastStep(2);const first=group.every(p=>p.body.enable);s.placePlayer(100,672,{release:true});d.fastStep(285);const expired=group.every(p=>!p.body.enable);s.placePlayer(sw.x,sw.y+25,{release:true});d.fastStep(2);return {first,expired,retry:group.every(p=>p.body.enable)};}''',lambda r:all(r.values()))
  await check('star platform gives standing player 300ms expiry grace',r'''()=>{const d=__BUBU_TEST__,s=d.scene,p=s.temporary.find(p=>p.config.groupId==='main-star-bridge');p.activate(s.simTime+1000);s.placePlayer(p.body.center.x,p.body.top-3,{release:true});d.fastStep(20);p.until=s.simTime+100;d.fastStep(9);const grace={enabled:p.body.enable,remaining:p.graceUntil-s.simTime};d.fastStep(18);return {grace,disabled:!p.body.enable};}''',lambda r:r['grace']['enabled'] and r['grace']['remaining']>0 and r['disabled'])
  await go()
  await check('photo timeout and re-entry cost no heart, no level restart',r'''()=>{const d=__BUBU_TEST__,s=d.scene,c=s.challenge.defs[0];s.placePlayer(c.entryX,c.entryY,{release:true});d.fastStep(25);const first=!!s.challenge.active;d.fastStep(735);const failed=s.challenge.retryCount;d.fastStep(70);return {first,failed,hearts:s.damage.hearts,hits:s.damage.hits,second:!!s.challenge.active,x:s.actor.body.center.x,entry:c.entryX,time:s.simTime};}''',lambda r:r['first'] and r['failed']>=1 and r['hearts']==3 and r['hits']==0 and r['second'] and abs(r['x']-r['entry'])<1 and r['time']>12000)
  await go()
  await check('configured two-heart damage does not reset ordinary hit to checkpoint',r'''()=>{const d=__BUBU_TEST__,s=d.scene;s.placePlayer(880,660,{release:true});const before=s.actor.x;s.combo.add(8);s.damage.hit({damage:2,response:'knockback',knockbackX:-90,knockbackY:-120,cooldownMs:900});const result={hearts:s.damage.hearts,hits:s.damage.hits,combo:s.combo.count,x:s.actor.x,vx:s.actor.body.velocity.x};d.fastStep(65);return {...result,alpha:s.avatar.alpha,before};}''',lambda r:r['hearts']==1 and r['hits']==1 and r['combo']==0 and r['x']==r['before'] and r['vx']==-90 and r['alpha']==1)
  for fps in (30,20):
   await go()
   await check(f'one-way landing at {fps} simulated updates per second',f'''()=>{{const d=__BUBU_TEST__,s=d.scene,p=s.platforms.find(p=>p.object.name==='reward-0');s.placePlayer(p.body.center.x,p.body.top-110,{{release:true}});s.actor.setVelocityY(300);d.fastStep({fps*2},{1000/fps});return {{bottom:s.actor.body.bottom,top:p.body.top,perfect:s.perfect.count,hearts:s.damage.hearts}};}}''',lambda r:abs(r['bottom']-r['top'])<2 and r['perfect']==1 and r['hearts']==3)
  for role in ('bubu','yier'):
   await go(c=role)
   await check(f'{role}: extra jump allowance is bounded',r'''()=>{const d=__BUBU_TEST__,s=d.scene;s.placePlayer(140,670,{release:true});d.fastStep(10);d.jump();d.fastStep(12);d.app.input.keys.delete('Space');d.fastStep();d.jump();d.fastStep();const second={vy:s.actor.body.velocity.y,extra:s.movement.airJumps};d.fastStep(12);d.app.input.keys.delete('Space');d.fastStep();d.jump();d.fastStep();return {second,third:{vy:s.actor.body.velocity.y,extra:s.movement.airJumps}};}''',lambda r,role=role:(r['second']['extra']==(1 if role=='yier' else 0)) and (r['third']['extra']==(1 if role=='yier' else 0)) and (r['second']['vy']<-440 if role=='yier' else r['second']['vy']>-400) and r['third']['vy']>-440)
  await check('twelve scene restarts do not accumulate scene input handlers',r'''()=>{const d=__BUBU_TEST__,counts=[];for(let n=0;n<12;n++){d.go(n%3+1,'bubu');d.fastStep(3);counts.push(d.scene.input.listenerCount('pointerupoutside'));}return {counts,keys:d.app.input.keys.size,pointers:d.app.input.pointers.size};}''',lambda r:all(c==0 for c in r['counts']) and r['keys']==0 and r['pointers']==0)
  await page.set_viewport_size({'width':540,'height':960})
  await check('portrait pause and guidance visibility',r'''()=>({paused:__BUBU_TEST__.scene.paused,guide:getComputedStyle(document.getElementById('rotate-hint')).display,keys:__BUBU_TEST__.app.input.keys.size})''',lambda r:r['paused'] and r['keys']==0 and r['guide']!='none')
  (ROOT/'qa/browser-regression.json').write_text(json.dumps({'cases':results,'errors':errors},ensure_ascii=False,indent=2))
  await browser.close()
 assert all(r['passed'] for r in results), 'See qa/browser-regression.json'
 assert not errors,errors
asyncio.run(main())
