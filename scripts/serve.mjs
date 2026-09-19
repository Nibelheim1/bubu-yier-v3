import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const base=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),dev=process.argv.includes('--dev');
const root=dev?base:path.join(base,'dist');const port=Number(process.env.PORT||4173);
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.css':'text/css; charset=utf-8','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml','.md':'text/markdown; charset=utf-8'};
http.createServer((req,res)=>{
  let url;try{url=decodeURIComponent(new URL(req.url,'http://localhost').pathname);}catch{res.writeHead(400);res.end('Bad request');return;}
  if(url==='/')url='/index.html';let file=path.resolve(root,'.'+url);
  if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return;}
  if(dev&&url.startsWith('/assets/'))file=path.join(base,'public',url);if(dev&&url==='/favicon.png')file=path.join(base,'public/favicon.png');
  if(!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404);res.end('Not found');return;}
  res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream','Cache-Control':'no-store'});fs.createReadStream(file).pipe(res);
}).listen(port,'0.0.0.0',()=>console.log(`Open http://localhost:${port} (${dev?'source':'dist'})`));
