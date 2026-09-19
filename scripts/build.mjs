import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { LEVELS } from '../src/config/game.js';
import { validateLevel } from '../src/tiled/LevelValidator.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),dist=path.join(root,'dist');
for(const l of LEVELS){const r=validateLevel(JSON.parse(fs.readFileSync(path.join(root,`public/assets/maps/${l.id}.json`))),l);if(!r.ok)throw new Error(r.errors.join(';'));}
fs.rmSync(dist,{recursive:true,force:true});fs.mkdirSync(dist,{recursive:true});
for(const item of ['src','vendor'])fs.cpSync(path.join(root,item),path.join(dist,item),{recursive:true});
fs.cpSync(path.join(root,'public'),dist,{recursive:true});fs.copyFileSync(path.join(root,'index.html'),path.join(dist,'index.html'));
fs.copyFileSync(path.join(root,'THIRD_PARTY_NOTICES.md'),path.join(dist,'THIRD_PARTY_NOTICES.md'));
console.log('Built dist/ — native ES modules, all assets local, no network dependency.');
