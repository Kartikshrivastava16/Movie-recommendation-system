"""
hybrid.py — uses absolute imports so it works both standalone and inside Django
"""

import pandas as pd
from models.collaborative_filtering import UserBasedCF
from models.content_based import ContentBasedFilter


class HybridRecommender:
    def __init__(self, cf_weight: float = 0.6, cb_weight: float = 0.4):
        assert abs(cf_weight + cb_weight - 1.0) < 1e-6, "Weights must sum to 1."
        self.cf_weight = cf_weight
        self.cb_weight = cb_weight
        self.cf_model = UserBasedCF()
        self.cb_model = ContentBasedFilter()
        self.movies = None
        self.ratings = None

    def fit(self, movies: pd.DataFrame, ratings: pd.DataFrame):
        self.movies = movies
        self.ratings = ratings
        self.cf_model.fit(ratings)
        self.cb_model.fit(movies)
        print("[HybridRecommender] Both models fitted.")

    def recommend(self, user_id: int, top_n: int = 5) -> list:
        cf_recs = self.cf_model.recommend(user_id, top_n=top_n * 2)

        user_ratings = self.ratings[self.ratings["user_id"] == user_id]
        cb_recs = []
        if not user_ratings.empty:
            top_movie_id = user_ratings.loc[user_ratings["rating"].idxmax(), "movie_id"]
            top_movie_row = self.movies[self.movies["movie_id"] == top_movie_id]
            if not top_movie_row.empty:
                seed_title = top_movie_row.iloc[0]["title"]
                cb_recs = self.cb_model.recommend_by_title(seed_title, top_n=top_n * 2)

        score_map: dict = {}
        for rank, movie_id in enumerate(cf_recs):
            score_map[movie_id] = score_map.get(movie_id, 0) + self.cf_weight * (1 / (rank + 1))
        for rank, movie_id in enumerate(cb_recs):
            score_map[movie_id] = score_map.get(movie_id, 0) + self.cb_weight * (1 / (rank + 1))

        return sorted(score_map, key=score_map.get, reverse=True)[:top_n]
