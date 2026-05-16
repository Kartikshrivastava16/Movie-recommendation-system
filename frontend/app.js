/* ═══════════════════════════════════════════
   CINEMATCH — app.js
   ═══════════════════════════════════════════ */

'use strict';

// ── Mock data ─────────────────────────────────────────────────────────────────

const MOVIES = [
  { id:1,   title:"The Shawshank Redemption", genres:["Drama"],                 year:1994, rating:4.8, emoji:"🏛️" },
  { id:2,   title:"The Godfather",             genres:["Crime","Drama"],          year:1972, rating:4.7, emoji:"🌹" },
  { id:3,   title:"The Dark Knight",           genres:["Action","Crime"],         year:2008, rating:4.9, emoji:"🦇" },
  { id:4,   title:"Pulp Fiction",              genres:["Crime","Drama"],          year:1994, rating:4.6, emoji:"💼" },
  { id:5,   title:"Schindler's List",          genres:["Biography","Drama"],      year:1993, rating:4.7, emoji:"📜" },
  { id:6,   title:"Inception",                 genres:["Action","Sci-Fi"],        year:2010, rating:4.8, emoji:"🌀" },
  { id:7,   title:"The Matrix",                genres:["Action","Sci-Fi"],        year:1999, rating:4.7, emoji:"🔴" },
  { id:8,   title:"Interstellar",              genres:["Adventure","Sci-Fi"],     year:2014, rating:4.6, emoji:"🚀" },
  { id:9,   title:"The Lord of the Rings",     genres:["Adventure","Fantasy"],    year:2001, rating:4.8, emoji:"💍" },
  { id:10,  title:"Forrest Gump",              genres:["Drama","Romance"],        year:1994, rating:4.5, emoji:"🍫" },
  { id:11,  title:"Fight Club",                genres:["Drama","Thriller"],       year:1999, rating:4.7, emoji:"🥊" },
  { id:12,  title:"Goodfellas",                genres:["Crime","Drama"],          year:1990, rating:4.6, emoji:"🔫" },
  { id:13,  title:"The Silence of the Lambs",  genres:["Crime","Thriller"],       year:1991, rating:4.5, emoji:"🦋" },
  { id:14,  title:"Avengers: Endgame",         genres:["Action","Adventure"],     year:2019, rating:4.4, emoji:"⚡" },
  { id:15,  title:"Parasite",                  genres:["Drama","Thriller"],       year:2019, rating:4.6, emoji:"🏚️" },
  { id:16,  title:"Whiplash",                  genres:["Drama","Music"],          year:2014, rating:4.5, emoji:"🥁" },
  { id:17,  title:"La La Land",                genres:["Drama","Music","Romance"],year:2016, rating:4.3, emoji:"🎷" },
  { id:18,  title:"Blade Runner 2049",         genres:["Drama","Sci-Fi"],         year:2017, rating:4.4, emoji:"🤖" },
  { id:19,  title:"The Grand Budapest Hotel",  genres:["Comedy","Drama"],         year:2014, rating:4.4, emoji:"🏨" },
  { id:20,  title:"Mad Max: Fury Road",        genres:["Action","Adventure"],     year:2015, rating:4.5, emoji:"🚗" },
  { id:21,  title:"Coco",                      genres:["Animation","Family"],     year:2017, rating:4.5, emoji:"💀" },
  { id:22,  title:"Spirited Away",             genres:["Animation","Fantasy"],    year:2001, rating:4.8, emoji:"🐉" },
  { id:23,  title:"Get Out",                   genres:["Horror","Thriller"],      year:2017, rating:4.3, emoji:"🧠" },
  { id:24,  title:"A Quiet Place",             genres:["Horror","Sci-Fi"],        year:2018, rating:4.2, emoji:"🤫" },
  { id:25,  title:"Everything Everywhere",     genres:["Action","Comedy","Sci-Fi"],year:2022,rating:4.7, emoji:"🥨" },
  { id:26,  title:"Oppenheimer",               genres:["Biography","Drama"],      year:2023, rating:4.6, emoji:"☢️" },
  { id:27,  title:"Barbie",                    genres:["Comedy","Fantasy"],       year:2023, rating:4.1, emoji:"💗" },
  { id:28,  title:"Dune",                      genres:["Adventure","Sci-Fi"],     year:2021, rating:4.5, emoji:"🏜️" },
  { id:29,  title:"No Country for Old Men",    genres:["Crime","Drama"],          year:2007, rating:4.5, emoji:"🪙" },
  { id:30,  title:"Her",                       genres:["Drama","Romance","Sci-Fi"],year:2013,rating:4.4, emoji:"💌" },
];

