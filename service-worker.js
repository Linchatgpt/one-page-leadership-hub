const CACHE_NAME = 'leadership-hub-shell-v1';
const STATIC_SHELL = [
  './', './index.html', './assets/article-learning.css', './assets/article-learning.js',
  './manifest.webmanifest', './assets/icon-192.png', './assets/icon-512.png', './assets/apple-touch-icon.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(
    keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
  )));
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  const excludedPrefixes = ['/api/', '/.netlify/functions/', '/audio_summaries/', '/uploads/', '/account', '/login', '/logout', '/membership', '/checkout', '/billing', '/subscribe'];
  const dynamic = excludedPrefixes.some((prefix) => url.pathname.startsWith(prefix));
  if (request.method !== 'GET' || url.origin !== self.location.origin || dynamic) return;
  event.respondWith(fetch(request).then((response) => {
    if (response.ok && response.type === 'basic') {
      const copy = response.clone();
      caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
    }
    return response;
  }).catch(() => caches.match(request).then((cached) => cached || caches.match('./index.html'))));
});
