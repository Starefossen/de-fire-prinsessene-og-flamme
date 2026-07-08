const CACHE_NAME = 'prinsessene-v1783520479';
const ASSETS = ["./","./index.html","./manifest.json","./bilder/persongalleri.jpg","./bilder/kap8-3.jpg","./bilder/kap8-2.jpg","./bilder/portrett-astrid.jpg","./bilder/kap8-1.jpg","./bilder/kap10-2.jpg","./bilder/kap10-3.jpg","./bilder/kap9-1.jpg","./bilder/kap9-3.jpg","./bilder/portett-hanna.jpg","./bilder/kap10-1.jpg","./bilder/portett-ellie.jpg","./bilder/kap9-2.jpg","./bilder/kap10-4.jpg","./bilder/kap10-5.jpg","./bilder/kap9-4.jpg","./bilder/kap3-2.jpg","./bilder/kap1-1.jpg","./bilder/kap3-3.jpg","./bilder/kap3-1.jpg","./bilder/kap1-3.jpg","./bilder/kap1-2.jpg","./bilder/kap7-4.jpg","./bilder/kap5-2.jpg","./bilder/portett-flamme.jpg","./bilder/kap5-3.jpg","./bilder/kap7-1.jpg","./bilder/kap7-3.jpg","./bilder/kap5-1.jpg","./bilder/portett-andre.jpg","./bilder/kap7-2.jpg","./bilder/kap2-1.jpg","./bilder/forside.jpg","./bilder/kap2-2.jpg","./bilder/kap2-3.jpg","./bilder/kap4-1.jpg","./bilder/portett-ela.jpg","./bilder/kap6-3.jpg","./bilder/kap6-2.jpg","./bilder/kap4-2.jpg","./bilder/kap6-1.jpg","./bilder/kap4-3.jpg"];

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
