"""
collaborative_filtering.py
===========================
User-based and Item-based Collaborative Filtering models.
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class UserBasedCF:
    """
    User-Based Collaborative Filtering.
    Recommends movies by finding users with similar rating patterns.
    """

    def __init__(self, n_similar_users: int = 5):
        self.n_similar_users = n_similar_users
        self.user_movie_matrix = None
        self.similarity_df = None

    def fit(self, ratings: pd.DataFrame):
        """Build the user-movie matrix and compute user similarities."""
        self.user_movie_matrix = ratings.pivot_table(
            index="user_id", columns="movie_id", values="rating"
        ).fillna(0)

        sim_matrix = cosine_similarity(self.user_movie_matrix)
        self.similarity_df = pd.DataFrame(
            sim_matrix,
            index=self.user_movie_matrix.index,
            columns=self.user_movie_matrix.index,
        )
        print("[UserBasedCF] Model fitted successfully.")

    def recommend(self, user_id: int, top_n: int = 5) -> list:
        """Return top-N recommended movie IDs for a given user."""
        if user_id not in self.similarity_df.index:
            print(f"[UserBasedCF] User {user_id} not found.")
            return []

        similar_users = (
            self.similarity_df[user_id]
            .drop(user_id)
            .nlargest(self.n_similar_users)
        )

        rated_movies = set(
            self.user_movie_matrix.loc[user_id][
                self.user_movie_matrix.loc[user_id] > 0
            ].index
        )

        score_map: dict = {}
        for other_user, sim_score in similar_users.items():
            if sim_score <= 0:
                continue
            other_row = self.user_movie_matrix.loc[other_user]
            for movie_id, rating in other_row.items():
                if rating > 0 and movie_id not in rated_movies:
                    score_map[movie_id] = score_map.get(movie_id, 0) + sim_score * rating

        return sorted(score_map, key=score_map.get, reverse=True)[:top_n]

    def get_similar_users(self, user_id: int, top_n: int = 5) -> pd.Series:
        """Return top-N most similar users."""
        if user_id not in self.similarity_df.index:
            return pd.Series()
        return self.similarity_df[user_id].drop(user_id).nlargest(top_n)


class ItemBasedCF:
    """
    Item-Based Collaborative Filtering.
    Recommends movies similar to what the user has already rated highly.
    """

    def __init__(self):
        self.item_similarity_df = None
        self.user_movie_matrix = None

    def fit(self, ratings: pd.DataFrame):
        """Compute item-item similarity matrix."""
        self.user_movie_matrix = ratings.pivot_table(
            index="user_id", columns="movie_id", values="rating"
        ).fillna(0)

        item_sim = cosine_similarity(self.user_movie_matrix.T)
        self.item_similarity_df = pd.DataFrame(
            item_sim,
            index=self.user_movie_matrix.columns,
            columns=self.user_movie_matrix.columns,
        )
        print("[ItemBasedCF] Model fitted successfully.")

    def recommend(self, user_id: int, top_n: int = 5) -> list:
        """Return top-N recommended movie IDs based on item similarity."""
        if user_id not in self.user_movie_matrix.index:
            print(f"[ItemBasedCF] User {user_id} not found.")
            return []

        user_ratings = self.user_movie_matrix.loc[user_id]
        rated = user_ratings[user_ratings > 0]
        unrated = user_ratings[user_ratings == 0].index

        scores: dict = {}
        for movie_id in unrated:
            if movie_id not in self.item_similarity_df.columns:
                continue
            sim_scores = self.item_similarity_df[movie_id][rated.index]
            scores[movie_id] = float(np.dot(sim_scores, rated.values))

        return sorted(scores, key=scores.get, reverse=True)[:top_n]

    def get_similar_movies(self, movie_id: int, top_n: int = 5) -> pd.Series:
        """Return top-N movies most similar to a given movie."""
        if movie_id not in self.item_similarity_df.index:
            return pd.Series()
        return self.item_similarity_df[movie_id].drop(movie_id).nlargest(top_n)
