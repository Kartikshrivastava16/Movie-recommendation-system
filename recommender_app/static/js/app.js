/* ═══════════════════════════════════════════════════════════════
   CineMatch — app.js  v2  (Django API Integration)
   Server: http://127.0.0.1:8000
   ═══════════════════════════════════════════════════════════════ */

'use strict';

// Base URL — all API calls go to http://127.0.0.1:8000
const API = 'http://127.0.0.1:8000';

const S = {
  movies:    [],
  users:     [],
  algo:      'collab',
  userId:    1,
  seedMovie: null,
  topN:      8,
  genres:    new Set(),
  view:      'grid',
  ready:     false,
};

const $ = id => document.getElementById(id);
const $$ = s  => document.querySelectorAll(s);

// ── Boot ──────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  loadAllData();
  bindUI();
});

async function loadAllData() {
  try {
    setStatus('loading', 'Fetching data from server…');

    const [statsRes, moviesRes, usersRes] = await Promise.all([
      fetch(`${API}/api/data/stats`),
      fetch(`${API}/api/data/movies`),
      fetch(`${API}/api/data/users`),
    ]);

    if (!statsRes.ok || !moviesRes.ok || !usersRes.ok) {
      throw new Error('Server returned an error — is Django running?');
    }

    const stats  = await statsRes.json();
    const movies = await moviesRes.json();
    const users  = await usersRes.json();

    S.movies = movies.map(m => ({
      ...m,
      genreList: (m.genres || []).map ? m.genres : String(m.genres || '').split('|').filter(Boolean),
    }));

    S.users = users;
    S.ready = true;

    const fmtNum = n => n >= 1000 ? (n / 1000).toFixed(1) + 'K' : n;
    setStatus('ready', `${stats.movies_count} movies · ${stats.users_count} users`);
    $('st-movies').textContent  = fmtNum(stats.movies_count);
    $('st-users').textContent   = fmtNum(stats.users_count);
    $('st-ratings').textContent = fmtNum(stats.ratings_count);

    buildUserSelect();
    buildGenreCloud();
    $('metricsPanel').style.display = 'block';

  } catch (e) {
    console.error(e);
    setStatus('error', 'Connection failed — run: python manage.py runserver');
  }
}

function setStatus(type, msg) {
  const dot = $('statusPill').querySelector('.status-dot');
  dot.className = `status-dot ${type}`;
  $('statusText').textContent = msg;
}

// ── Build UI ──────────────────────────────────────────────────────────────────

function buildUserSelect() {
  const sel = $('userSelect');
  sel.innerHTML = S.users.map(u =>
    `<option value="${u.user_id}">User ${u.user_id} — ${u.name}</option>`
  ).join('');
  sel.value = 1;
  S.userId = 1;
  updateUserInfo(1);
}

function updateUserInfo(uid) {
  const u    = S.users.find(u => u.user_id === uid);
  const info = $('userInfo');
  if (!u) { info.classList.remove('show'); return; }
  info.innerHTML = `<b>${u.name}</b> &nbsp;·&nbsp; Age ${u.age} &nbsp;·&nbsp; ${u.gender === 'F' ? 'Female' : 'Male'}<br/>
    Genres: ${String(u.favorite_genres).replace(/\|/g, ', ')}`;
  info.classList.add('show');
}

function buildGenreCloud() {
  const all = [...new Set(S.movies.flatMap(m =>
    Array.isArray(m.genreList) ? m.genreList : String(m.genreList || '').split('|')
  ))].sort();
  const cloud = $('genreCloud');
  cloud.innerHTML = all.map(g =>
    `<button class="genre-chip" data-g="${g}">${g}</button>`
  ).join('');
  cloud.querySelectorAll('.genre-chip').forEach(btn => {
    btn.addEventListener('click', () => {
      btn.classList.toggle('active');
      const g = btn.dataset.g;
      S.genres.has(g) ? S.genres.delete(g) : S.genres.add(g);
    });
  });
}

// ── Bind UI ───────────────────────────────────────────────────────────────────

const ALGO_DESC = {
  collab:  "Finds users with similar rating patterns, then recommends highly-rated movies from those users that you haven't seen yet.",
  content: "Recommends movies similar to a seed movie using TF-IDF on genres, director, and cast.",
  hybrid:  "Blends Collaborative Filtering and Content-Based scores (60% CF + 40% content) for better accuracy.",
};

const LOADING_MSGS = {
  collab:  ['Building user–movie matrix…', 'Computing similarity…', 'Ranking picks…'],
  content: ['Vectorising metadata…', 'Computing cosine similarity…', 'Ranking films…'],
  hybrid:  ['Computing CF scores…', 'Merging content signals…', 'Ranking picks…'],
};

