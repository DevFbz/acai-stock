const CACHE_NAME = "acai-stock-v1";
const OFFLINE_URL = "/offline/";

const ASSETS_TO_CACHE = [
    "/",
    "/static/css/theme.css",
    "/static/css/base.css",
    "/static/js/base.js",
    "/offline/",
];

self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS_TO_CACHE).catch(() => {}))
    );
    self.skipWaiting();
});

self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
        )
    );
    self.clients.claim();
});

self.addEventListener("fetch", event => {
    if (event.request.method !== "GET") return;

    event.respondWith(
        caches.match(event.request).then(cached => {
            return fetch(event.request)
                .then(response => {
                    if (response && response.status === 200 && response.type === "basic") {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                    }
                    return response;
                })
                .catch(() => {
                    if (cached) return cached;
                    if (event.request.mode === "navigate") return caches.match(OFFLINE_URL);
                });
        })
    );
});
