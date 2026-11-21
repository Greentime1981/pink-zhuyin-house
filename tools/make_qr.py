"""產生 QR Code 與安裝海報，並解碼驗證網址。用法：python tools/make_qr.py"""
import os, cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
URL = 'https://greentime1981.github.io/pink-zhuyin-house/'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'qr')
os.makedirs(OUT, exist_ok=True)

p = cv2.QRCodeEncoder_Params(); p.correction_level = cv2.QRCodeEncoder_CORRECT_LEVEL_M
qr = cv2.QRCodeEncoder.create(p).encode(URL)
qr = cv2.resize(qr, (qr.shape[1] * 20, qr.shape[0] * 20), interpolation=cv2.INTER_NEAREST)
qr = cv2.copyMakeBorder(qr, 40, 40, 40, 40, cv2.BORDER_CONSTANT, value=255)
qr_path = os.path.join(OUT, 'pink-zhuyin-house-qr.png')
cv2.imencode('.png', qr)[1].tofile(qr_path)

def check(path):
    img = cv2.imdecode(np.fromfile(path, np.uint8), cv2.IMREAD_COLOR)
    data, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    return data

font = next(f for f in [r'C:\Windows\Fonts\msjhbd.ttc', r'C:\Windows\Fonts\msjh.ttc'] if os.path.exists(f))
F = lambda s: ImageFont.truetype(font, s)
W, H = 1240, 1754
PINK, DEEP, TEXT, MUTE = '#ffe3ec', '#e5487f', '#6b3a4e', '#a77a8c'
poster = Image.new('RGB', (W, H), PINK); d = ImageDraw.Draw(poster)
for x in range(0, W, 60):
    for y in range(0, H, 60):
        if (x // 60 + y // 60) % 2 == 0: d.ellipse([x + 22, y + 22, x + 34, y + 34], fill='#fff2f6')
d.rounded_rectangle([40, 40, W - 40, 250], 50, fill='#ff7aa8')
d.text((W / 2, 120), '粉紅注音小屋', font=F(88), fill='white', anchor='mm')
d.text((W / 2, 205), '4～5 歲注音小遊戲・17 關・AI 真人語音・可離線', font=F(36), fill='white', anchor='mm')
icon = Image.open(os.path.join(ROOT, 'icons', 'icon-192.png')).resize((170, 170))
mask = Image.new('L', (170, 170), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, 170, 170], 38, fill=255)
poster.paste(icon, (W // 2 - 85, 285), mask)
d.rounded_rectangle([W // 2 - 310, 490, W // 2 + 310, 1110], 40, fill='white')
q = Image.open(qr_path).convert('RGB').resize((580, 580), Image.NEAREST)
poster.paste(q, (W // 2 - 290, 510))
d.text((W / 2, 1165), '用手機相機掃描 QR Code', font=F(46), fill=TEXT, anchor='mm')
d.text((W / 2, 1220), URL, font=F(30), fill=MUTE, anchor='mm')
y = 1290
for title, steps in [('iPhone／iPad（用 Safari 開啟）', ['① 點「分享」按鈕（新版 Safari 先點右下角「…」）', '② 往下滑，點「加入主畫面」', '③ 右上角點「加入」，完成！']),
                     ('Android（用 Chrome 開啟）', ['① 打開網頁，到「家長專區」點「裝到手機」', '② 按「安裝」，主畫面就會出現小貓圖示'])]:
    d.text((120, y), title, font=F(38), fill=DEEP); y += 56
    for s in steps:
        d.text((150, y), s, font=F(31), fill=TEXT); y += 46
    y += 16
d.text((W / 2, H - 50), '在 LINE／Facebook 裡開啟時，請先改用 Safari 或 Chrome。', font=F(28), fill=MUTE, anchor='mm')
poster_path = os.path.join(OUT, 'pink-zhuyin-house-poster.png')
poster.save(poster_path)

for path in (qr_path, poster_path):
    got = check(path)
    print(os.path.basename(path), 'decoded:', got, 'OK' if got == URL else 'MISMATCH')
    assert got == URL
