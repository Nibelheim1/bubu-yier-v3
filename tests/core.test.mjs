import test from 'node:test';
import assert from 'node:assert/strict';
import { SaveManager, normalizeSave, SAVE_KEY, OLD_KEY } from '../src/systems/SaveManager.js';
import { ComboSystem } from '../src/systems/ComboSystem.js';
import { LEVELS, PHOTOS } from '../src/config/game.js';
const storage=(entries={})=>({ data:new Map(Object.entries(entries)),getItem(k){return this.data.get(k)??null;},setItem(k,v){this.data.set(k,v);} });
const l=LEVELS[0],pid=PHOTOS.find(p=>p.levelId===l.id).id;
const run=(o={})=>({happiness:18,maxCombo:15,elapsed:100000,hearts:3,damageHits:0,...o});

test('empty or malformed root is a complete usable V2 save',()=>{
  for(const value of [null,undefined,[],42,'text']){
    const d=normalizeSave(value);assert.equal(d.version,2);assert.equal(d.selectedCharacter,'bubu');assert.equal(Object.keys(d.levels).length,3);
  }
});
test('v1 migration retains photographs, unlock, hearts, selected character and best happiness',()=>{
  const legacy={version:1,selectedCharacter:'yier',unlockedLevel:2,levels:{[l.id]:{completed:true,photos:[pid,pid,'wrong'],collectibles:17,bestHearts:2}}};
  const st=storage({[OLD_KEY]:JSON.stringify(legacy)}),s=new SaveManager(st),d=s.data.levels[l.id];
  assert.equal(s.migrated,true);assert.equal(s.data.selectedCharacter,'yier');assert.equal(d.best.happiness,17);assert.equal(d.best.hearts,2);
  assert.deepEqual(d.photos,[pid]);assert.equal(s.data.unlockedLevel,2);assert.ok(st.getItem(SAVE_KEY));assert.ok(st.getItem(OLD_KEY));
});
test('v1 does not invent combo, time, no-damage or new badges',()=>{
  const d=normalizeSave({version:1,levels:{[l.id]:{completed:true,bestHearts:3,best:{combo:300,timeMs:2000},badges:{steady:true,flow:true}}}}).levels[l.id];
  assert.equal(d.best.combo,0);assert.equal(d.best.timeMs,null);assert.equal(d.best.noDamage,false);assert.deepEqual(d.badges,{steady:false,flow:false,happiness:false});
});
test('corruption of a single field does not erase other chapters',()=>{
  const d=normalizeSave({version:2,levels:{[l.id]:{best:{timeMs:0,happiness:'nope'},photos:[pid]},[LEVELS[1].id]:{completed:true,best:{combo:12,happiness:11}}}});
  assert.deepEqual(d.levels[l.id].photos,[pid]);assert.equal(d.levels[l.id].best.timeMs,null);assert.equal(d.levels[LEVELS[1].id].best.combo,12);assert.equal(d.unlockedLevel,3);
});
test('invalid time zero, negative and NaN become null',()=>{
  for(const t of [0,-1,NaN,Infinity,'x',null])assert.equal(normalizeSave({version:2,levels:{[l.id]:{best:{timeMs:t}}}}).levels[l.id].best.timeMs,null);
});
test('invalid role names including inherited object keys fall back safely',()=>{
  for(const c of ['toString','constructor','__proto__','missing'])assert.equal(normalizeSave({selectedCharacter:c}).selectedCharacter,'bubu');
  const s=new SaveManager(storage());s.selectCharacter('toString');assert.equal(s.data.selectedCharacter,'bubu');
});
test('broken V2 JSON falls back to preserved readable v1',()=>{
  const st=storage({[SAVE_KEY]:'{bad json',[OLD_KEY]:JSON.stringify({version:1,selectedCharacter:'yier'})});const s=new SaveManager(st);assert.equal(s.data.selectedCharacter,'yier');assert.equal(s.migrated,true);
});
test('photo unlock is validated, immediate and idempotent',()=>{
  const st=storage(),s=new SaveManager(st);assert.equal(s.addPhoto(l.id,pid),true);assert.equal(s.addPhoto(l.id,pid),false);assert.equal(s.addPhoto(LEVELS[1].id,pid),false);assert.equal(s.addPhoto(l.id,'made-up'),false);
  assert.equal(new SaveManager(st).hasPhoto(pid),true);assert.equal(s.photoCount,1);
});
test('missing storage uses memory and tells the caller it is not persistent',()=>{
  const s=new SaveManager();s.addPhoto(l.id,pid);assert.equal(s.hasPhoto(pid),true);assert.equal(s.persist(),false);assert.match(s.lastError,/本地存储/);
});
test('quota failure does not lose in-memory photographs',()=>{
  const s=new SaveManager({getItem(){return null;},setItem(){throw new Error('quota');}});s.addPhoto(l.id,pid);assert.equal(s.hasPhoto(pid),true);assert.match(s.lastError,/空间不足/);
});
test('thumbnail failure cannot erase the permanent unlock',()=>{
  const st=storage(),s=new SaveManager(st);s.addPhoto(l.id,pid);st.setItem=()=>{throw new Error('quota');};s.saveThumbnail(pid,'data:image/jpeg;base64,AAA');assert.equal(s.hasPhoto(pid),true);
});
test('badges are evaluated from a single run and remain earned',()=>{
  const s=new SaveManager(storage()),r=s.commitRun(l,'bubu',run());assert.deepEqual(r.earned,{happiness:true,steady:true,flow:true});s.commitRun(l,'bubu',run({happiness:2,maxCombo:1,damageHits:5}));assert.deepEqual(s.data.levels[l.id].badges,r.earned);
});
test('healing back to three hearts never retroactively earns no-damage',()=>{
  const s=new SaveManager(storage()),r=s.commitRun(l,'bubu',run({damageHits:2,hearts:3}));assert.equal(r.earned.steady,false);assert.equal(s.data.levels[l.id].best.noDamage,false);
});
test('best values and character personal records are independently retained',()=>{
  const s=new SaveManager(storage());s.commitRun(l,'bubu',run({elapsed:90000,maxCombo:12}));s.commitRun(l,'yier',run({elapsed:85000,maxCombo:10}));s.commitRun(l,'bubu',run({elapsed:95000,maxCombo:13}));
  const d=s.data.levels[l.id];assert.equal(d.best.timeMs,85000);assert.equal(d.best.combo,13);assert.equal(d.characters.bubu.bestTimeMs,90000);assert.equal(d.characters.yier.bestCombo,10);
});
test('JSON backup can be restored and invalid imports leave progress untouched',()=>{
  const s=new SaveManager(storage());s.addPhoto(l.id,pid);const text=s.exportJSON(),other=new SaveManager(storage());other.importJSON(text);assert.equal(other.hasPhoto(pid),true);
  assert.throws(()=>other.importJSON('{"version":4}'));assert.equal(other.hasPhoto(pid),true);assert.throws(()=>other.importJSON('{broken'));
});
test('ordinary collection increments combo, refreshes timer and keeps maximum',()=>{
  const c=new ComboSystem(3200);assert.equal(c.add(),1);c.update(2000);c.add(2);assert.equal(c.remaining,3200);assert.equal(c.count,3);c.break('damage');assert.equal(c.count,0);assert.equal(c.max,3);
});
test('combo expires exactly at the configured boundary, with one break event',()=>{
  const events=[],c=new ComboSystem(3200,{onBreak:(...a)=>events.push(a)});c.add();c.update(3199);assert.equal(c.count,1);c.update(1);assert.equal(c.count,0);c.update(100);assert.deepEqual(events,[['timeout',1]]);
});
test('Bubu keeps his extra 0.6 seconds without altering time on pause',()=>{
  const c=new ComboSystem(3800);c.add(5);c.update(3200);assert.equal(c.count,5);assert.equal(c.remaining,600);assert.equal(c.ratio,600/3800);c.update(600);assert.equal(c.count,0);
});
