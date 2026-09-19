import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { LEVELS } from '../src/config/game.js';
import {validateLevel,objects,props,groundRects} from '../src/tiled/LevelValidator.js';
const maps=LEVELS.map(l=>JSON.parse(fs.readFileSync(new URL(`../public/assets/maps/${l.id}.json`,import.meta.url),'utf8')));
for(let i=0;i<3;i++)test(`chapter ${i+1}: real Tiled data, quantities, cross-references and Bubu geometry`,()=>{
  const v=validateLevel(maps[i],LEVELS[i]);assert.deepEqual(v.errors,[]);assert.equal(v.ok,true);assert.equal(v.stats.happiness,20);assert.equal(v.stats.photos,3);assert.equal(v.stats.checkpoints,3);assert.equal(v.stats.perfect,10);assert.ok(v.stats.maxGap<=144);assert.ok(v.stats.maxRise<=96);
});
test('all three main terrain outlines are different',()=>{const outlines=maps.map(m=>JSON.stringify(groundRects(m).map(r=>[r.x,r.y,r.width])));assert.equal(new Set(outlines).size,3);});
test('every chapter provides eight labelled modules and at least four explicit branches',()=>{for(const m of maps){assert.equal(objects(m,'storyTriggers').length,8);assert.ok(objects(m,'routeBranches').length>=4);}});
test('nine photo challenges are actual multi-event sequences, never touch-to-unlock',()=>{for(const m of maps)for(const o of objects(m,'challengeTriggers')){const p=props(o);assert.ok(JSON.parse(p.sequence).length>=3||p.eventCount>=5);assert.ok(p.retryDelayMs>=0);assert.ok(p.timeLimitMs>=5000);}});
test('main star bridge can be activated again after failure',()=>{const p=props(objects(maps[2],'switches').find(o=>o.name==='bridge-switch'));assert.equal(p.once,false);assert.equal(p.activeDurationMs,4500);});
test('missing goal is rejected',()=>{const m=structuredClone(maps[0]);m.layers.find(l=>l.name==='goal').objects=[];assert.equal(validateLevel(m,LEVELS[0]).ok,false);});
test('duplicate photo IDs are rejected',()=>{const m=structuredClone(maps[0]),p=objects(m,'photos');p[1].properties.find(v=>v.name==='photoId').value=props(p[0]).photoId;assert.match(validateLevel(m,LEVELS[0]).errors.join(' '),/照片/);});
test('unsupported modifier enum and orphaned switch group are rejected',()=>{const m=structuredClone(maps[2]);objects(m,'modifiers')[0].properties.find(p=>p.name==='modifierKind').value='fake';objects(m,'switches')[0].properties.find(p=>p.name==='groupId').value='absent';assert.equal(validateLevel(m,LEVELS[2]).ok,false);});
test('non-contiguous checkpoint order is rejected',()=>{const m=structuredClone(maps[0]);objects(m,'checkpoints')[1].properties.find(p=>p.name==='order').value=5;assert.match(validateLevel(m,LEVELS[0]).errors.join(' '),/order/);});
test('collectible value is accounted for rather than hardcoded to object count',()=>{const m=structuredClone(maps[0]);objects(m,'collectibles')[0].properties.find(p=>p.name==='value').value=2;assert.match(validateLevel(m,LEVELS[0]).errors.join(' '),/manifest/);});
