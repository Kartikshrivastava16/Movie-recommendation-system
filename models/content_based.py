"""
content_based.py
=================
Content-Based Filtering model using TF-IDF on movie metadata.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedFilter:
    """
    Content-Based Filtering using TF-IDF vectorization on genres,
    director, and cast metadata.
    """

    def __init__(self):
        self.tfidf = TfidfVectorizer(stop_words="english")
        self.cosine_sim = None
        self.movies = None
        self.indices = None

    def _build_soup(self, row: pd.Series) -> str:
        """Combine metadata fields into a single text string."""
        genres = row["genres"].replace("|", " ") if pd.notna(row.get("genres")) else ""
        director = row.get("director", "")
        cast = row.get("cast", "").replace("|", " ") if pd.notna(row.get("cast")) else ""
        description = row.get("description", "") if pd.notna(row.get("description")) else ""
        return f"{genres} {director} {cast} {description}"

    def fit(self, movies: pd.DataFrame):
        """Build TF-IDF matrix and cosine similarity."""
        self.movies = movies.reset_index(drop=True).copy()
        self.movies["soup"] = self.movies.apply(self._build_soup, axis=1)
        self.indices = pd.Series(self.movies.index, index=self.movies["title"].str.lower())

        tfidf_matrix = self.tfidf.fit_transform(self.movies["soup"])
        self.cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        print("[ContentBasedFilter] Model fitted successfully.")

    def recommend_by_title(self, title: str, top_n: int = 5) -> list:
        """Recommend movies similar to a given title."""
        key = title.lower()
        if key not in self.indices:
            print(f"[ContentBasedFilter] '{title}' not found in dataset.")
            return []

        idx = self.indices[key]
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = [s for s in sim_scores if s[0] != idx][:top_n]

        movie_indices = [i[0] for i in sim_scores]
        return list(self.movies.iloc[movie_indices]["movie_id"])

    def recommend_by_genres(self, genres: list, top_n: int = 5) -> list:
        """Recommend movies matching a list of genre preferences."""
        query = " ".join(genres)
        query_vec = self.tfidf.transform([query])
        sim_scores = cosine_similarity(query_vec, self.tfidf.transform(self.movies["soup"]))
        top_indices = sim_scores[0].argsort()[::-1][:top_n]
        return list(self.movies.iloc[top_indices]["movie_id"])
