const CACHE_NAME = "v1";
const urlsToCache = [
  "/",
  "/static/css/style.css",
  "/static/js/script.js",
  "/login",
  "/register",
  // Adicione mais URLs conforme necessário
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
