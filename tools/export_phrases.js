// 從 index.html 取出所有要唸的片段，存成 tools/phrases.json。用法：node tools/export_phrases.js
const fs = require('fs'), path = require('path');
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
let js = html.slice(html.indexOf("'use strict';"), html.lastIndexOf('</script>'));
js = js.slice(0, js.indexOf('// ---------- 啟動 ----------'));
const window = {addEventListener(){}}, document = {addEventListener(){}};
const out = new Function('window', 'document', js + '\nreturn allPhrases();')(window, document);
fs.writeFileSync(path.join(__dirname, 'phrases.json'), JSON.stringify(out, null, 1));
console.log('片段數：', out.length);
