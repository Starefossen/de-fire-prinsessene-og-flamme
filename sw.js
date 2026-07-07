const CACHE_NAME = 'prinsessene-v1';
const ASSETS = ["./","./index.html","./manifest.json","./bilder/persongalleri.png","./bilder/kap8-3.png","./bilder/kap8-2.png","./bilder/kap8-1.png","./bilder/kap10-2.png","./bilder/kap9-1.png","./bilder/kap10-3.png","./bilder/kap10-1.png","./bilder/kap9-3.png","./bilder/kap9-2.png","./bilder/kap10-4.png","./bilder/kap10-5.png","./bilder/kap9-4.png","./bilder/kap3-2.png","./bilder/kap3-3.png","./bilder/kap1-1.png","./bilder/kap1-3.png","./bilder/kap3-1.png","./bilder/kap1-2.png","./bilder/kap7-4.png","./bilder/kap5-2.png","./bilder/kap7-1.png","./bilder/kap5-3.png","./bilder/kap5-1.png","./bilder/kap7-3.png","./bilder/kap7-2.png","./bilder/forside.png","./bilder/kap2-1.png","./bilder/kap2-2.png","./bilder/kap2-3.png","./bilder/kap6-3.png","./bilder/kap4-1.png","./bilder/kap6-2.png","./bilder/kap4-2.png","./bilder/kap4-3.png","./bilder/kap6-1.png"];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