function bindUI() {
  // Algorithm radio
  $$('.algo-opt').forEach(opt => {
    opt.addEventListener('click', () => {
      $$('.algo-opt').forEach(o => o.classList.remove('active'));
      opt.classList.add('active');
      opt.querySelector('input').checked = true;
      S.algo = opt.dataset.algo;
      $('algoDesc').textContent = ALGO_DESC[S.algo];
      $('seedCard').classList.toggle('hidden', S.algo !== 'content');
      $('userPickerCard').classList.toggle('hidden', S.algo === 'content');
    });
  });

  // User select
  $('userSelect').addEventListener('change', e => {
    S.userId = +e.target.value;
    updateUserInfo(S.userId);
  });

  // Top-N slider
  $('topN').addEventListener('input', e => {
    S.topN = +e.target.value;
    $('topNVal').textContent = e.target.value;
  });

  // Seed movie autocomplete
  const seedInput = $('seedInput');
  const seedDrop  = $('seedDrop');

  seedInput.addEventListener('input', () => {
    const q = seedInput.value.toLowerCase();
    if (!q) { seedDrop.classList.remove('open'); return; }
    const matches = S.movies.filter(m => m.title.toLowerCase().includes(q)).slice(0, 8);
    seedDrop.innerHTML = matches.map(m =>
      `<div class="seed-item" data-id="${m.movie_id}">${m.title} <span style="color:var(--muted);font-size:11px;">(${m.year})</span></div>`
    ).join('');
    seedDrop.classList.toggle('open', matches.length > 0);
  });

  seedDrop.addEventListener('click', e => {
    const item = e.target.closest('.seed-item');
    if (!item) return;
    const movie = S.movies.find(m => m.movie_id === +item.dataset.id);
    if (movie) {
      S.seedMovie = movie;
      seedInput.value = movie.title;
      seedDrop.classList.remove('open');
      $('seedInfo').innerHTML = `<b>${Array.isArray(movie.genres) ? movie.genres.join(' · ') : String(movie.genres || '').replace(/\|/g, ' · ')}</b><br/>Dir: ${movie.director}`;
    }
  });

  document.addEventListener('click', e => {
    if (!e.target.closest('.seed-wrap')) seedDrop.classList.remove('open');
  });

  // Run button
  $('runBtn').addEventListener('click', () => {
    if (!S.ready) { alert('Data is still loading. Please wait.'); return; }
    run();
  });

  // View toggle
  $$('.view-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      $$('.view-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      S.view = btn.dataset.view;
      $('cardsWrap').className = 'cards-wrap' + (S.view === 'list' ? ' list' : '');
    });
  });

  // Hero search
  function doSearch() {
    const q = $('heroSearch').value.trim();
    if (!q) return;
    fetch(`${API}/api/search?q=${encodeURIComponent(q)}`)
      .then(r => r.json())
      .then(results => {
        renderCards(results.slice(0, S.topN), `Search: "${q}"`, `${results.length} result(s) found`);
        document.querySelector('.main').scrollIntoView({ behavior: 'smooth' });
      });
  }
  $('heroSearchBtn').addEventListener('click', doSearch);
  $('heroSearch').addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(); });
  $$('.ql').forEach(q => q.addEventListener('click', () => {
    $('heroSearch').value = q.dataset.q;
    doSearch();
  }));

  // Nav tabs
  $$('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      $$('.tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const t = tab.dataset.tab;
      if (t !== 'discover') {
        const optEl = document.querySelector(`.algo-opt[data-algo="${t}"]`);
        if (optEl) optEl.click();
      }
      document.querySelector('.main').scrollIntoView({ behavior: 'smooth' });
    });
  });

  // Modal close
  $('modalClose').addEventListener('click', closeModal);
  $('modalBg').addEventListener('click', e => { if (e.target === $('modalBg')) closeModal(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
}

// ── Run recommendations ───────────────────────────────────────────────────────

async function run() {
  showLoading(true);
  const msgs = LOADING_MSGS[S.algo];
  let i = 0;
  $('loadingMsg').textContent = msgs[0];
  const iv = setInterval(() => { i = (i + 1) % msgs.length; $('loadingMsg').textContent = msgs[i]; }, 700);

  let results = [], title = '', sub = '';

  try {
    if (S.algo === 'collab') {
      const res = await fetch(`${API}/api/recommend/collaborative/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: S.userId, top_n: S.topN, genres: [...S.genres] }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      results = data.recommendations;
      title   = `Top Picks for ${userName(S.userId)}`;
      sub     = `${data.algorithm} · ${results.length} results`;

    } else if (S.algo === 'content') {
      if (!S.seedMovie) { alert('Please select a seed movie first.'); throw new Error('No seed'); }
      const res = await fetch(`${API}/api/recommend/content-based/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seed_movie: S.seedMovie.title, top_n: S.topN, genre_filter: [...S.genres] }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      results = data.recommendations;
      title   = `Similar to "${S.seedMovie.title}"`;
      sub     = `${data.algorithm} · ${results.length} results`;

    } else if (S.algo === 'hybrid') {
      const res = await fetch(`${API}/api/recommend/hybrid/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: S.userId, top_n: S.topN, genres: [...S.genres] }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      results = data.recommendations;
      title   = `Hybrid Picks for ${userName(S.userId)}`;
      sub     = `${data.algorithm} · ${results.length} results`;
    }
  } catch (e) {
    console.error(e);
    clearInterval(iv);
    showLoading(false);
    if (e.message !== 'No seed') alert('Error: ' + e.message);
    return;
  }

  clearInterval(iv);
  showLoading(false);
  renderCards(results, title, sub);
}

function userName(uid) {
  const u = S.users.find(u => u.user_id === uid);
  return u ? u.name : `User ${uid}`;
}

// ── Render ────────────────────────────────────────────────────────────────────

function showLoading(show) {
  $('loadingCover').classList.toggle('hidden', !show);
}

const POSTER_ARTS = [
  `<svg width="80" height="80" viewBox="0 0 80 80" fill="none" stroke="currentColor" stroke-width="1" opacity="0.12"><circle cx="40" cy="40" r="35"/><circle cx="40" cy="40" r="22"/><circle cx="40" cy="40" r="9"/><line x1="40" y1="5" x2="40" y2="75"/><line x1="5" y1="40" x2="75" y2="40"/></svg>`,
  `<svg width="80" height="80" viewBox="0 0 80 80" fill="none" stroke="currentColor" stroke-width="1" opacity="0.12"><polygon points="40,5 75,70 5,70"/><polygon points="40,20 63,65 17,65"/></svg>`,
  `<svg width="80" height="80" viewBox="0 0 80 80" fill="none" stroke="currentColor" stroke-width="1" opacity="0.12"><rect x="10" y="10" width="60" height="60"/><rect x="22" y="22" width="36" height="36"/><rect x="34" y="34" width="12" height="12"/></svg>`,
  `<svg width="80" height="80" viewBox="0 0 80 80" fill="none" stroke="currentColor" stroke-width="1" opacity="0.12"><path d="M40 5 L75 40 L40 75 L5 40 Z"/><path d="M40 18 L62 40 L40 62 L18 40 Z"/></svg>`,
];

function renderCards(movies, title, subtitle) {
  $('resultsTitle').textContent = title;
  $('resultsSub').textContent   = subtitle;

  if (!movies || movies.length === 0) {
    $('cardsWrap').innerHTML = `
      <div class="empty-state">
        <div class="empty-icon"><svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m10 9 5 3-5 3V9z"/></svg></div>
        <div class="empty-title">No results</div>
        <div class="empty-sub">Try different settings or filters</div>
      </div>`;
    return;
  }

  $('cardsWrap').className = 'cards-wrap' + (S.view === 'list' ? ' list' : '');
  $('cardsWrap').innerHTML = movies.map((m, idx) => {
    const genres = Array.isArray(m.genres) ? m.genres.join(' · ') : String(m.genres || '').replace(/\|/g, ' · ');
    const cast   = Array.isArray(m.cast)   ? m.cast.slice(0, 3).join(', ') : String(m.cast || '').split('|').slice(0, 3).join(', ');
    const art    = POSTER_ARTS[idx % POSTER_ARTS.length];
    return `
      <div class="movie-card" data-idx="${idx}" style="animation-delay:${idx * 40}ms">
        <div class="card-poster">
          <div class="poster-art">${art}</div>
          <div class="poster-num">${String(idx + 1).padStart(2, '0')}</div>
          <div class="poster-rating">★ ${m.rating_avg ? Number(m.rating_avg).toFixed(1) : 'N/A'}</div>
        </div>
        <div class="card-body">
          <h3 class="card-title">${m.title}</h3>
          <p class="card-genres">${genres}</p>
          <p class="card-meta"><b>${m.director}</b> · ${m.year}</p>
          <p class="card-desc">${m.description || ''}</p>
          <p class="card-cast">${cast}</p>
        </div>
      </div>`;
  }).join('');

  $$('.movie-card').forEach(card => {
    card.addEventListener('click', () => {
      const movie = movies[+card.dataset.idx];
      if (movie) openModal(movie);
    });
  });
}

function openModal(m) {
  const genres = Array.isArray(m.genres) ? m.genres.join(', ') : String(m.genres || '').replace(/\|/g, ', ');
  const cast   = Array.isArray(m.cast)   ? m.cast.join(', ')   : String(m.cast || '').replace(/\|/g, ', ');
  const rating = m.rating_avg ? Number(m.rating_avg).toFixed(1) : 'N/A';
  $('modalBody').innerHTML = `
    <div class="modal-accent-bar"></div>
    <div class="modal-header">
      <h2>${m.title}</h2>
      <p class="modal-year">${m.year} · ${genres}</p>
    </div>
    <div class="modal-content">
      <p><b>Director</b><br/>${m.director}</p>
      <p><b>Cast</b><br/>${cast}</p>
      <div class="modal-description">${m.description || 'No description available.'}</div>
      <div class="modal-rating-badge">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        ${rating} / 10
      </div>
    </div>`;
  $('modalBg').classList.remove('hidden');
}

function closeModal() {
  $('modalBg').classList.add('hidden');
}
