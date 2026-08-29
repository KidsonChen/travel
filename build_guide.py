import re, json, os, urllib.request, time, sys

SRC = 'map.html'
OUT = 'guide.html'
IMG_DIR = 'guide_images'
os.makedirs(IMG_DIR, exist_ok=True)

html = open(SRC, encoding='utf-8').read()

# 用 Node 原生解析 JS 字面量，匯出 JSON（最穩）
node_extract = r'''
const fs=require('fs');
const html=fs.readFileSync('map.html','utf8');
const pm=html.match(/\/\* ===PLACES_START=== \*\/([\s\S]*?)\/\* ===PLACES_END=== \*\//);
const im=html.match(/const IMG = (\{[\s\S]*?\n\});/);
const PLACES = eval('('+pm[1].replace('const PLACES =','').trim().replace(/;$/,'')+')');
const IMG = eval('('+im[1]+')');
fs.writeFileSync('places.json', JSON.stringify(PLACES));
fs.writeFileSync('img.json', JSON.stringify(IMG));
console.log('extracted', PLACES.length, 'places,', Object.keys(IMG).length, 'imgs');
'''
open('_extract.js','w',encoding='utf-8').write(node_extract)
import subprocess
subprocess.run(['node','_extract.js'], check=True)
PLACES = json.load(open('places.json',encoding='utf-8'))
IMG = json.load(open('img.json',encoding='utf-8'))
open('places.json','w',encoding='utf-8').close()
open('img.json','w',encoding='utf-8').close()

# 每日車程/主題（假設 10/19 出發）
DRIVE = {
 1:  ("10/19", "布拉格老城漫步", "市區步行，無自駕車程"),
 2:  ("10/20", "城南＋河景", "市區移動，傍晚伏爾塔瓦河遊船"),
 3:  ("10/21", "城堡線：Konopiště → Tábor → Hluboká → CK", "布拉格→Konopiště 51km/0.7h→Tábor 46km/0.7h→Hluboká 59km/0.7h→CK 44km/0.6h（當日約 200km/2.0h）"),
 4:  ("10/22", "跨國 → 哈修塔特 → 薩爾斯堡", "CK→哈修塔特→薩爾斯堡 275km/4.4h"),
 5:  ("10/23", "德國國王湖天氣巡禮", "薩爾斯堡⇄國王湖 90km/1.6h（當日往返，含鷹巢）"),
 6:  ("10/24", "回程捷克 → 皮爾森啤酒之鄉", "薩爾斯堡→皮爾森 290km/4.1h"),
 7:  ("10/25", "卡爾什特因城堡 → 還車返台", "皮爾森→卡爾什特因→機場 103km/1.5h"),
}

def safe(s): return re.sub(r'[\\/:*?"<>|]', '_', s)

# 下載圖片到本地（含重試，避開 429）
def dl(url, path):
    if not url: return False
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 (travel-guide)'})
            data = urllib.request.urlopen(req, timeout=12).read()
            open(path,'wb').write(data)
            return True
        except Exception as e:
            wait = 1.5 + attempt*2
            print(f"  重試 {safe(url)[:24]} ({e}) wait {wait}s")
            time.sleep(wait)
    return False

# 建立 名稱->本地路徑 對照（按 PLACES 順序）
name2local = {}
# 不本地下載（Wikimedia 會限流）；改用縮圖參數遠端網址，瀏覽器按需載入即可
def thumb(url):
    # 用 Special:FilePath?width=800 縮圖（穩定 200，不會 400）
    if not url: return ''
    # IMG 網址的檔名已是 URL-encoded，直接取用即可（不要再 quote 一次）
    m = re.search(r'/([^/?#]+\.(?:jpg|jpeg|png|svg|JPG|JPEG|PNG|SVG))$', url)
    if m:
        fname = m.group(1)
        return 'https://commons.wikimedia.org/wiki/Special:FilePath/'+fname+'?width=800'
    return url

name2local = {}
for i,p in enumerate(PLACES):
    nm = p['name']
    remote = IMG.get(nm,'')
    name2local[nm] = thumb(remote)

print("圖片採遠端縮圖網址（不本地下載，開頁時聯網載入）:", sum(1 for v in name2local.values() if v))
IMG_LOCAL = dict(name2local)

