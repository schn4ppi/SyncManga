// SyncManga PWA Service-Worker: network-first, faellt offline auf den Cache zurueck.
// Aktiv nur, wenn die Liste ueber http(s) ausgeliefert wird (Server) - auf file:// inaktiv.
// v2 (22.07.2026): Seitenabrufe umgehen den HTTP-Cache (no-store) - der Browser darf nie
// wieder still eine alte Fassung servieren; alte Cache-Generationen werden beim Aktivieren
// geloescht (die Wurzel des "Strg+F5 noetig"-Problems).
const CACHE = 'syncmanga-v2';

self.addEventListener('install', e => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(
  caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim())
));

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  // Seiten (Navigation/HTML) IMMER frisch vom Netz; Nebenressourcen mit Revalidierung.
  const frisch = e.request.mode === 'navigate' || e.request.destination === 'document';
  e.respondWith(
    fetch(e.request, { cache: frisch ? 'no-store' : 'no-cache' })
      .then(r => { const c = r.clone(); caches.open(CACHE).then(x => x.put(e.request, c)); return r; })
      .catch(() => caches.match(e.request))
  );
});
