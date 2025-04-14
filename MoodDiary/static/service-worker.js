self.addEventListener('install', (e) => {
    e.waitUntil(
      caches.open('mood-diary-cache').then((cache) => {
        return cache.addAll([
          '/',
          '/dashboard',
          '/static/css/style.css',
          '/static/js/script.js',
          '/static/icon.png',
          '/mood-trends'
        ]);
      })
    );
  });
  
  self.addEventListener('fetch', (e) => {
    e.respondWith(
      caches.match(e.request).then((response) => {
        return response || fetch(e.request);
      })
    );
  });
  
  self.addEventListener('activate', (event) => {
    const cacheWhitelist = ['mood-diary-cache'];
    event.waitUntil(
      caches.keys().then((cacheNames) =>
        Promise.all(
          cacheNames.map((cacheName) => {
            if (!cacheWhitelist.includes(cacheName)) {
              return caches.delete(cacheName);
            }
          })
        )
      )
    );
  });
  