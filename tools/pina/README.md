# The Código piña

`images/codigo/pina.svg` is built from the store's own egg drawing (the agave scroll block on codigo1530shop.com),
with labels and links removed and the scroll-driven opening replaced by an 18-second SMIL loop that matches the reel in `index.html`.

To rebuild (from the site root):

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --virtual-time-budget=3000 --dump-dom "file://$PWD/tools/pina/gen.html" > /tmp/pina-dom.html
python3 -c "import re,json,html;d=open('/tmp/pina-dom.html').read();open('tools/pina/egg.json','w').write(json.dumps(json.loads(html.unescape(re.search(r'<pre id=\"out\">(.*?)</pre>',d,re.S).group(1)))))"
python3 tools/pina/build.py
```

`gen.html` is the store block with `N_SCALES` lowered to 84 and an output step added. `build.py` slims the markup and adds the timeline:
closed until 37% of the loop, open by 50% (translate + rotate sampled from the store's easing, including the hop), hold, snap back at 85% while the frame is hidden.
