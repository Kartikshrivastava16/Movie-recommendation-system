"""
Movie Recommendation System
============================
Uses collaborative filtering and content-based filtering
to suggest movies based on user preferences and behavior.
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


# ── Load Data ─────────────────────────────────────────────────────────────────

def load_data():
    movies  = pd.read_csv("movies.csv")
    ratings = pd.read_csv("ratings.csv")
    return movies, ratings


# ── Collaborative Filtering ───────────────────────────────────────────────────

def collaborative_filtering(ratings: pd.DataFrame, target_user_id: int, top_n: int = 5):
    """
    User-based collaborative filtering.
    Finds users similar to the target user and recommends movies they liked.
    """
    # Build user-movie matrix
    user_movie_matrix = ratings.pivot_table(
        index="user_id", columns="movie_id", values="rating"
    ).fillna(0)

    if target_user_id not in user_movie_matrix.index:
        print(f"User {target_user_id} not found in ratings data.")
        return []

    # Cosine similarity between users
    similarity_matrix = cosine_similarity(user_movie_matrix)
    similarity_df = pd.DataFrame(
        similarity_matrix,
        index=user_movie_matrix.index,
        columns=user_movie_matrix.index
    )

    # Get similarity scores for the target user (excluding themselves)
    similar_users = (
        similarity_df[target_user_id]
        .drop(target_user_id)
        .sort_values(ascending=False)
    )

    # Movies already rated by the target user
    rated_movies = set(
        ratings[ratings["user_id"] == target_user_id]["movie_id"]
    )

    # Collect weighted scores from similar users
    score_map: dict[int, float] = {}
    for other_user, sim_score in similar_users.items():
        if sim_score <= 0:
            continue
        other_ratings = ratings[ratings["user_id"] == other_user]
        for _, row in other_ratings.iterrows():
            mid = int(row["movie_id"])
            if mid not in rated_movies:
                score_map[mid] = score_map.get(mid, 0) + sim_score * row["rating"]

    # Sort and return top-N movie IDs
    recommended_ids = sorted(score_map, key=score_map.get, reverse=True)[:top_n]
    return recommended_ids


# ── Content-Based Filtering ───────────────────────────────────────────────────

def content_based_filtering(movies: pd.DataFrame, movie_title: str, top_n: int = 5):
    """
    Content-based filtering using TF-IDF on genre tags.
    Recommends movies similar to a given movie title.
    """
    movies = movies.copy()
    movies["genres"] = movies["genres"].str.replace("|", " ", regex=False)

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(movies["genres"])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Find index of the requested movie
    matches = movies[movies["title"].str.lower() == movie_title.lower()]
    if matches.empty:
        print(f"Movie '{movie_title}' not found.")
        return []

    idx = matches.index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Exclude the movie itself
    sim_scores = [s for s in sim_scores if s[0] != idx][:top_n]
    recommended_ids = [movies.iloc[i[0]]["movie_id"] for i in sim_scores]
    return recommended_ids


# ── Display Helpers ───────────────────────────────────────────────────────────

def display_recommendations(movie_ids: list, movies: pd.DataFrame, label: str):
    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}")
    if not movie_ids:
        print("  No recommendations found.")
        return
    for rank, mid in enumerate(movie_ids, start=1):
        row = movies[movies["movie_id"] == mid]
        if not row.empty:
            title  = row.iloc[0]["title"]
            genres = row.iloc[0]["genres"]
            print(f"  {rank}. {title}  [{genres}]")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    movies, ratings = load_data()

    print("\n🎬  MOVIE RECOMMENDATION SYSTEM")
    print("=" * 50)
    print(f"  Loaded {len(movies)} movies and {len(ratings)} ratings\n")

    # ── Collaborative Filtering Demo ──
    target_user = 1
    cf_ids = collaborative_filtering(ratings, target_user_id=target_user, top_n=5)
    display_recommendations(
        cf_ids, movies,
        f"Collaborative Filtering — Top 5 for User {target_user}"
    )

    # ── Content-Based Filtering Demo ──
    seed_movie = "Inception"
    cb_ids = content_based_filtering(movies, movie_title=seed_movie, top_n=5)
    display_recommendations(
        cb_ids, movies,
        f"Content-Based Filtering — Similar to '{seed_movie}'"
    )

    print("\n" + "=" * 50)
    print("  Recommendation complete!")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
