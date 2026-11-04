import json, html, datetime, sys
cal = json.load(open(sys.argv[1])); month = sys.argv[2]; out = sys.argv[3]
E = html.escape
cards = []
pillars = {}
for p in cal:
    pillars[p["pillar"]] = pillars.get(p["pillar"], 0) + 1
    d = datetime.date.fromisoformat(p["date"])
    imgs = [f for f in p["files"] if f.endswith(".jpg")]
    if p["fmt"] == "reel":
        mp4 = [f for f in p["files"] if f.endswith(".mp4")][0]
        media = f'<video controls playsinline preload="none" poster="media/{imgs[0]}" src="media/{mp4}"></video>'
        dl = [mp4, imgs[0]]
    elif p["fmt"] == "carousel":
        media = '<div class="strip">' + "".join(f'<img loading="lazy" src="media/{f}" alt="Slide {i+1}">' for i, f in enumerate(imgs)) + "</div>"
        dl = imgs
    else:
        media = f'<img loading="lazy" src="media/{imgs[0]}" alt="{E(p["title"])}">'
        dl = imgs
    links = " · ".join(dl)
    cards.append(f'''<article class="card" id="d{p['date']}">
<div class="meta"><div class="date"><b>{d.strftime('%a %d %b')}</b><span>{p['time']} IST</span></div>
<span class="chip">{p['fmt'].title()}</span><span class="chip alt">{E(p['pillar'])}</span></div>
<div class="body"><div class="media {p['fmt']}">{media}</div>
<div class="text"><h3>{E(p['title'].replace(chr(10),' '))}</h3>
<div class="cap"><div class="caphead">Instagram <button data-c="ig{p['date']}">Copy</button></div><pre id="ig{p['date']}">{E(p['ig_text'])}</pre></div>
<details><summary>Facebook version</summary><div class="cap"><div class="caphead">Facebook <button data-c="fb{p['date']}">Copy</button></div><pre id="fb{p['date']}">{E(p['fb_text'])}</pre></div></details>
<p class="dl">Files: {links}</p></div></div></article>''')
mix = "".join(f"<li><b>{v}</b> {E(k)}</li>" for k, v in sorted(pillars.items(), key=lambda x: -x[1]))
fmts = {f: sum(1 for p in cal if p["fmt"] == f) for f in ("single", "carousel", "reel")}
page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vipra Stays {month}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@600&display=swap" rel="stylesheet">
<style>
:root{{--bg:#f6f1e6;--card:#fffdf8;--fg:#1e2a20;--mut:#6a705f;--line:#e4dccb;--acc:#1e3b2a;--gold:#b88a2f;--chip:#e8efe6}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#121712;--card:#1a211b;--fg:#ebeee6;--mut:#9ba191;--line:#2b342c;--acc:#9fd0aa;--gold:#d8ae55;--chip:#243026}}}}
:root[data-theme="dark"]{{--bg:#121712;--card:#1a211b;--fg:#ebeee6;--mut:#9ba191;--line:#2b342c;--acc:#9fd0aa;--gold:#d8ae55;--chip:#243026}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 Inter,system-ui,sans-serif}}
.wrap{{max-width:1080px;margin:0 auto;padding:40px 16px 80px}}
h1{{font:600 40px/1.1 "Playfair Display",Georgia,serif;margin:6px 0 10px;color:var(--acc)}}
.eyebrow{{letter-spacing:.14em;font-size:12px;font-weight:600;color:var(--gold)}}
.lede{{color:var(--mut);max-width:680px;margin:0 0 24px}}
.summary{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-bottom:28px}}
.box{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}}
.box h2{{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);margin:0 0 8px}}
.box ul{{margin:0;padding:0;list-style:none}}.box li{{padding:2px 0}}.big{{font:600 30px "Playfair Display",serif;color:var(--acc)}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin-bottom:16px}}
.meta{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:12px}}
.date{{display:flex;gap:8px;align-items:baseline;margin-right:6px}}.date b{{font-size:17px}}.date span{{color:var(--mut);font-size:13px}}
.chip{{background:var(--chip);color:var(--acc);border-radius:99px;padding:2px 10px;font-size:12px;font-weight:600}}.chip.alt{{background:transparent;border:1px solid var(--line);color:var(--mut)}}
.body{{display:grid;grid-template-columns:300px 1fr;gap:20px}}
.media img,.media video{{width:100%;border-radius:8px;display:block}}
.media.reel video{{aspect-ratio:9/16;background:#000;max-height:520px;object-fit:cover}}
.strip{{display:flex;gap:8px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:6px}}.strip img{{flex:0 0 85%;scroll-snap-align:start}}
h3{{font:600 21px/1.25 "Playfair Display",serif;margin:0 0 10px}}
.cap{{border:1px solid var(--line);border-radius:10px;overflow:hidden;margin-bottom:10px}}
.caphead{{display:flex;justify-content:space-between;align-items:center;padding:6px 10px;font-size:12px;font-weight:600;color:var(--mut);border-bottom:1px solid var(--line)}}
button{{font:600 12px Inter,sans-serif;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:6px;padding:4px 10px;cursor:pointer}}
pre{{white-space:pre-wrap;font:14px/1.5 Inter,sans-serif;margin:0;padding:10px 12px;max-height:260px;overflow:auto}}
details summary{{cursor:pointer;color:var(--mut);font-size:13px;margin-bottom:8px}}.dl{{font-size:12px;color:var(--mut);word-break:break-all}}.dl a{{color:var(--acc)}}
@media (max-width:720px){{.body{{grid-template-columns:1fr}}h1{{font-size:30px}}}}
</style></head><body><div class="wrap">
<div class="eyebrow">VIPRA STAYS · GREENWOOD FARM</div>
<h1>Social calendar: {month}</h1>
<p class="lede">One post a day for Instagram and Facebook. Each card has the creative, the caption and hashtags, and the posting time. Reply in chat with any changes (for example "swap the 14th photo" or "make the 26th about Christmas") and Claude will update this page before scheduling.</p>
<div class="summary">
<div class="box"><h2>Posts</h2><div class="big">{len(cal)}</div><div>{fmts['single']} single images · {fmts['carousel']} carousels · {fmts['reel']} reels</div></div>
<div class="box"><h2>Content mix</h2><ul>{mix}</ul></div>
<div class="box"><h2>Key dates used</h2><ul><li>Dhanteras 6 · Diwali 8 · Bhai Dooj 11</li><li>Children's Day 14</li><li>Dev Uthani Ekadashi 20 (wedding season)</li><li>Gurpurab 24</li><li>Wedding muhurats 21, 24–26 Nov; 1–4, 11–13 Dec</li></ul></div>
</div>
{''.join(cards)}
</div>
<script>document.querySelectorAll('button[data-c]').forEach(b=>b.onclick=async()=>{{const t=document.getElementById(b.dataset.c).innerText;try{{await navigator.clipboard.writeText(t);b.textContent='Copied';}}catch(e){{b.textContent='Select text';}}setTimeout(()=>b.textContent='Copy',1500)}})</script>
</body></html>'''
open(out, "w").write(page)
