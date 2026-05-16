"""
ml_engine.py — Singleton: loads data + fits all ML models once at startup.
Views call functions here. No model state in views.
"""

import os
import sys
import pandas as pd

_MODELS = {}
_DATA   = {}
_ready  = False


def initialize():
    global _MODELS, _DATA, _ready
    if _ready:
        return

    from django.conf import settings

    # Ensure project root is on path so 'models' package is importable
    base_dir = str(settings.BASE_DIR)
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    data_dir = str(settings.DATA_DIR)

    # Load CSVs
    movies  = pd.read_csv(os.path.join(data_dir, 'movies.csv'))
    ratings = pd.read_csv(os.path.join(data_dir, 'ratings.csv'))
    users   = pd.read_csv(os.path.join(data_dir, 'users.csv'))
    print(f"[ML] Loaded {len(movies)} movies, {len(ratings)} ratings, {len(users)} users")

    # Clean ratings
    ratings = ratings.drop_duplicates(subset=['user_id', 'movie_id'])
    ratings = ratings.dropna(subset=['rating'])
    ratings['rating'] = ratings['rating'].clip(0.5, 5.0)
    counts  = ratings.groupby('user_id')['movie_id'].count()
    active  = counts[counts >= 3].index
    ratings = ratings[ratings['user_id'].isin(active)].reset_index(drop=True)

    # Import ML models (project root already on sys.path)
    from models.collaborative_filtering import UserBasedCF, ItemBasedCF
    from models.content_based import ContentBasedFilter
    from models.hybrid import HybridRecommender

    ub  = UserBasedCF(n_similar_users=5)
    ub.fit(ratings)

    ib  = ItemBasedCF()
    ib.fit(ratings)

    cb  = ContentBasedFilter()
    cb.fit(movies)

    hyb = HybridRecommender(cf_weight=0.6, cb_weight=0.4)
    hyb.fit(movies, ratings)

    _MODELS = {'collaborative': ub, 'item_based': ib, 'content': cb, 'hybrid': hyb}
    _DATA   = {'movies': movies, 'ratings': ratings, 'users': users}
    _ready  = True
    print("✅  CineMatch — all ML models ready!")


# ── Public API ─────────────────────────────────────────────────────────────────

def get_stats():
    return {
        'movies_count':  int(len(_DATA['movies'])),
        'users_count':   int(len(_DATA['users'])),
        'ratings_count': int(len(_DATA['ratings'])),
    }


def get_all_movies():
    rows = []
    for _, r in _DATA['movies'].iterrows():
        rows.append({
            'movie_id':   int(r['movie_id']),
            'title':      str(r['title']),
            'genres':     str(r['genres']) if pd.notna(r['genres']) else '',
            'year':       int(r['year']) if pd.notna(r['year']) else None,
            'director':   str(r['director']) if pd.notna(r['director']) else '',
            'cast':       str(r['cast']) if pd.notna(r['cast']) else '',
            'description':str(r['description']) if pd.notna(r['description']) else '',
            'rating_avg': float(r['rating_avg']) if pd.notna(r['rating_avg']) else None,
        })
    return rows


def get_all_users():
    rows = []
    for _, r in _DATA['users'].iterrows():
        rows.append({
            'user_id':         int(r['user_id']),
            'name':            str(r['name']),
            'age':             int(r['age']) if pd.notna(r['age']) else None,
            'gender':          str(r['gender']),
            'favorite_genres': str(r['favorite_genres']) if pd.notna(r['favorite_genres']) else '',
        })
    return rows


def get_genres():
    genres = set()
    for g in _DATA['movies']['genres']:
        if pd.notna(g):
            genres.update(str(g).split('|'))
    return sorted(genres)


def recommend_collaborative(user_id, top_n=8, genre_filter=None):
    ids = _MODELS['collaborative'].recommend(user_id, top_n=top_n * 2)
    return _build_recs(ids, genre_filter or [], top_n)


def recommend_item_based(user_id, top_n=8, genre_filter=None):
    ids = _MODELS['item_based'].recommend(user_id, top_n=top_n * 2)
    return _build_recs(ids, genre_filter or [], top_n)


def recommend_content(seed_movie=None, genres=None, top_n=8, genre_filter=None):
    model = _MODELS['content']
    if seed_movie:
        ids = model.recommend_by_title(seed_movie, top_n=top_n * 2)
    else:
        ids = model.recommend_by_genres(genres or [], top_n=top_n * 2)
    return _build_recs(ids, genre_filter or [], top_n)


def recommend_hybrid(user_id, top_n=8, genre_filter=None):
    ids = _MODELS['hybrid'].recommend(user_id, top_n=top_n * 2)
    return _build_recs(ids, genre_filter or [], top_n)


def search_movies(query, top_n=10):
    movies = _DATA['movies']
    q = query.lower()
    mask = (
        movies['title'].str.lower().str.contains(q, na=False) |
        movies['director'].str.lower().str.contains(q, na=False) |
        movies['genres'].str.lower().str.contains(q, na=False)
    )
    return _rows_to_list(movies[mask].head(top_n))


def get_movie_by_id(movie_id):
    movies = _DATA['movies']
    row = movies[movies['movie_id'] == movie_id]
    if row.empty:
        return None
    r = row.iloc[0]
    return {
        'movie_id':    int(r['movie_id']),
        'title':       str(r['title']),
        'genres':      str(r['genres']) if pd.notna(r['genres']) else '',
        'year':        int(r['year']) if pd.notna(r['year']) else None,
        'director':    str(r['director']) if pd.notna(r['director']) else '',
        'cast':        str(r['cast']) if pd.notna(r['cast']) else '',
        'description': str(r['description']) if pd.notna(r['description']) else '',
        'rating_avg':  float(r['rating_avg']) if pd.notna(r['rating_avg']) else None,
    }


# ── Helpers ────────────────────────────────────────────────────────────────────

def _build_recs(movie_ids, genre_filter, top_n):
    movies = _DATA['movies']
    recs   = []
    for mid in movie_ids:
        row = movies[movies['movie_id'] == mid]
        if row.empty:
            continue
        r = row.iloc[0]
        genres_list = str(r['genres']).split('|') if pd.notna(r['genres']) else []
        if genre_filter and not any(g in genre_filter for g in genres_list):
            continue
        recs.append({
            'movie_id':    int(mid),
            'title':       str(r['title']),
            'genres':      genres_list,
            'year':        int(r['year']) if pd.notna(r['year']) else None,
            'director':    str(r['director']) if pd.notna(r['director']) else '',
            'cast':        str(r['cast']).split('|') if pd.notna(r['cast']) else [],
            'description': str(r['description']) if pd.notna(r['description']) else '',
            'rating_avg':  float(r['rating_avg']) if pd.notna(r['rating_avg']) else None,
        })
        if len(recs) >= top_n:
            break
    return recs


def _rows_to_list(df):
    out = []
    for _, r in df.iterrows():
        out.append({
            'movie_id':    int(r['movie_id']),
            'title':       str(r['title']),
            'genres':      str(r['genres']).split('|') if pd.notna(r['genres']) else [],
            'year':        int(r['year']) if pd.notna(r['year']) else None,
            'director':    str(r['director']) if pd.notna(r['director']) else '',
            'cast':        str(r['cast']).split('|') if pd.notna(r['cast']) else [],
            'description': str(r['description']) if pd.notna(r['description']) else '',
            'rating_avg':  float(r['rating_avg']) if pd.notna(r['rating_avg']) else None,
        })
    return out
