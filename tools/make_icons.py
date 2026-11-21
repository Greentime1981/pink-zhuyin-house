"""畫 App 圖示（原創小貓）。用法：python tools/make_icons.py"""
import os
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def draw(size):
    S = 4 * size  # 先畫大張再縮小，邊緣比較平滑
    k = S / 200
    im = Image.new('RGB', (S, S), '#ffc4d8'); d = ImageDraw.Draw(im)
    for x in range(0, S, int(30 * k)):
        for y in range(0, S, int(30 * k)):
            if (x // int(30 * k) + y // int(30 * k)) % 2 == 0:
                d.ellipse([x + 9 * k, y + 9 * k, x + 15 * k, y + 15 * k], fill='#ffd9e6')
    line, w = '#6b3a4e', int(5 * k)
    P = lambda pts: [(x * k, y * k) for x, y in pts]
    oy = 8  # 整體往下移一點
    for ear, inner in (([(42, 86), (36, 26), (88, 56)], [(50, 72), (47, 42), (74, 58)]), ([(158, 86), (164, 26), (112, 56)], [(150, 72), (153, 42), (126, 58)])):
        d.polygon(P([(x, y + oy) for x, y in ear]), fill='white', outline=line, width=w)
        d.polygon(P([(x, y + oy) for x, y in inner]), fill='#ffb3cc')
    d.ellipse(P([(30, 52 + oy), (170, 172 + oy)]), fill='white', outline=line, width=w)
    # 蝴蝶結
    cx, cy = 150, 46 + oy
    d.polygon(P([(cx, cy), (cx - 22, cy - 18), (cx - 26, cy + 10)]), fill='#ff5f97', outline=line, width=int(4 * k))
    d.polygon(P([(cx, cy), (cx + 22, cy - 6), (cx + 14, cy + 22)]), fill='#ff5f97', outline=line, width=int(4 * k))
    d.ellipse(P([(cx - 7, cy - 7), (cx + 7, cy + 7)]), fill='#ff8fb3', outline=line, width=int(4 * k))
    for ex in (76, 124):
        d.ellipse(P([(ex - 8, 96 + oy), (ex + 8, 116 + oy)]), fill=line)
        d.ellipse(P([(ex - 2, 96 + oy), (ex + 4, 102 + oy)]), fill='white')
    for cxx in (62, 138):
        d.ellipse(P([(cxx - 10, 118 + oy), (cxx + 10, 138 + oy)]), fill='#ffc2d6')
    d.polygon(P([(95, 117 + oy), (105, 117 + oy), (100, 123 + oy)]), fill='#ff7aa8')
    d.arc(P([(88, 120 + oy), (100, 132 + oy)]), 0, 180, fill=line, width=int(4 * k))
    d.arc(P([(100, 120 + oy), (112, 132 + oy)]), 0, 180, fill=line, width=int(4 * k))
    for a, b in (((30, 112), (52, 112)), ((30, 124), (52, 120)), ((170, 112), (148, 112)), ((170, 124), (148, 120))):
        d.line(P([(a[0], a[1] + oy), (b[0], b[1] + oy)]), fill=line, width=int(3.5 * k))
    return im.resize((size, size), Image.LANCZOS)

os.makedirs(os.path.join(ROOT, 'icons'), exist_ok=True)
for n in (180, 192, 512):
    draw(n).save(os.path.join(ROOT, 'icons', f'icon-{n}.png'))
    print('icon', n)
