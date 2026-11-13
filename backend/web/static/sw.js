const CACHE_NAME = 'medicare-cache-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/login',
  '/static/css/style.css',
  '/static/vendor/bootstrap.min.css',
  '/static/vendor/bootstrap-icons.min.css',
  '/static/vendor/chart.umd.min.js',
  '/static/vendor/bootstrap.bundle.min.js',
  '/static/sounds/alarm_chime.wav'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