const ALL_GENRES = [...new Set(MOVIES.flatMap(m => m.genres))].sort();

const ALGO_EXPLAINS = {
  collaborative: "Analyses rating patterns from similar users. If users A and B both love Sci-Fi, movies A rated highly are recommended to B.",
  content:       "Looks at a seed movie's genres and features, then finds other movies with matching attributes using TF-IDF similarity.",
  hybrid:        "Blends collaborative and content-based scores for a balanced recommendation — better coverage and diversity.",
};

const LOADING_MSGS = {
  collaborative: ["Analysing user patterns…", "Computing cosine similarity…", "Ranking top picks…"],
  content:       ["Vectorising movie genres…", "Running TF-IDF similarity…", "Matching closest films…"],
  hybrid:        ["Combining both algorithms…", "Weighing scores…", "Assembling hybrid list…"],
};

// ── State ─────────────────────────────────────────────────────────────────────

let state = {
  algo:     "collaborative",
  userId:   42,
  topN:     8,
  genres:   [],
  seedMovie: null,
  view:     "grid",
  results:  [],
};

// ── DOM refs ──────────────────────────────────────────────────────────────────

const $ = id => document.getElementById(id);
const $$ = sel => document.querySelectorAll(sel);

// ── Init ──────────────────────────────────────────────────────────────────────

function init() {
  buildGenreFilters();
  bindAlgoButtons();
  bindSliders();
  bindSearch();
  bindSeedInput();
  bindRunButton();
  bindViewToggle();
  bindNavLinks();
  drawRadarChart();
}

// ── Genre filter chips ────────────────────────────────────────────────────────

function buildGenreFilters() {
  const container = $('genreFilters');
  ALL_GENRES.forEach(g => {
    const btn = document.createElement('button');
    btn.className = 'genre-tag';
    btn.textContent = g;
    btn.addEventListener('click', () => {
      btn.classList.toggle('active');
      if (state.genres.includes(g)) {
        state.genres = state.genres.filter(x => x !== g);
      } else {
        state.genres.push(g);
      }
    });
    container.appendChild(btn);
  });
}

// ── Algorithm buttons ─────────────────────────────────────────────────────────

function bindAlgoButtons() {
  $$('.algo-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      $$('.algo-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.algo = btn.dataset.algo;
      $('algoExplain').textContent = ALGO_EXPLAINS[state.algo];
      const seedRow = $('seedRow');
      seedRow.style.display = state.algo === 'content' ? 'flex' : 'none';
    });
  });
}

// ── Sliders ───────────────────────────────────────────────────────────────────

function bindSliders() {
  const userSlider = $('userSlider');
  const sliderDisplay = $('sliderDisplay');
  const activeUser = $('activeUser');
  userSlider.addEventListener('input', () => {
    state.userId = +userSlider.value;
    sliderDisplay.textContent = userSlider.value;
    activeUser.textContent = userSlider.value;
  });

  const topNSlider = $('topNSlider');
  const topNDisplay = $('topNDisplay');
  topNSlider.addEventListener('input', () => {
    state.topN = +topNSlider.value;
    topNDisplay.textContent = topNSlider.value;
  });
}

// ── Hero search ───────────────────────────────────────────────────────────────

function bindSearch() {
  const input = $('searchInput');
  const btn   = $('searchBtn');

  function doSearch() {
    const q = input.value.trim().toLowerCase();
    if (!q) return;
    const matches = MOVIES.filter(m =>
      m.title.toLowerCase().includes(q) ||
      m.genres.some(g => g.toLowerCase().includes(q))
    );
    const topN = matches.slice(0, state.topN || 8);
    state.results = topN;
    renderCards(topN, `Search: "${input.value.trim()}"`);
    document.querySelector('.main').scrollIntoView({ behavior: 'smooth' });
  }

  btn.addEventListener('click', doSearch);
  input.addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(); });

  $$('.hint').forEach(h => {
    h.addEventListener('click', () => {
      input.value = h.dataset.q;
      doSearch();
    });
  });
}

// ── Seed movie input (content-based) ─────────────────────────────────────────

