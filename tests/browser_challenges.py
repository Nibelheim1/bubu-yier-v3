import os
import asyncio,json
from playwright.async_api import async_playwright
from browser_support import load_offline,ROOT
BOT=r'''([level,char,photo])=>{
 const d=__BUBU_TEST__;d.go(level,char);d.step(8);const s=d.scene,def=s.challenge.defs[photo-1],cid=def.challengeId;
 s.placePlayer(def.entryX,def.entryY-4,{release:true});d.fastStep(30);const startState=d.state(),steps=[];let failed=false;
 const input=d.app.input;
 const controls=(direction,space=true)=>{input.keys.clear();if(space)input.keys.add('Space');if(direction>0)input.keys.add('ArrowRight');if(direction<0)input.keys.add('ArrowLeft');};
 const grounding=()=>s.actor.body.blocked.down||s.actor.body.touching.down;
 const support=()=>s.platforms.find(p=>p.body.enable&&Math.abs(p.body.top-s.actor.body.bottom)<4&&s.actor.body.right>p.body.left&&s.actor.body.left<p.body.right);
 const active=()=>s.challenge.active?.def.challengeId===cid;
 function hop(name){
   if(s.runPhotos.has(def.photoId))return true;
   const target=s.platforms.find(p=>p.object.name===name);if(!target){steps.push({name,error:'missing'});failed=true;return false;}
   const retry=s.challenge.retryCount;
   let current=support();let align=current?Math.min(current.body.right-24,current.body.center.x+50):s.actor.x;
   if(target.body.center.x<s.actor.x+30)align=s.actor.x;
   for(let i=0;i<45;i++){
     if(Math.abs(s.actor.x-align)<4&&grounding())break;
     controls(Math.abs(s.actor.x-align)<4?0:Math.sign(align-s.actor.x),false);d.fastStep();
     if(s.challenge.retryCount!==retry)break;
   }
   controls(Math.sign(target.body.center.x-s.actor.x));input.jumpQueued=true;
   let landed=false;
   for(let i=0;i<125;i++){
     const dx=target.body.center.x-s.actor.body.center.x;controls(Math.abs(dx)<3?0:Math.sign(dx));
     d.fastStep();
     if(s.challenge.retryCount!==retry||s.runPhotos.has(def.photoId))break;
     if(i>8&&grounding()&&Math.abs(s.actor.body.bottom-target.body.top)<4&&Math.abs(s.actor.body.center.x-target.body.center.x)<target.body.width/2+7){landed=true;break;}
   }
   steps.push({target:name,landed,active:active(),progress:s.challenge.progress,x:s.actor.x,y:s.actor.body.bottom,targetX:target.body.center.x,targetY:target.body.top,perfect:s.perfect.count});
   if(s.challenge.retryCount!==retry||(!landed&&!s.runPhotos.has(def.photoId))){failed=true;return false;}
   d.fastStep(2);return true;
 }
 const kind=def.challengeKind;
 if(kind==='balloons'||kind==='air-chain'){
   controls(1);input.jumpQueued=true;
   let frames=0,retry=s.challenge.retryCount;
   for(;frames<700;frames++){
     controls(s.actor.x>=def.finishX-12?0:1);
     d.fastStep();if(s.runPhotos.has(def.photoId)||s.challenge.retryCount>retry)break;
   }
   steps.push({kind,frames,state:d.state(),events:s.telemetry.events.filter(e=>e.type.startsWith('photo_challenge')).slice(-3)});
 }else{
   let names=[];
   if(kind==='bus-chain')names=['bus-1','bus-2','bus-3'];
   if(kind==='box-roof')names=['box','awning','roof'];
   if(kind==='lamps')names=['lamp-pad-0','lamp-pad-1','lamp-pad-2'];
   if(kind==='carousel')names=['horse-0','horse-1','horse-2'];
   if(kind==='fireflies')names=['tree-pad-0','tree-pad-1','tree-pad-2','tree-pad-3'];
   if(kind==='meteor')names=['meteor-pad-0','meteor-pad-1','meteor-pad-2','meteor-pad-3','meteor-pad-4'];
   if(kind==='camp-lamps')names=['star-0','star-1','star-2'];
   names.push('finish');
   for(const name of names){if(!hop(`${cid}-${name}`)||s.runPhotos.has(def.photoId))break;}
 }
 controls(0,false);d.step(1);
 return {kind,success:s.runPhotos.has(def.photoId),startState,steps,endState:d.state(),retryCount:s.challenge.retryCount};
}'''
async def main():
 results=[];errors=[]
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader'])
  page=await b.new_page(viewport={'width':1440,'height':810});page.on('pageerror',lambda e:errors.append(str(e)))
  await load_offline(page)
  for char in ('bubu','yier'):
   for level in (1,2,3):
    for photo in (1,2,3):
     r=await page.evaluate(BOT,[level,char,photo]);results.append({'character':char,'level':level,'photo':photo,**r})
     print(char,level,photo,r['kind'],r['success'],'retries',r['retryCount'],'last',r['steps'][-1] if r['steps'] else r['endState'],flush=True)
     if not r['success']:
      # Render camera near the actual course for the screenshot, without changing game state.
      await page.evaluate('''()=>{const d=__BUBU_TEST__,s=d.scene;s.cameras.main.setScroll(Math.max(0,s.actor.x-380),Math.max(0,Math.min(228,s.actor.body.bottom-350)));d.step(1);}''')
      await page.screenshot(path=str(ROOT/f'qa/challenge_fail_{char}_{level}_{photo}.png'))
  (ROOT/'qa/photo-challenges.json').write_text(json.dumps({'challenges':results,'errors':errors},ensure_ascii=False,indent=2));print('ERRORS',errors)
  await b.close()
 assert len(results)==18 and all(r['success'] for r in results), 'Photo challenge regression failed'
 assert not errors,errors
if __name__=='__main__':asyncio.run(main())
