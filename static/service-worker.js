const CACHE_NAME = "app-cache-v1";
const urlsToCache = [
  "/",
  "/static/css/style.css",
  "/static/js/script.js",
  "/login",
  "/register",
  "/favicon.ico", // Recomendado adicionar
  "/manifest.json", // Recomendado para PWA
  // Adicione mais URLs conforme necessário
];

// Evento de instalação
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("Abrindo cache:", CACHE_NAME);
      return cache.addAll(urlsToCache);
    })
  );
});

// Evento de ativação (limpeza de caches antigos)
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log("Removendo cache antigo:", cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
});

// Evento de busca
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) {
        console.log("Respondendo do cache:", event.request.url);
        return response;
      }
      console.log("Buscando do servidor:", event.request.url);
      return fetch(event.request);
    })
  );
});