function bindSeedInput() {
  const input    = $('seedInput');
  const dropdown = $('seedDropdown');

  input.addEventListener('input', () => {
    const q = input.value.toLowerCase();
    if (!q) { dropdown.classList.remove('open'); return; }
    const matches = MOVIES.filter(m => m.title.toLowerCase().includes(q)).slice(0, 8);
    dropdown.innerHTML = matches.map(m =>
      `<div class="seed-option" data-id="${m.id}">${m.title} <span style="color:var(--muted);font-size:11px;">${m.year}</span></div>`
    ).join('');
    dropdown.classList.toggle('open', matches.length > 0);
  });

  dropdown.addEventListener('click', e => {
    const opt = e.target.closest('.seed-option');
    if (!opt) return;
    const movie = MOVIES.find(m => m.id === +opt.dataset.id);
    if (movie) {
      state.seedMovie = movie;
      input.value = movie.title;
      dropdown.classList.remove('open');
    }
  });

  document.addEventListener('click', e => {
    if (!e.target.closest('.seed-search')) dropdown.classList.remove('open');
  });
}

// ── Run button ────────────────────────────────────────────────────────────────

function bindRunButton() {
  $('runBtn').addEventListener('click', async () => {
    await runRecommendations();
  });
}

async function runRecommendations() {
  const overlay  = $('loadingOverlay');
  const loadText = $('loadingText');
  const msgs     = LOADING_MSGS[state.algo];

  overlay.style.display = 'flex';

  // Cycle loading messages
  let i = 0;
  loadText.textContent = msgs[0];
  const interval = setInterval(() => {
    i = (i + 1) % msgs.length;
    loadText.textContent = msgs[i];
  }, 600);

  await sleep(1800);
  clearInterval(interval);
  overlay.style.display = 'none';

  const results = computeRecommendations();
  state.results = results;
  renderCards(results, buildResultsTitle());
}

function computeRecommendations() {
  let pool = [...MOVIES];

  // Genre filter
  if (state.genres.length > 0) {
    pool = pool.filter(m => m.genres.some(g => state.genres.includes(g)));
  }

  if (state.algo === 'collaborative') {
    // Simulate: random seed from userId, sort by simulated score
    const seed = state.userId * 31337;
    pool = pool.map(m => ({ ...m, _score: pseudoRandom(seed + m.id) * m.rating }));
    pool.sort((a, b) => b._score - a._score);

  } else if (state.algo === 'content') {
    if (state.seedMovie) {
      const seedGenres = state.seedMovie.genres;
      pool = pool.filter(m => m.id !== state.seedMovie.id);
      pool = pool.map(m => {
        const overlap = m.genres.filter(g => seedGenres.includes(g)).length;
        return { ...m, _score: overlap / Math.max(m.genres.length, seedGenres.length) };
      });
      pool.sort((a, b) => b._score - a._score);
    } else {
      pool.sort((a, b) => b.rating - a.rating);
    }

  } else { // hybrid
    const seed = state.userId * 13337;
    pool = pool.map(m => ({
      ...m,
      _score: 0.6 * pseudoRandom(seed + m.id) * m.rating + 0.4 * m.rating / 5,
    }));
    pool.sort((a, b) => b._score - a._score);
  }

  return pool.slice(0, state.topN);
}

function buildResultsTitle() {
  if (state.algo === 'collaborative') return `TOP PICKS — USER ${state.userId}`;
  if (state.algo === 'content' && state.seedMovie) return `SIMILAR TO "${state.seedMovie.title.toUpperCase()}"`;
  if (state.algo === 'hybrid') return `HYBRID PICKS — USER ${state.userId}`;
  return "RECOMMENDED FOR YOU";
}

// ── Render cards ──────────────────────────────────────────────────────────────

function renderCards(movies, title = "RECOMMENDED FOR YOU") {
  const grid = $('cardsGrid');
  $('resultsTitle').textContent = title;
  $('resultsMeta').textContent = `${movies.length} result${movies.length !== 1 ? 's' : ''} · ${algoLabel(state.algo)}`;

  if (movies.length === 0) {
    grid.innerHTML = `<div class="placeholder-state">
      <div class="placeholder-icon">🔍</div>
      <div class="placeholder-text">No movies found</div>
      <div class="placeholder-sub">Try adjusting your filters</div>
    </div>`;
    return;
  }

  grid.innerHTML = movies.map((m, i) => buildCard(m, i)).join('');

  // Stagger animation delays
  grid.querySelectorAll('.movie-card').forEach((card, i) => {
    card.style.animationDelay = `${i * 60}ms`;
  });
}

