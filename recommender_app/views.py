"""
views.py — Django views + JSON API endpoints
"""

import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from recommender_app import ml_engine


def _ensure_ready():
    """Lazy-initialize if not already done (safety net)."""
    if not ml_engine._ready:
        ml_engine.initialize()


# ── Page ───────────────────────────────────────────────────────────────────────

def index(request):
    return render(request, 'recommender_app/index.html')


# ── Data API ───────────────────────────────────────────────────────────────────

def api_stats(request):
    _ensure_ready()
    return JsonResponse(ml_engine.get_stats())


def api_movies(request):
    _ensure_ready()
    return JsonResponse(ml_engine.get_all_movies(), safe=False)


def api_users(request):
    _ensure_ready()
    return JsonResponse(ml_engine.get_all_users(), safe=False)


def api_genres(request):
    _ensure_ready()
    return JsonResponse(ml_engine.get_genres(), safe=False)


def api_search(request):
    _ensure_ready()
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse([], safe=False)
    return JsonResponse(ml_engine.search_movies(q), safe=False)


def api_movie_detail(request, movie_id):
    _ensure_ready()
    movie = ml_engine.get_movie_by_id(movie_id)
    if movie is None:
        return JsonResponse({'error': 'Movie not found'}, status=404)
    return JsonResponse(movie)


# ── Recommend API ──────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(['POST'])
def api_recommend_collaborative(request):
    _ensure_ready()
    try:
        data         = json.loads(request.body)
        user_id      = int(data['user_id'])
        top_n        = int(data.get('top_n', 8))
        genre_filter = data.get('genres', [])
        recs = ml_engine.recommend_collaborative(user_id, top_n, genre_filter)
        return JsonResponse({
            'algorithm': 'Collaborative Filtering',
            'user_id': user_id,
            'recommendations': recs,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(['POST'])
def api_recommend_item_based(request):
    _ensure_ready()
    try:
        data         = json.loads(request.body)
        user_id      = int(data['user_id'])
        top_n        = int(data.get('top_n', 8))
        genre_filter = data.get('genres', [])
        recs = ml_engine.recommend_item_based(user_id, top_n, genre_filter)
        return JsonResponse({
            'algorithm': 'Item-Based Collaborative Filtering',
            'user_id': user_id,
            'recommendations': recs,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(['POST'])
def api_recommend_content(request):
    _ensure_ready()
    try:
        data         = json.loads(request.body)
        seed_movie   = data.get('seed_movie')
        genres       = data.get('genres', [])
        top_n        = int(data.get('top_n', 8))
        genre_filter = data.get('genre_filter', [])

        if not seed_movie and not genres:
            return JsonResponse({'error': 'seed_movie or genres required'}, status=400)

        recs = ml_engine.recommend_content(seed_movie, genres, top_n, genre_filter)
        return JsonResponse({
            'algorithm': 'Content-Based Filtering',
            'seed': seed_movie or f"Genres: {', '.join(genres)}",
            'recommendations': recs,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(['POST'])
def api_recommend_hybrid(request):
    _ensure_ready()
    try:
        data         = json.loads(request.body)
        user_id      = int(data['user_id'])
        top_n        = int(data.get('top_n', 8))
        genre_filter = data.get('genres', [])
        recs = ml_engine.recommend_hybrid(user_id, top_n, genre_filter)
        return JsonResponse({
            'algorithm': 'Hybrid (CF + Content-Based)',
            'user_id': user_id,
            'recommendations': recs,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
