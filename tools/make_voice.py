"""用微軟 AI 語音（edge-tts）把所有片段做成 mp3，並寫出 audio/map.js。
用法：node tools/export_phrases.js → python tools/make_voice.py
已經做過的片段不會重做；換聲音時刪掉 audio 資料夾再跑。"""
import asyncio, hashlib, json, os, sys
import edge_tts

VOICE, RATE, PITCH = 'zh-TW-HsiaoYuNeural', '-12%', '+12Hz'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'audio')
os.makedirs(OUT, exist_ok=True)
phrases = json.load(open(os.path.join(ROOT, 'tools', 'phrases.json'), encoding='utf-8'))
fname = lambda t: hashlib.md5((VOICE + RATE + PITCH + t).encode()).hexdigest()[:10] + '.mp3'

async def one(t, sem):
    f = os.path.join(OUT, fname(t))
    if os.path.exists(f) and os.path.getsize(f) > 0: return
    async with sem:
        for tries in range(4):
            try:
                await edge_tts.Communicate(t, VOICE, rate=RATE, pitch=PITCH).save(f)
                if os.path.getsize(f) > 0: return
            except Exception as e:
                print('重試', t, e, file=sys.stderr); await asyncio.sleep(2)
        raise SystemExit('失敗：' + t)

async def main():
    sem = asyncio.Semaphore(6)
    await asyncio.gather(*(one(t, sem) for t in phrases))
    m = {t: fname(t) for t in phrases}
    keep = set(m.values())
    for f in os.listdir(OUT):
        if f.endswith('.mp3') and f not in keep: os.remove(os.path.join(OUT, f))
    with open(os.path.join(OUT, 'map.js'), 'w', encoding='utf-8') as fp:
        fp.write('// 自動產生，請勿手改（tools/make_voice.py）\nself.VOICE_MAP = ' + json.dumps(m, ensure_ascii=False) + ';\n')
    size = sum(os.path.getsize(os.path.join(OUT, f)) for f in keep)
    print(f'完成 {len(m)} 個音檔，共 {size/1024/1024:.2f} MB')

asyncio.run(main())