# ---- 產生 guide.html ----
CSS = """
:root{--blue:#0B4F8C;--blue2:#1a6fc4;--ink:#222;--muted:#777;--line:#e3e8ef;--bg:#f5f7fa}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,"PingFang TC","Microsoft JhengHei",sans-serif;color:var(--ink);background:var(--bg);line-height:1.7}
a{color:var(--blue2);text-decoration:none}
.hero{background:linear-gradient(135deg,#0B4F8C,#1a6fc4 60%,#3a8fd0);color:#fff;padding:46px 20px 38px;text-align:center}
.hero h1{margin:0 0 8px;font-size:30px;letter-spacing:1px}
.hero p{margin:4px 0;opacity:.95}
.chips{margin-top:14px;display:flex;gap:8px;justify-content:center;flex-wrap:wrap}
.chip{background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.35);padding:4px 12px;border-radius:20px;font-size:13px}
.toc{position:sticky;top:0;background:#fff;border-bottom:1px solid var(--line);z-index:5;display:flex;gap:6px;padding:10px;overflow-x:auto;box-shadow:0 1px 4px rgba(0,0,0,.05)}
.toc a{flex:0 0 auto;padding:5px 12px;border-radius:18px;background:#eef6ff;color:var(--blue);font-size:13px;font-weight:600}
.day{max-width:860px;margin:26px auto;background:#fff;border:1px solid var(--line);border-radius:14px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.04)}
.day-head{background:linear-gradient(135deg,var(--blue),var(--blue2));color:#fff;padding:16px 22px}
.day-head .dnum{font-size:13px;opacity:.9;letter-spacing:2px}
.day-head h2{margin:2px 0 4px;font-size:22px}
.day-head .meta{font-size:12.5px;opacity:.95}
.day-head .drive{margin-top:6px;font-size:12.5px;background:rgba(255,255,255,.15);padding:5px 10px;border-radius:8px;display:inline-block}
.spot{display:flex;gap:14px;padding:16px 22px;border-top:1px solid var(--line)}
.spot:nth-child(odd){background:#fafcff}
.spot img{width:160px;height:120px;object-fit:cover;border-radius:10px;flex:0 0 160px;background:#eee}
.spot .body{flex:1}
.spot h3{margin:0 0 2px;font-size:16px;color:var(--blue)}
.tag{display:inline-block;font-size:11px;color:var(--muted);background:#eef2f7;border-radius:6px;padding:1px 8px;margin-bottom:6px}
.spot p{margin:4px 0 0;font-size:13.5px;color:#333}
.foot{max-width:860px;margin:30px auto;padding:20px;background:#fff;border:1px solid var(--line);border-radius:14px}
.foot h2{color:var(--blue);font-size:18px;margin-top:0}
.foot ul{margin:6px 0;padding-left:20px;font-size:13.5px}
.foot li{margin:4px 0}
.note{font-size:12px;color:var(--muted);text-align:center;margin:18px}
@media(max-width:640px){.spot{flex-direction:column}.spot img{width:100%;height:180px;flex:none}.hero h1{font-size:24px}}
"""

def esc(s): return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

days = sorted({p['day'] for p in PLACES}, key=lambda x:(x if isinstance(x,int) else 999))
toc = ''.join(f'<a href="#day{d}">Day {d}</a>' for d in days if isinstance(d,int)) + '<a href="#pocket">口袋名單</a>'

spots_html = ''
for d in days:
    if not isinstance(d,int): continue
    date, theme, drive = DRIVE.get(d, ("","",""))
    items = [p for p in PLACES if p['day']==d]
    cards = ''
    for p in items:
        local = IMG_LOCAL.get(p['name'],'')
        remote = IMG.get(p['name'],'')
        img_tag = ''
        if local:
            fb = f"this.onerror=null;this.src='{remote}'" if remote else ''
            img_tag = f'<img src="{esc(local)}" alt="{esc(p["name"])}" loading="lazy" onerror="{fb}">'
        elif remote:
            img_tag = f'<img src="{esc(remote)}" alt="{esc(p["name"])}" loading="lazy">'
        note = f'<span class="tag">{esc(p.get("note",""))}</span>' if p.get('note') else ''
        desc = f'<p>{esc(p.get("desc",""))}</p>' if p.get('desc') else ''
        cards += f'<div class="spot">{img_tag}<div class="body"><h3>{esc(p["name"])}</h3>{note}{desc}</div></div>'
    spots_html += f'''
<div class="day" id="day{d}">
  ={d}=
</div>
'''  # placeholder replaced below
    spots_html = spots_html.replace(f'={d}=', f'''<div class="day-head">
    <div class="dnum">DAY {d} ｜ {esc(date)}</div>
    <h2>{esc(theme)}</h2>
    <div class="meta">{len(items)} 個景點 / 住宿</div>
    <div class="drive">🚗 今日車程：{esc(drive)}</div>
  </div>
  {cards}''')

