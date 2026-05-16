"""
main.py
========
Entry point — runs a full demo of all recommendation modes.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils import load_all, clean_ratings, filter_active_users
from models import UserBasedCF, ItemBasedCF, HybridRecommender
from models.content_based import ContentBasedFilter
from utils.display import print_recommendations, print_movie_details, print_similar_users


def main():
    print("\n🎬  MOVIE RECOMMENDATION SYSTEM — FULL DEMO")
    print("=" * 60)

    # ── Load & preprocess ──────────────────────────────────────────
    movies, ratings, users = load_all()
    ratings = clean_ratings(ratings)
    ratings = filter_active_users(ratings, min_ratings=3)

    # ── Fit models ─────────────────────────────────────────────────
    ub_model     = UserBasedCF(n_similar_users=5);   ub_model.fit(ratings)
    ib_model     = ItemBasedCF();                     ib_model.fit(ratings)
    cb_model     = ContentBasedFilter();              cb_model.fit(movies)
    hybrid_model = HybridRecommender(cf_weight=0.6, cb_weight=0.4)
    hybrid_model.fit(movies, ratings)

    # ── Demo: User-Based CF ────────────────────────────────────────
    for uid in [1, 3, 5]:
        recs = ub_model.recommend(uid, top_n=5)
        print_recommendations(recs, movies, f"User-Based CF — Top 5 for User {uid}")

    # ── Demo: Item-Based CF ────────────────────────────────────────
    for uid in [2, 4]:
        recs = ib_model.recommend(uid, top_n=5)
        print_recommendations(recs, movies, f"Item-Based CF — Top 5 for User {uid}")

    # ── Demo: Content-Based ────────────────────────────────────────
    for title in ["Inception", "The Godfather", "Spirited Away"]:
        recs = cb_model.recommend_by_title(title, top_n=5)
        print_recommendations(recs, movies, f"Content-Based — Similar to '{title}'")

    # ── Demo: Genre-Based ─────────────────────────────────────────
    recs = cb_model.recommend_by_genres(["Action", "Sci-Fi"], top_n=5)
    print_recommendations(recs, movies, "Genre-Based — Action & Sci-Fi")

    # ── Demo: Hybrid ──────────────────────────────────────────────
    for uid in [1, 6]:
        recs = hybrid_model.recommend(uid, top_n=5)
        print_recommendations(recs, movies, f"Hybrid — Top 5 for User {uid}")

    # ── Demo: Movie Details ───────────────────────────────────────
    print_movie_details(2, movies)   # Inception
    print_movie_details(7, movies)   # Shawshank

    # ── Demo: Similar Users ───────────────────────────────────────
    similar = ub_model.get_similar_users(1, top_n=3)
    print_similar_users(similar, users)

    print("\n✅  Demo complete!\n")


if __name__ == "__main__":
    main()
