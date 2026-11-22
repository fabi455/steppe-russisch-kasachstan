const CACHE = 'steppe-russisch-offline-v3-grosswoerterbuch';
const CORE = ['./','./index.html','./app.js','./style.css','./content.js','./dictionary/ui.js','./dictionary/ru-de.js','./manifest.webmanifest','./icons/icon-192.png','./icons/icon-512.png'];
self.addEventListener('install',event=>{
  event.waitUntil((async()=>{
    const cache=await caches.open(CACHE);
    await cache.addAll(CORE);
    try {
      const response=await fetch('./content.json');
      const lessons=await response.json();
      const names=[...new Set(lessons.flatMap(l=>[...l.words,...l.phrases].map(w=>w.id)))];
      await Promise.allSettled(names.map(id=>cache.add('./audio/'+id+'.mp3')));
    } catch(e) { /* Core learning UI remains cached. */ }
    await self.skipWaiting();
  })());
});
self.addEventListener('activate',event=>event.waitUntil((async()=>{
  for(const name of await caches.keys())if(name!==CACHE)await caches.delete(name);
  await self.clients.claim();
})()));
self.addEventListener('fetch',event=>{
  if(event.request.method!=='GET')return;
  const url=new URL(event.request.url);
  if(url.origin!==self.location.origin)return;
  event.respondWith((async()=>{
    const cached=await caches.match(event.request);
    if(cached)return cached;
    try {return await fetch(event.request);}catch {return new Response('Offline-Datei nicht verfügbar',{status:503});}
  })());
});