POCKET = r'''
<section class="foot" id="pocket">
  <h2>🎒 布拉格口袋名單（影片攻略補充）</h2>
  <p style="font-size:13px;color:#777;margin:2px 0 10px">以下整理自旅遊影片章節標記 [mm:ss]，可作為上述 Day1–Day2 的額外口袋清單；座標待補，可同步加入 <a href="map.html">map.html</a> 地圖標記。</p>
  <h3 style="color:var(--blue);font-size:15px;margin:14px 0 6px">🚉 交通</h3>
  <ul>
    <li><b>機場出市區：</b>搭 59 號巴士到機場範圍外，再轉電車或地鐵，車程約 45 分–1 小時。</li>
    <li><b>市內票券：</b>機場巴士站旁黃色售票機購票；停留 3–4 天建議買 72 小時車票，上車後插卡啟用生效。</li>
  </ul>
  <h3 style="color:var(--blue);font-size:15px;margin:14px 0 6px">🏰 景點（含影片時間戳）</h3>
  <ul>
    <li><b>天文鐘</b> — 600 多年歷史，整點 1.5 分鐘機械報時表演（耶穌門徒轉出與雞鳴）。</li>
    <li><b>火藥塔</b> — 舊城區 13 座城門唯一留存，昔日皇室入口。</li>
    <li><b>老城廣場</b>（胡斯雕像 & 泰恩教堂） — 14 世紀哥德式雙塔教堂。</li>
    <li><b>查理大橋</b> — 白天夜晚各去一次；早晨約 7 點人潮最少，橋上 30 座雕像。</li>
    <li><b>聖約翰尼波穆克雕像</b> — 撫摸底座浮雕求好運，已被摸到發亮。</li>
    <li><b>聖維特大教堂南塔觀景台</b> — 單購票登南塔，360° 俯瞰查理大橋與舊城。</li>
    <li><b>斯特拉霍夫修道院觀景台</b> — 山丘免費市景，旁有修道院自釀啤酒餐廳。</li>
    <li><b>萊特納公園觀景台</b> — 電車可達，拍橋與舊電車；後方有巨型節拍器。</li>
    <li><b>復古木船遊老運河</b> — 19 世紀「威尼斯號」，含飲品點心與耳機導覽。</li>
    <li><b>藍儂牆</b> — 小城區塗鴉象徵地標。</li>
  </ul>
  <h3 style="color:var(--blue);font-size:15px;margin:14px 0 6px">🍽️ 美食（座標待補）</h3>
  <ul>
    <li><b>Crème de la Crème 義式冰淇淋</b> — 天文鐘步行 5 分，推薦開心果、黑巧克力。</li>
    <li><b>煙囪卷 Trdelník</b> — 傳統街頭甜點，可加榛果醬或冰淇淋。</li>
    <li><b>Kuchyň（城堡區）</b> — 16 世紀貴族廚房風，烤鴨胸配紫椰菜馬鈴薯餅。</li>
    <li><b>Pork's 巨型烤豬手</b> — 新城區分店較易入座，約 800 克朗兩人分食。</li>
    <li><b>Naše Maso（舊城區肉舖）</b> — 招牌布拉格火腿／煙燻牛胸肉三明治，設自助點餐機。</li>
  </ul>
</section>
'''

guide = f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>奧捷＋德國國王湖 · 7天自駕攻略</title>
<style>{CSS}</style>
</head>
<body>
<header class="hero">
  <h1>🇨🇿🇦🇹 奧捷＋德國國王湖 · 7天自駕攻略</h1>
  <p>4 人同行 ｜ 10 月賞楓自駕 ｜ 布拉格 → CK → 哈修塔特 → 薩爾斯堡 → 國王湖 → 皮爾森</p>
  <div class="chips">
    <span class="chip">🚗 全程自駕</span>
    <span class="chip">📅 7 天 6 夜</span>
    <span class="chip">🍁 10月賞楓</span>
    <span class="chip">👥 4 人</span>
  </div>
</header>
<nav class="toc">{toc}</nav>
{spots_html}
{POCKET}
<section class="foot">
  <h2>📌 實用資訊</h2>
  <ul>
    <li><b>自駕租車：</b>4人含跨國（Cross-Border 允許奧/德），全包約 NT$7,000/人（租車＋全險＋油資＋過路費）。</li>
    <li><b>奧地利 Vignette：</b>10日 €10.20（ASFINAG 官網/加油站，貼擋風玻璃）；德國小客車免費。</li>
    <li><b>捷克 e-vignette：</b>10日 310 Kč ≈ €12（車牌連結，行前在 edalnice.cz 線上購買；本程 D1/D5/D6/D7 多在捷克高速，必備）。</li>
    <li><b>停車：</b>哈修塔特付費場(P1/P2)+接駁；國王湖大停車場；奧伊根多夫/安德區住宿附停車。</li>
    <li><b>住宿評價：</b>四間皆優（布拉格9.7 / CK 8.8 / 薩爾斯堡9.5 / 皮爾森9.1），無明顯負評。</li>
    <li><b>必帶：</b>台灣駕照正本＋國際駕照(IDP)＋護照＋本人信用卡。</li>
  </ul>
  <p class="note">日期以 10/19 出發推算（D1=10/19…D7=10/25）。地圖與可編輯版本請見 <a href="map.html">map.html</a>。</p>
</section>
<p class="note">本攻略由 map.html 資料自動產生 ｜ 圖片來源：Wikimedia Commons（免費授權）</p>
</body>
</html>'''

open(OUT,'w',encoding='utf-8').write(guide)
print("已產生", OUT, "大小", os.path.getsize(OUT), "bytes")
