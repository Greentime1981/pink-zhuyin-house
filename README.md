# 粉紅注音小屋

給 4～5 歲小朋友的注音小遊戲：認識 37 個注音符號 → 四個聲調 → 拼音 → 看圖讀讀看，共 17 關。

## 檔案
- `index.html`：整個 App（資料、題目產生器、畫面、音效都在這一個檔案）
- `manifest.json`、`sw.js`、`icons/`：離線使用、加到主畫面
- `audio/`：AI 語音音檔（微軟「曉臻」台灣女聲（原聲不調整），用 edge-tts 產生）與對照表 map.js
- `tools/make_icons.py`：重新畫 App 圖示

## 要改內容時
- 注音例字：`index.html` 裡的 `SYM_RAW`（符號|語音念法用字|例字|例字注音|圖）
- 聲調、拼音、字詞：`TONE_BANK`、`LIGHT`、`PIN`、`WORDS`
- 貼紙：`STICKERS`
- **改了任何會唸出來的字（例字、字詞、提示句）後**，要重做語音：
  `node tools/export_phrases.js` → `python tools/make_voice.py`（需要 `pip install edge-tts`；聲音設定在 make_voice.py 最上面）
- **每次發布前把 `sw.js` 的 `CACHE` 版本號 +1**，不然已安裝的手機會一直用舊版。

## 本機試玩
在這個資料夾執行 `python -m http.server 8123`，打開 http://localhost:8123
