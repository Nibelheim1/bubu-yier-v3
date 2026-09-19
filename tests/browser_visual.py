import os
"""Capture built game screens. Saved records and scene positions are visual fixtures."""
import asyncio,json
from playwright.async_api import async_playwright
from browser_support import load_offline,ROOT

async def main():
 errors=[];captures=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader'])
  page=await browser.new_page(viewport={'width':1440,'height':810},device_scale_factor=1)
  page.on('pageerror',lambda e:errors.append(str(e)))
  await load_offline(page)
  async def shot(name):
   await page.wait_for_timeout(120)
   await page.screenshot(path=str(ROOT/'qa'/name));captures.append(name)
  await shot('01_title.png')
  await page.click('#begin');await shot('02_characters.png')
  await page.click('#choose-role');await page.evaluate('__BUBU_TEST__.step(30)');await shot('03_city.png')
  await page.evaluate('''()=>{const d=__BUBU_TEST__,s=d.scene,c=s.challenge.defs[0];s.placePlayer(c.entryX,c.entryY,{release:true});d.fastStep(30);d.jump();d.app.input.keys.add('ArrowRight');d.fastStep(38);s.cameras.main.setScroll(s.actor.body.center.x-430,100);d.step();}''');await shot('04_city_photo.png')
  await page.evaluate('''()=>{const d=__BUBU_TEST__;d.go(2,'yier');d.step(10);const s=d.scene,c=s.challenge.defs[0];s.placePlayer(c.entryX,c.entryY,{release:true});d.fastStep(30);d.jump();d.app.input.keys.add('ArrowRight');d.fastStep(94);s.cameras.main.setScroll(s.actor.body.center.x-430,80);d.step();}''');await shot('05_park_balloons.png')
  await page.evaluate('''()=>{const d=__BUBU_TEST__;d.go(3,'bubu');d.step(10);const s=d.scene,sw=s.switches.find(x=>x.id==='bridge-switch');s.placePlayer(sw.x,sw.y+25,{release:true});d.fastStep(4);d.jump();d.app.input.keys.add('ArrowRight');d.fastStep(25);s.cameras.main.setScroll(s.actor.body.center.x-430,125);d.step();}''');await shot('06_night_bridge.png')
  await page.click('#pause-button');await shot('07_pause.png')
  await page.click('#pause-settings');await shot('08_settings.png')
  await page.evaluate('''()=>{const d=__BUBU_TEST__,s=d.scene;s.setPaused(false);s.damage.hearts=3;s.happiness=18;s.combo.max=15;s.simTime=92633;s.damage.hits=0;s.placePlayer(9010,670,{release:true});d.fastStep(250);d.step();}''');await shot('09_result.png')
  # Record fixtures only: never packaged in the initial save.
  await page.evaluate('''async()=>{const d=__BUBU_TEST__,{LEVELS,PHOTOS}=await import('http://local-game.test/src/config/game.js');for(const l of LEVELS){for(const p of PHOTOS.filter(p=>p.levelId===l.id))d.app.save.addPhoto(l.id,p.id);d.app.save.commitRun(l,'bubu',{happiness:18,maxCombo:15,elapsed:92633,damageHits:0,hearts:3});}d.app.open('levels');d.step(2);}''');await shot('10_levels.png')
  await page.click('#open-album');await page.evaluate('__BUBU_TEST__.step(2)');await shot('11_album.png')
  await page.click('[data-back]');await page.evaluate('__BUBU_TEST__.step(2)');await shot('12_complete_cover.png')
  await page.set_viewport_size({'width':540,'height':960});await shot('13_portrait.png')
  await browser.close()
 (ROOT/'qa/visual.json').write_text(json.dumps({'captures':captures,'errors':errors,'note':'菜单进度、结算成绩和截图位置是视觉检查夹具，不是通关成绩证明。'},ensure_ascii=False,indent=2))
 print('CAPTURES',len(captures),'ERRORS',errors)
 assert not errors
if __name__=='__main__':asyncio.run(main())
