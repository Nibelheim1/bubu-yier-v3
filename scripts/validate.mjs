import fs from 'node:fs';
import { LEVELS } from '../src/config/game.js';
import { validateLevel } from '../src/tiled/LevelValidator.js';
let fail=false;
for(const level of LEVELS){
  const map=JSON.parse(fs.readFileSync(new URL(`../public/assets/maps/${level.id}.json`,import.meta.url)));
  const r=validateLevel(map,level);console.log(level.title,JSON.stringify(r));if(!r.ok)fail=true;
}
if(fail)process.exitCode=1;
