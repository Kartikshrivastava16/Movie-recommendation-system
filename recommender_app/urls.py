from django.urls import path
from recommender_app import views

urlpatterns = [
    # ── Page ──────────────────────────────────────────────────────
    path('', views.index, name='index'),

    # ── Data API ──────────────────────────────────────────────────
    path('api/data/stats',   views.api_stats,        name='api_stats'),
    path('api/data/movies',  views.api_movies,       name='api_movies'),
    path('api/data/users',   views.api_users,        name='api_users'),
    path('api/data/genres',  views.api_genres,       name='api_genres'),
    path('api/search',       views.api_search,       name='api_search'),
    path('api/movie/<int:movie_id>/', views.api_movie_detail, name='api_movie_detail'),

    # ── Recommend API ─────────────────────────────────────────────
    path('api/recommend/collaborative/', views.api_recommend_collaborative, name='api_collab'),
    path('api/recommend/item-based/',    views.api_recommend_item_based,    name='api_item'),
    path('api/recommend/content-based/', views.api_recommend_content,       name='api_content'),
    path('api/recommend/hybrid/',        views.api_recommend_hybrid,        name='api_hybrid'),
]
