// 粉紅注音小屋 service worker：每次發布請把版本號 +1
const CACHE = 'pink-zhuyin-v5';
importScripts('./audio/map.js');  // 語音音檔清單
const ASSETS = ['./', './manifest.json', './audio/map.js', './icons/icon-180.png', './icons/icon-192.png', './icons/icon-512.png',
  ...[...new Set(Object.values(self.VOICE_MAP || {}))].map(f => './audio/' + f)];

self.addEventListener('install', e => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    await Promise.all(ASSETS.map(async url => {
      try {
        const r = await fetch(url, {cache: 'reload'});
        // 被轉址的回應重新包成新的 Response，避免從主畫面開啟時 ERR_FAILED
        const body = r.redirected ? new Response(await r.blob(), {status: 200, headers: r.headers}) : r;
        if (r.ok) await c.put(url, body);
      } catch (err) {}
    }));
    self.skipWaiting();
  })());
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k !== CACHE) await caches.delete(k);
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  if (req.mode === 'navigate') {
    e.respondWith(caches.match('./').then(r => r || fetch(req)));
    return;
  }
  e.respondWith(caches.match(req).then(r => r || fetch(req)));
});
