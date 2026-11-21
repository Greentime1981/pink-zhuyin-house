"""注音念法試聽：每個注音用好幾種寫法讓曉臻念，用耳朵挑最像老師念的那一個。
用法：python tools/voice_test.py → python -m http.server 8123 → 打開 http://localhost:8123/tools/voice_test/
挑好後按頁面下方「複製結果」，貼給 Claude（或自己改 index.html 的 SYM_RAW 第二欄）。"""
import asyncio, hashlib, json, os, re, sys
import edge_tts

VOICE, RATE, PITCH = 'zh-TW-HsiaoChenNeural', '+0%', '+0Hz'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'voice_test')
os.makedirs(OUT, exist_ok=True)

# 從 index.html 讀出目前的 符號|念法|例字
html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
raw = re.search(r'const SYM_RAW = `([^`]*)`', html).group(1)
rows = [l.split('|') for l in raw.strip().split('\n')]

# 額外候選：符號本身、符號拼寫、常見的一聲／輕聲用字
EXTRA = {
  'ㄈ': ['ㄈㄛ'], 'ㄉ': ['嘚', 'ㄉㄜ'], 'ㄊ': ['ㄊㄜ'], 'ㄋ': ['呢', 'ㄋㄜ'], 'ㄌ': ['了', 'ㄌㄜ'],
  'ㄍ': ['ㄍㄜ'], 'ㄎ': ['ㄎㄜ'], 'ㄏ': ['ㄏㄜ'], 'ㄖ': ['ㄖ'], 'ㄚ': ['阿'], 'ㄛ': ['噢'],
  'ㄜ': ['婀', '呃'], 'ㄝ': ['欸'], 'ㄟ': ['誒'], 'ㄥ': ['ㄥ'], 'ㄦ': ['ㄦ'],
}
fname = lambda t: hashlib.md5((VOICE + RATE + PITCH + t).encode()).hexdigest()[:10] + '.mp3'

groups = []
for s, say, word, *_ in rows:
    cands = []
    for c in [say, s, *EXTRA.get(s, [])]:
        if c not in cands: cands.append(c)
    groups.append({'s': s, 'word': word, 'now': say,
                   'cands': [{'c': c, 'one': c, 'line': f'{c}，{word}的{c}'} for c in cands]})
texts = sorted({t for g in groups for c in g['cands'] for t in (c['one'], c['line'])})

async def one(t, sem):
    f = os.path.join(OUT, fname(t))
    if os.path.exists(f) and os.path.getsize(f) > 0: return
    async with sem:
        for _ in range(4):
            try:
                await edge_tts.Communicate(t, VOICE, rate=RATE, pitch=PITCH).save(f)
                if os.path.getsize(f) > 0: return
            except Exception as e:
                print('重試', t, e, file=sys.stderr); await asyncio.sleep(2)
        print('失敗：' + t, file=sys.stderr)

async def main():
    sem = asyncio.Semaphore(6)
    await asyncio.gather(*(one(t, sem) for t in texts))
    for g in groups:
        for c in g['cands']: c['f1'], c['f2'] = fname(c['one']), fname(c['line'])
    page = PAGE.replace('/*DATA*/', json.dumps(groups, ensure_ascii=False))
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(page)
    print(f'完成 {len(texts)} 個試聽音檔，打開 tools/voice_test/index.html')

PAGE = r'''<!doctype html><html lang="zh-Hant-TW"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>注音念法試聽</title>
<style>
body{font-family:"PingFang TC","Noto Sans TC","Microsoft JhengHei",sans-serif;background:#fff3f7;color:#6b3a4e;margin:0;padding:16px;max-width:760px;margin:auto}
h1{font-size:1.4rem}.g{background:#fff;border-radius:14px;padding:10px 12px;margin:10px 0;box-shadow:0 3px 0 #f0a3bf}
.g h2{margin:0 0 6px;font-size:1.6rem}.g h2 small{font-size:.9rem;color:#a77a8c;font-weight:400}
label{display:flex;align-items:center;gap:8px;padding:6px 0;border-top:1px dashed #f3d0dc;flex-wrap:wrap}
label b{min-width:3.5em;font-size:1.2rem}button{border:0;border-radius:10px;background:#ffd1e1;padding:6px 10px;font-size:1rem;cursor:pointer}
.now{font-size:.8rem;color:#e5487f}#out{width:100%;height:5rem;font-size:1rem}.bar{position:sticky;bottom:0;background:#fff3f7;padding:8px 0}
</style></head><body>
<h1>🎧 注音念法試聽</h1>
<p>每個注音點 ▶ 聽聽看，選最像老師念的那一個。「單念」是只念聲音，「整句」是「ㄅ，冰淇淋的ㄅ」那樣念。<br>都不好就選「都不好」。</p>
<div id="list"></div>
<div class="bar"><button id="copy">📋 複製結果</button> <small>按下後貼給 Claude</small><br><textarea id="out" readonly></textarea></div>
<script>
const G = /*DATA*/;
const au = new Audio();
const play = f => { au.src = f; au.play(); };
document.getElementById('list').innerHTML = G.map((g, i) => `<div class="g"><h2>${g.s} <small>例字：${g.word}</small></h2>` +
  g.cands.map((c, j) => `<label><input type="radio" name="g${i}" value="${c.c}" ${c.c === g.now ? 'checked' : ''}>
   <b>${c.c}</b><button type="button" onclick="play('${c.f1}')">▶ 單念</button><button type="button" onclick="play('${c.f2}')">▶ 整句</button>
   ${c.c === g.now ? '<span class="now">目前用的</span>' : ''}</label>`).join('') +
  `<label><input type="radio" name="g${i}" value="?"><b>都不好</b></label></div>`).join('');
const result = () => G.map((g, i) => { const v = document.querySelector(`input[name=g${i}]:checked`).value; return v === g.now ? null : g.s + '=' + v; }).filter(Boolean);
const upd = () => { const r = result(); document.getElementById('out').value = '注音念法試聽結果：' + (r.length ? r.join('、') : '全部維持原本的'); };
document.addEventListener('change', upd); upd();
document.getElementById('copy').onclick = () => { const o = document.getElementById('out'); o.select(); try { navigator.clipboard.writeText(o.value); } catch (e) { document.execCommand('copy'); } };
</script></body></html>'''

asyncio.run(main())
