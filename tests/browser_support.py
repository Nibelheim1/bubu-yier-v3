from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent.parent
async def load_offline(page,debug=True):
    async def route(r):
        uri=urlsplit(r.request.url).path
        file=ROOT/'dist'/uri.lstrip('/')
        if not file.is_file():
            await r.abort(); return
        content=file.read_bytes()
        if debug and uri=='/src/main.js':
            content=content.replace(b"this.debug=new URLSearchParams(location.search).get('debug')==='1'",b"this.debug=true")
        typ={'.js':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.jpg':'image/jpeg'}.get(file.suffix,'text/html')
        await r.fulfill(body=content,content_type=typ,headers={'Access-Control-Allow-Origin':'*'})
    await page.route('**/*',route)
    html=(ROOT/'dist/index.html').read_text().replace('<head>','<head><base href="http://local-game.test/">')
    await page.set_content(html)
    await page.wait_for_selector('#begin',timeout=15000)
