// instaloader_pwa/service-worker.js - Empty service worker to force unregistration

// Immediately unregister this service worker to prevent API conflicts
self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        self.clients.claim().then(() => {
            // Unregister the service worker immediately after activation
            self.registration.unregister();
        })
    );
});