function buildCard(movie, rank) {
  const stars = starString(movie.rating);
  const genres = movie.genres.map(g => `<span class="genre-pill">${g}</span>`).join('');
  const score  = movie._score ? (movie._score * 20).toFixed(0) + '%' : (movie.rating * 20).toFixed(0) + '%';

  return `<div class="movie-card" style="animation-delay:${rank*60}ms">
    <div class="card-poster">
      <div class="card-poster-bg">${movie.emoji}</div>
      <div class="card-rank">${rank + 1}</div>
      <div class="card-score">${score}</div>
      <div class="card-poster-title">${movie.title}</div>
    </div>
    <div class="card-body">
      <div class="card-genres">${genres}</div>
      <div>
        <span class="card-stars">${stars}</span>
        <span class="card-year">${movie.year}</span>
      </div>
    </div>
  </div>`;
}

function starString(rating) {
  const full  = Math.round(rating);
  const empty = 5 - full;
  return '★'.repeat(full) + '☆'.repeat(empty);
}

// ── View toggle ───────────────────────────────────────────────────────────────

function bindViewToggle() {
  $$('.view-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      $$('.view-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.view = btn.dataset.view;
      const grid = $('cardsGrid');
      grid.classList.toggle('list-view', state.view === 'list');
    });
  });
}

// ── Nav links (scroll) ────────────────────────────────────────────────────────

function bindNavLinks() {
  $$('.nav-link').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      $$('.nav-link').forEach(l => l.classList.remove('active'));
      link.classList.add('active');
      const section = link.dataset.section;
      if (section !== 'discover') {
        // auto-select algo
        const algoBtn = document.querySelector(`.algo-btn[data-algo="${section === 'collaborative' ? 'collaborative' : section === 'content' ? 'content' : 'hybrid'}"]`);
        if (algoBtn) algoBtn.click();
      }
      document.querySelector('.main').scrollIntoView({ behavior: 'smooth' });
    });
  });
}

// ── Radar chart ───────────────────────────────────────────────────────────────

function drawRadarChart() {
  const canvas = $('radarChart');
  const ctx    = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  const cx = W / 2, cy = H / 2;
  const R  = Math.min(W, H) / 2 - 40;

  const labels = ['Precision', 'Recall', 'Coverage', 'Diversity', 'Speed'];
  const datasets = [
    { color: '#e8ff47', values: [0.82, 0.75, 0.60, 0.55, 0.90] },
    { color: '#47c8ff', values: [0.70, 0.80, 0.85, 0.78, 0.95] },
    { color: '#ff6f47', values: [0.88, 0.84, 0.80, 0.75, 0.80] },
  ];

  const n = labels.length;
  const angleStep = (Math.PI * 2) / n;
  const angles = labels.map((_, i) => -Math.PI / 2 + i * angleStep);

  function toXY(angle, r) {
    return [cx + r * Math.cos(angle), cy + r * Math.sin(angle)];
  }

  // Clear
  ctx.clearRect(0, 0, W, H);

  // Grid rings
  [0.25, 0.5, 0.75, 1].forEach(frac => {
    ctx.beginPath();
    angles.forEach((a, i) => {
      const [x, y] = toXY(a, R * frac);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineWidth = 1;
    ctx.stroke();
  });

  // Spokes
  angles.forEach(a => {
    const [x, y] = toXY(a, R);
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(x, y);
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineWidth = 1;
    ctx.stroke();
  });

  // Labels
  ctx.font = '500 11px "DM Mono", monospace';
  ctx.fillStyle = 'rgba(255,255,255,0.4)';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  angles.forEach((a, i) => {
    const [x, y] = toXY(a, R + 22);
    ctx.fillText(labels[i], x, y);
  });

  // Datasets
  datasets.forEach(ds => {
    ctx.beginPath();
    angles.forEach((a, i) => {
      const [x, y] = toXY(a, R * ds.values[i]);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.strokeStyle = ds.color;
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.fillStyle = ds.color + '22';
    ctx.fill();

    // Dots
    angles.forEach((a, i) => {
      const [x, y] = toXY(a, R * ds.values[i]);
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fillStyle = ds.color;
      ctx.fill();
    });
  });
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function pseudoRandom(seed) {
  let x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
}

function algoLabel(algo) {
  return { collaborative: 'Collaborative Filtering', content: 'Content-Based Filtering', hybrid: 'Hybrid Model' }[algo];
}

// ── Run ───────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', init);
