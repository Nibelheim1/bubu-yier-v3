import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { LEVELS, PHOTOS } from '../src/config/game.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const WIDTH=192,HEIGHT=16,TILE=48;
const properties=o=>Object.entries(o).filter(([,v])=>v!==undefined).map(([name,value])=>({name,type:typeof value==='boolean'?'bool':typeof value==='number'?(Number.isInteger(value)?'int':'float'):'string',value:typeof value==='object'?JSON.stringify(value):value}));
const layers=['platforms','spawn','checkpoints','goal','collectibles','photos','hazards','springs','movingPlatforms','modifiers','switches','temporaryPlatforms','perfectZones','challengeTriggers','storyTriggers','cameraBounds','routeBranches'];
export function generateLevel(level){
  let id=1;const L=Object.fromEntries(layers.map(name=>[name,[]]));
  const add=(layer,name,x,y,w,h,p={})=>{const o={id:id++,name,type:layer,x,y,width:w,height:h,rotation:0,visible:true,properties:properties(p)};L[layer].push(o);return o;};
  const heights=[],theme=level.theme;
  const holeByTheme={
    commute:{2:[19],4:[15,16],6:[18,19]},
    park:{3:[10,11],5:[17],6:[15,16]},
    starlight:{4:[20],5:[18,19],6:[21]}
  };
  for(let x=0;x<WIDTH;x++){
    const m=Math.floor(x/24),c=x%24;let row=14;
    if(theme==='commute'){
      row=14;
      if(m===1&&c>=8&&c<=17)row=13;
      if(m===2&&c>=6&&c<=10)row=13;
      if(m===3&&c>=9&&c<=15)row=13;
      if(m===4&&c>=6&&c<=11)row=13;
      if(m===5&&c>=9&&c<=14)row=12;
      if(m===6&&c>=7&&c<=12)row=13;
      if(m===7&&c>=10&&c<=17)row=13;
    }
    if(theme==='park'){
      row=14;
      if(c>=4&&c<=8)row=13;
      if(c>=9&&c<=13)row=12;
      if(c>=14&&c<=17)row=13;
      if(m===0||m===7)row=14;
      if(m===2&&c>=10&&c<=14)row=11;
      if(m===4&&c>=8&&c<=15)row=11;
      if(m===6&&c>=12&&c<=18)row=12;
    }
    if(theme==='starlight'){
      if(c<4)row=14; else if(c<8)row=13; else if(c<13)row=12; else if(c<18)row=13; else row=14;
      if(m===1&&c>=12&&c<=16)row=11;
      if(m===3&&c>=8&&c<=13)row=11;
      if(m===5&&c>=10&&c<=14)row=12;
      if(m===7)row=c<7?13:c<15?12:13;
    }
    heights[x]=(holeByTheme[theme][m]||[]).includes(c)?null:row;
  }
  const groundAt=x=>(heights[Math.max(0,Math.min(191,Math.floor(x/TILE)))]??14)*TILE;
  const data=Array(WIDTH*HEIGHT).fill(0);for(let x=0;x<WIDTH;x++)if(heights[x]!==null)for(let y=heights[x];y<HEIGHT;y++)data[y*WIDTH+x]=1;
  const groundY=groundAt(144);add('spawn','start',144,groundY-4,0,0,{facing:1});
  add('cameraBounds','world',0,0,9216,768,{lerpX:.09,lerpY:.06,lookAhead:120});
  const checkpointByTheme={commute:[1200,3980,6660],park:[1560,4380,7090],starlight:[1820,4680,7440]};const checkpointXs=checkpointByTheme[theme]; for(let n=1;n<=3;n++){const x=checkpointXs[n-1];add('checkpoints',`checkpoint-${n}`,x,groundAt(x)-88,64,88,{order:n,respawnX:x+32,respawnY:groundAt(x)-4,respawnFacing:1,heal:1});}
  add('goal','reunion',9000,groundAt(9000)-130,130,130,{nextLevel:level.nextLevel||'',reunion:theme==='starlight'});
  const platform=(name,x,y,w=120,p={})=>add(p.moving?'movingPlatforms':p.groupId?'temporaryPlatforms':'platforms',name,x-w/2,y,w,p.kind==='bus'?48:20,{kind:'ledge',oneWay:true,perfectEnabled:false,...p});
  const photoModules=theme==='commute'?[1,3,6]:theme==='park'?[1,4,6]:[2,4,6];
  const courseByModule={};
  for(let m=0;m<8;m++){
    const base=m*1152;
    add('storyTriggers',`chapter-${m}`,base+20,0,140,768,{once:true,text:level.modules[m],moduleIndex:m});
    if(!photoModules.includes(m)){
      const y=groundAt(base+300);platform(`step-${m}`,base+290,y-64,132,{kind:theme==='commute'?'awning':theme==='park'?'candy':'mushroom'});
      platform(`reward-${m}`,base+450,y-128,136,{kind:theme==='commute'?'awning':theme==='park'?'candy':'mushroom',candidatePerfect:true});
      platform(`exit-${m}`,base+610,y-96,156,{kind:theme==='commute'?'awning':theme==='park'?'candy':'mushroom'});
      add('routeBranches',`branch-${m}`,base+260,y-190,420,90,{route:'reward'});
    }
  }
  const course=(photoIndex,m,kind)=>{
    const pid=`${level.id}_photo_${photoIndex}`,cid=`challenge-${photoIndex}`,x=m*1152+(theme==='park'?238:228),y=theme==='commute'?576:theme==='park'?568:560;
    const common={challengeId:cid};
    platform(`${cid}-step`,x-145,608,118,{kind:theme==='commute'?'awning':theme==='park'?'candy':'mushroom'});
    platform(`${cid}-entry`,x,y,148,{kind:theme==='commute'?'awning':theme==='park'?'candy':'mushroom'});
    const seq=[];let count=0,finishY=500,finishX=x+704;
    const land=(suffix,dx,top,p={})=>{const name=`${cid}-${suffix}`;platform(name,x+dx,top,p.width||120,{...common,candidatePerfect:true,...p});seq.push({type:'landing',id:name,perfect:!!p.requirePerfect});return name;};
    const spark=(suffix,dx,cy,p={})=>{const name=`${cid}-${suffix}`;add('switches',name,x+dx-18,cy-18,36,36,{...common,switchKind:'spark',once:true,...p});return name;};
    if(kind==='bus-chain'){
      land('bus-1',170,516,{kind:'bus',moving:true,axis:'horizontal',distance:30,speed:32,pingPong:true});
      land('bus-2',340,468,{kind:'bus',moving:true,axis:'vertical',distance:26,speed:23,pingPong:true});
      land('bus-3',520,468,{kind:'bus',moving:true,axis:'horizontal',distance:28,speed:26,pingPong:true});finishY=492;
    }else if(kind==='box-roof'){
      land('box',165,544,{kind:'box',moving:true,axis:'horizontal',distance:48,speed:35,pingPong:true,width:104});
      land('awning',342,464,{kind:'awning',width:140});land('roof',512,408,{kind:'roof',width:152});finishY=432;
    }else if(kind==='lamps'){
      for(let i=0;i<3;i++){
        const top=[512,464,464][i],dx=170+i*170;
        platform(`${cid}-lamp-pad-${i}`,x+dx,top,128,{...common,kind:'awning',candidatePerfect:true});
        const name=spark(`lamp-${i}`,dx,top-56,{switchKind:'lamp',order:i});seq.push({type:'switch',id:name});
      }finishY=496;
    }else if(kind==='balloons'||kind==='air-chain'){
      const dxs=kind==='balloons'?[175,365,555]:[155,350,555],ys=kind==='balloons'?[438,426,448]:[406,382,414];
      if(kind==='air-chain'){
        add('springs',`${cid}-spring`,x-38,y-15,76,15,{...common,impulse:-600,kind:'rainbow'});
        spark('spark-0',65,440,{switchKind:'spark',radius:45});spark('spark-1',655,435,{switchKind:'spark',radius:45});
        count=5;
      }
      for(let i=0;i<3;i++){
        const name=`${cid}-balloon-${i}`;
        add('springs',name,x+dxs[i]-28,ys[i]-28,56,56,{...common,kind:'balloon',color:['#ed9b99','#f3d486','#9bcbd4'][i],
          impulse:-495,impulseX:230,boostMs:600,radius:42,order:i});
        if(kind==='balloons')seq.push({type:'bounce',id:name});
      }
      finishY=510;finishX=x+748;
      // A safety ledge is intentionally below the balloons, not a wall.
    }else if(kind==='carousel'){
      for(let i=0;i<3;i++)land(`horse-${i}`,170+i*178,[524,484,508][i],{kind:'horse',moving:true,axis:'vertical',distance:42,speed:30,
        pingPong:true,phase:i/3,width:132,requirePerfect:i===2,forcePerfect:true});finishY=500;
    }else if(kind==='fireflies'){
      for(let i=0;i<4;i++){
        const dx=[12,178,348,518][i],top=[544,516,476,444][i],group=`${cid}-tree-${i}`;
        const name=spark(`fly-${i}`,dx,top-55,{switchKind:'firefly',groupId:group,activeDurationMs:14000});seq.push({type:'switch',id:name});
        platform(`${cid}-tree-pad-${i}`,x+[178,348,518,694][i],[516,476,444,464][i],136,{...common,kind:'star',groupId:group,candidatePerfect:true});
      }finishY=464;finishX=x+702;
    }else if(kind==='meteor'){
      for(let i=0;i<5;i++){
        const dx=100+i*135,top=[544,500,500,452,480][i];
        platform(`${cid}-meteor-pad-${i}`,x+dx,top,118,{...common,kind:'moon',candidatePerfect:true});
        const name=spark(`star-${i}`,dx,top-46,{switchKind:'meteor',order:i});seq.push({type:'switch',id:name});
      }finishY=504;finishX=x+768;
    }else if(kind==='camp-lamps'){
      for(let i=0;i<3;i++){
        const dx=[15,225,448][i],top=[544,504,464][i],group=`${cid}-lamps-${i}`;
        const name=spark(`lamp-${i}`,dx,top-55,{switchKind:'lamp',groupId:group,activeDurationMs:14000});seq.push({type:'switch',id:name});
        platform(`${cid}-star-${i}`,x+[225,448,670][i],[504,464,496][i],170,{...common,groupId:group,kind:'star',candidatePerfect:true});
      }finishY=496;finishX=x+684;
    }
    // The last photo deck is also governed by its switch group when needed.
    const finishGroup=kind==='fireflies'?`${cid}-tree-3`:kind==='camp-lamps'?`${cid}-lamps-2`:undefined;
    platform(`${cid}-finish`,finishX,finishY,152,{...common,kind:'photo',groupId:finishGroup});
    add('photos',pid,finishX-36,finishY-86,72,86,{photoId:pid,challengeId:cid});
    add('challengeTriggers',cid,x-45,y-94,90,98,{challengeId:cid,challengeKind:kind,photoId:pid,
      timeLimitMs:kind==='fireflies'?14000:kind==='carousel'?14000:12000,retryDelayMs:1000,
      entryX:x,entryY:y+26,finishX,finishY,sequence:seq,eventCount:count,
      failOnGround:kind!=='meteor',boundsLeft:x-128,boundsRight:finishX+130,boundsBottom:648});
    add('routeBranches',`${cid}-route`,x-45,y-100,800,100,{route:'photo'});
    courseByModule[m]={x,y,cid,finishX,finishY};
  };
  const kinds=theme==='commute'?['bus-chain','box-roof','lamps']:theme==='park'?['balloons','carousel','air-chain']:['fireflies','meteor','camp-lamps'];
  photoModules.forEach((m,i)=>course(i+1,m,kinds[i]));
  if(theme==='commute'){
    for(const [m,dx] of [[2,500],[5,390]]){
      const x=m*1152+dx;platform(`rolling-box-${m}`,x,groundAt(x)-48,74,{kind:'box',moving:true,axis:'horizontal',distance:90,speed:58,pingPong:true});
    }
    platform('city-bus',2580,558,164,{kind:'bus',moving:true,axis:'horizontal',distance:120,speed:64,pingPong:true,candidatePerfect:true});
    platform('skateboard',5*1152+670,648,110,{kind:'skate',moving:true,axis:'horizontal',distance:195,speed:104,pingPong:true,sideDamage:1});
    for(const [m,dx,w] of [[0,710,190],[4,270,260],[5,860,180]]){const x=m*1152+dx;add('modifiers',`puddle-${m}`,x,groundAt(x)-16,w,24,{modifierKind:'slow',moveMultiplier:.64});}
    for(const [m,dir]of [[3,-1],[7,1]]){const x=m*1152+380;add('modifiers',`conveyor-${m}`,x,groundAt(x)-20,320,32,{modifierKind:'conveyor',direction:dir,speed:75});}
  }else if(theme==='park'){
    for(const m of [0,2,3,5,7]){const x=m*1152+(m===7?350:460);add('springs',`trampoline-${m}`,x,groundAt(x)-17,94,17,{kind:'rainbow',impulse:m===7?-745:-710});}
    for(const m of [3,5]){const x=m*1152+705;add('modifiers',`bubble-pool-${m}`,x,groundAt(x)-14,230,24,{modifierKind:'bounce',impulse:-520});}
    for(let i=0;i<3;i++)platform(`carousel-main-${i}`,2*1152+560+i*165,548-i*22,124,{kind:'horse',moving:true,axis:'vertical',distance:42,speed:30,pingPong:true,phase:i/3,candidatePerfect:true});
    for(const [i,x]of [5960,6390].entries())add('hazards',`hammer-${i}`,x,552,56,56,{hazardKind:'hammer',response:'knockback',damage:1,knockbackY:-240,cooldownMs:900,axis:'vertical',distance:66,speed:80,phase:i*.5});
  }else{
    for(const [m,dx] of [[0,330],[2,230],[5,260]]){const x=m*1152+dx;add('modifiers',`wind-${m}`,x,280,580,400,{modifierKind:'wind',airControlMultiplier:1.08,extraGravityY:-175});}
    const x=2*1152+340;add('switches','bridge-switch',x,groundAt(x)-62,46,46,{switchKind:'firefly',groupId:'main-star-bridge',once:false,cooldownMs:900,activeDurationMs:4500});
    for(let i=0;i<3;i++)platform(`main-star-${i}`,x+170+i*160,groundAt(x)-66-i*16,142,{kind:'star',groupId:'main-star-bridge',candidatePerfect:true});
    platform('moon-ferry',3*1152+520,514,168,{kind:'moon',moving:true,axis:'horizontal',distance:130,speed:50,pingPong:true,candidatePerfect:true});
    add('modifiers','night-dew',3*1152+770,groundAt(3*1152+770)-18,230,30,{modifierKind:'slippery',moveMultiplier:1});
    for(const x of [5*1152+510,5*1152+870])add('hazards',`thorn-${x}`,x,groundAt(x)-24,78,24,{hazardKind:'thorn',response:'knockback',damage:1,knockbackX:-180,knockbackY:-240,cooldownMs:900});
  }
  const counts=theme==='commute'?[2,2,3,2,3,3,2,3]:theme==='park'?[2,3,2,3,2,3,2,3]:[2,2,3,2,3,2,3,3];
  let collectible=0;
  for(let m=0;m<8;m++){
    const xs=counts[m]===3?[250,570,915]:[280,830];
    xs.forEach((dx,j)=>{
      let x=m*1152+dx,y=groundAt(x)-42;
      const course=courseByModule[m];
      // 14 accessible lower-road tokens; six reward tokens on clearly visible ledges.
      if(j===xs.length-1&&m!==0&&m!==7){
        if(course){x=course.finishX;y=course.finishY-44;}
        else{x=m*1152+450;y=groundAt(m*1152+300)-172;}
      }
      add('collectibles',`happy-${++collectible}`,x-16,y-16,32,32,{value:1,collectibleId:`${level.id}-happy-${collectible}`});
    });
  }
  // Exactly ten designated landing zones. Other ledges are ordinary forgiving surfaces.
  const candidates=[...L.platforms,...L.movingPlatforms,...L.temporaryPlatforms].filter(o=>o.properties.some(p=>p.name==='candidatePerfect'&&p.value));
  candidates.sort((a,b)=>Number(b.properties.some(p=>p.name==='forcePerfect'&&p.value))-Number(a.properties.some(p=>p.name==='forcePerfect'&&p.value)));
  for(const o of candidates.slice(0,10)){
    o.properties.find(p=>p.name==='perfectEnabled').value=true;
    add('perfectZones',`perfect-${o.name}`,o.x,o.y,o.width,12,{zoneId:`perfect-${o.name}`,platformId:o.name,comboValue:1});
  }
  for(const group of Object.values(L))for(const o of group)o.properties=o.properties.filter(p=>!['candidatePerfect','forcePerfect','width'].includes(p.name));
  return {compressionlevel:-1,height:HEIGHT,width:WIDTH,infinite:false,orientation:'orthogonal',renderorder:'right-down',tiledversion:'1.11.0',tileheight:TILE,tilewidth:TILE,type:'map',version:'1.10',
    properties:properties({levelId:level.id,theme,moduleCount:8,totalCollectibles:20,totalPhotos:3}),
    tilesets:[{firstgid:1,name:`tileset_${level.id}`,image:`tileset_${level.id}.png`,imagewidth:384,imageheight:48,tilewidth:48,tileheight:48,tilecount:8,columns:8}],
    layers:[{id:1,type:'tilelayer',name:'terrain',width:WIDTH,height:HEIGHT,opacity:1,visible:true,x:0,y:0,data},
      ...Object.entries(L).map(([name,objects],i)=>({id:i+2,name,type:'objectgroup',draworder:'topdown',visible:true,opacity:1,objects}))],nextlayerid:layers.length+2,nextobjectid:id};
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
  fs.mkdirSync(path.join(root,'public/assets/maps'),{recursive:true});
  for(const level of LEVELS){const map=generateLevel(level);fs.writeFileSync(path.join(root,'public/assets/maps',`${level.id}.json`),JSON.stringify(map,null,2));console.log('Generated',level.id);}
}
