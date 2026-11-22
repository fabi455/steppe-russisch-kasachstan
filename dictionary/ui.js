/* Steppe 1.2 – großes, offline durchsuchbares russisch-deutsches Wörterbuch. */
(() => {
  'use strict';
  let words = null, loading = false, loadError = '';
  let query = '', part = 'all', maxResults = 50, debounce;
  const POS = ['Substantiv','Verb','Adjektiv','Sonstiges'];
  const $ = id => document.getElementById(id);
  const escapeHtml = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fold = s => String(s ?? '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('de').replace(/ё/g,'е');
  const isHere = () => location.hash.startsWith('#/lexicon');
  const state = () => window.STEPPE_LEXICON_STATE;
  const saved = () => new Set(state()?.favorites?.() || []);
  const count = () => words?.length || window.STEPPE_LEXICON_META?.count || 0;

  function requestData() {
    if (Array.isArray(window.STEPPE_LEXICON)) { words = window.STEPPE_LEXICON; return; }
    if (loading) return;
    loading = true; loadError = '';
    const script = document.createElement('script');
    script.src = 'dictionary/ru-de.js';
    script.async = true;
    script.onload = () => {
      loading = false;
      if (Array.isArray(window.STEPPE_LEXICON) && window.STEPPE_LEXICON.length >= 50000) {
        words = window.STEPPE_LEXICON;
        loadError = '';
      } else {
        loadError = 'Die Wörterbuchdatei ist unvollständig. Bitte die neueste App installieren.';
      }
      if (isHere()) window.dispatchEvent(new Event('hashchange'));
    };
    script.onerror = () => {
      loading = false;
      loadError = 'Wörterbuchdatei nicht verfügbar. Öffne die vollständige Steppe-App oder starte den Wörterbuch-Build.';
      if (isHere()) window.dispatchEvent(new Event('hashchange'));
    };
    document.head.appendChild(script);
  }

  function page() {
    if (!words) {
      if (!loadError) requestData();
      return `<div class="page-intro"><div class="eyebrow">NEU · GROSSES WÖRTERBUCH</div><h1>Russisch von A bis Я.</h1>
      <p>${loadError ? escapeHtml(loadError) : 'Die große russisch-deutsche Offline-Wortliste wird geladen …'}</p></div>
      <div class="panel" style="max-width:740px"><button class="btn btn-outline" data-nav="dictionary">← Zurück zum Lernwörterbuch</button>
      ${loadError ? '<button class="btn btn-dark" data-lex-retry style="margin-left:8px">Erneut versuchen</button>' : ''}</div>`;
    }
    return `<div class="page-intro"><div class="eyebrow">NEU · OFFLINE-WÖRTERBUCH · DEUTSCH ⇄ RUSSISCH</div>
      <h1>Russisch von A bis Я.</h1>
      <p><strong>${count().toLocaleString('de-DE')} russische Wörter</strong> mit deutscher Bedeutung. Suche auf Kyrillisch oder Deutsch und speichere neue Vokabeln in deiner Merkliste.</p></div>
      <div class="dictionary-tools">
        <input class="search" id="lexicon-search" autocomplete="off" spellcheck="false" placeholder="z. B. привет, Stadt, lieben …" aria-label="In allen russischen Wörtern suchen"/>
        <select class="filter" id="lexicon-part" aria-label="Wortart auswählen">
          <option value="all">Alle Wortarten</option>
          <option value="0">Substantive</option><option value="1">Verben</option><option value="2">Adjektive</option><option value="3">Sonstige Wörter</option>
          <option value="saved">♥ Meine Merkliste</option>
        </select>
      </div>
      <div class="word-grid" id="lexicon-results" aria-live="polite"></div>
      <div style="margin:18px 0 26px"><button class="btn btn-outline" id="lexicon-more" data-lex-more hidden>Weitere Wörter anzeigen</button></div>
      <div class="panel" style="max-width:900px">
        <h3>Wortschatz &amp; Aussprache</h3>
        <p class="small muted">Die ${count().toLocaleString('de-DE')} Einträge sind ein Nachschlagewerk mit Grundformen. Beugungen und Übersetzungsnuancen sind nicht immer vollständig. Für die 128 Lernkarten und Beispielsätze gibt es die bekannten offline verfügbaren Neural-Hörproben. Für die zusätzlichen Wörter sind derzeit keine individuellen Audioaufnahmen enthalten.</p>
        <p class="small muted">Wörterbuchdaten: <a href="https://de.openrussian.org/dictionary-data" target="_blank" rel="noopener noreferrer">OpenRussian.org</a> / Badestrand – CC BY-SA 4.0. Änderungen: Auswahl, Zusammenführung und kompaktes Anzeigeformat. Nicht amtlich; Kasachisch bleibt eine eigenständige Sprache.</p>
        <button class="btn btn-outline" data-nav="dictionary">← Lernwörterbuch öffnen</button>
      </div>`;
  }

  function refresh() {
    const input = $('lexicon-search');
    const list = $('lexicon-results');
    if (!words || !input || !list) return;
    input.value = query;
    $('lexicon-part').value = part;
    updateResults();
  }

  function updateResults() {
    const list = $('lexicon-results');
    if (!list || !words) return;
    const q = fold(query.trim());
    const favorites = saved();
    const matched = [];
    for (const row of words) {
      const ru = row[0], de = row[2], pos = row[3];
      if (part === 'saved') { if (!favorites.has(ru)) continue; }
      else if (part !== 'all' && Number(part) !== pos) continue;
      const r = fold(ru), d = fold(de);
      if (q && !r.includes(q) && !d.includes(q)) continue;
      const rank = !q ? 9 : r===q ? 0 : r.startsWith(q) ? 1 : d.startsWith(q) ? 2 : r.includes(q) ? 3 : 4;
      matched.push([row,rank]);
    }
    if (q) matched.sort((a,b)=>a[1]-b[1] || a[0][0].localeCompare(b[0][0],'ru'));
    const total = matched.length, shown = matched.slice(0,maxResults);
    const summary = `<div class="small muted" style="grid-column:1/-1;padding:8px 2px">
      <strong>${total.toLocaleString('de-DE')}</strong> ${q || part==='saved' ? 'Treffer' : 'Wörter'} · ${Math.min(total,maxResults).toLocaleString('de-DE')} angezeigt
    </div>`;
    list.innerHTML = summary + (total ? shown.map(([row]) => {
      const [ru,accent,de,pos] = row, star = favorites.has(ru);
      return `<article class="word-row lexicon-entry">
        <div style="min-width:0">
          <div class="nor" lang="ru">${escapeHtml(ru)}</div>
          ${accent && accent!==ru ? `<div class="lexicon-stress" lang="ru">${escapeHtml(accent)}</div>` : ''}
          <div class="de">${escapeHtml(de)}</div>
          <div class="romanization">${POS[pos] || 'Wort'}</div>
        </div>
        <button class="btn-icon" data-lex-favorite="${escapeHtml(ru)}"
          aria-label="${star ? 'Aus Merkliste entfernen' : 'Zur Merkliste hinzufügen'}"
          title="${star ? 'Gemerkt' : 'Merken'}">${star ? '♥' : '♡'}</button>
      </article>`;
    }).join('') : '<div class="empty-state">Keine passenden Wörter. Probiere eine Grundform oder einen anderen Suchbegriff.</div>');
    const more = $('lexicon-more');
    if (more) more.hidden = total <= maxResults;
  }

  document.addEventListener('input', e => {
    if (e.target.id !== 'lexicon-search') return;
    query = e.target.value; maxResults = 50;
    clearTimeout(debounce);
    debounce = setTimeout(updateResults, 110);
  });
  document.addEventListener('change', e => {
    if (e.target.id !== 'lexicon-part') return;
    part = e.target.value; maxResults = 50; updateResults();
  });
  document.addEventListener('click', e => {
    const t = e.target.closest('button');
    if (!t) return;
    if (t.hasAttribute('data-lex-favorite')) {
      state()?.toggle?.(t.getAttribute('data-lex-favorite'));
      updateResults();
    } else if (t.hasAttribute('data-lex-more')) {
      maxResults += 50; updateResults();
    } else if (t.hasAttribute('data-lex-retry')) {
      loadError = ''; requestData(); if (isHere()) window.dispatchEvent(new Event('hashchange'));
    }
  });
  window.STEPPE_EXT = {page,postRender:refresh};
})();
