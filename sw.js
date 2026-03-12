const CACHE = 'afp-v1';

const PRECACHE = [
  '/',
  '/index.html',
  '/fonts/playfair-display-700-latin.woff2',
  '/fonts/playfair-display-700-latin-ext.woff2',
  '/fonts/dm-sans-400-latin.woff2',
  '/fonts/dm-sans-400-latin-ext.woff2',
  '/images/og-homepage.jpg',
  '/guides/',
  '/guides/separation-anxiety.html',
  '/guides/calming-chews.html',
  '/guides/thundershirt-review.html',
  '/guides/nighttime-anxiety.html',
  '/breeds/golden-retriever.html',
  '/breeds/french-bulldog.html',
  '/breeds/poodle.html',
  '/breeds/german-shepherd.html',
  '/breeds/labrador-retriever.html',
];

// Install — precache core assets
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(PRECACHE))
      .then(() => self.skipWaiting())
  );
});

// Activate — purge old caches
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Fetch strategy:
//   Fonts/images → cache-first (long-lived, never changes)
//   HTML pages   → network-first with cache fallback
//   Everything else → stale-while-revalidate
self.addEventListener('fetch', e => {
  const { request } = e;
  const url = new URL(request.url);

  // Only handle same-origin requests
  if (url.origin !== location.origin) return;

  const isFontOrImage = /\.(woff2?|ttf|otf|jpg|jpeg|png|webp|svg|ico)$/i.test(url.pathname);
  const isHTML = request.headers.get('accept')?.includes('text/html');

  if (isFontOrImage) {
    // Cache-first
    e.respondWith(
      caches.match(request).then(cached => cached || fetch(request).then(res => {
        const clone = res.clone();
        caches.open(CACHE).then(c => c.put(request, clone));
        return res;
      }))
    );
  } else if (isHTML) {
    // Network-first
    e.respondWith(
      fetch(request)
        .then(res => {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(request, clone));
          return res;
        })
        .catch(() => caches.match(request))
    );
  } else {
    // Stale-while-revalidate
    e.respondWith(
      caches.open(CACHE).then(cache =>
        cache.match(request).then(cached => {
          const network = fetch(request).then(res => {
            cache.put(request, res.clone());
            return res;
          });
          return cached || network;
        })
      )
    );
  }
});
