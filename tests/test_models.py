"""
test_models.py
===============
Unit tests for all recommendation models.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
import pandas as pd
from models.collaborative_filtering import UserBasedCF, ItemBasedCF
from models.content_based import ContentBasedFilter
from models.hybrid import HybridRecommender


# ── Minimal fixture data ───────────────────────────────────────────────────────

MOVIES = pd.DataFrame({
    "movie_id": [1, 2, 3, 4, 5],
    "title":    ["Movie A", "Movie B", "Movie C", "Movie D", "Movie E"],
    "genres":   ["Action|Sci-Fi", "Drama|Romance", "Action|Adventure", "Drama|Crime", "Sci-Fi|Adventure"],
    "director": ["Dir1", "Dir2", "Dir1", "Dir3", "Dir2"],
    "cast":     ["Actor1|Actor2", "Actor3", "Actor1", "Actor2|Actor3", "Actor1|Actor3"],
    "description": [
        "An action packed sci-fi movie",
        "A heartfelt drama romance",
        "Action and adventure await",
        "A gripping crime drama",
        "Sci-fi adventure in space"
    ],
    "year": [2010, 2015, 2018, 2020, 2022],
    "rating_avg": [8.0, 7.5, 8.2, 7.8, 8.5],
})

RATINGS = pd.DataFrame({
    "user_id":  [1, 1, 1, 2, 2, 2, 3, 3, 3],
    "movie_id": [1, 2, 3, 1, 3, 4, 2, 4, 5],
    "rating":   [5.0, 3.0, 4.0, 4.0, 5.0, 3.5, 4.5, 5.0, 4.0],
})


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestUserBasedCF(unittest.TestCase):

    def setUp(self):
        self.model = UserBasedCF(n_similar_users=2)
        self.model.fit(RATINGS)

    def test_fit_creates_similarity(self):
        self.assertIsNotNone(self.model.similarity_df)

    def test_recommend_returns_list(self):
        recs = self.model.recommend(1, top_n=3)
        self.assertIsInstance(recs, list)

    def test_recommend_excludes_rated(self):
        rated = set(RATINGS[RATINGS["user_id"] == 1]["movie_id"])
        recs = self.model.recommend(1, top_n=5)
        for mid in recs:
            self.assertNotIn(mid, rated)

    def test_recommend_unknown_user(self):
        recs = self.model.recommend(999, top_n=3)
        self.assertEqual(recs, [])


class TestItemBasedCF(unittest.TestCase):

    def setUp(self):
        self.model = ItemBasedCF()
        self.model.fit(RATINGS)

    def test_fit_creates_similarity(self):
        self.assertIsNotNone(self.model.item_similarity_df)

    def test_recommend_returns_list(self):
        recs = self.model.recommend(1, top_n=3)
        self.assertIsInstance(recs, list)


class TestContentBasedFilter(unittest.TestCase):

    def setUp(self):
        self.model = ContentBasedFilter()
        self.model.fit(MOVIES)

    def test_recommend_by_title_returns_list(self):
        recs = self.model.recommend_by_title("Movie A", top_n=3)
        self.assertIsInstance(recs, list)

    def test_recommend_excludes_self(self):
        recs = self.model.recommend_by_title("Movie A", top_n=5)
        movie_a_id = MOVIES[MOVIES["title"] == "Movie A"].iloc[0]["movie_id"]
        self.assertNotIn(movie_a_id, recs)

    def test_recommend_unknown_title(self):
        recs = self.model.recommend_by_title("Unknown Movie XYZ", top_n=3)
        self.assertEqual(recs, [])


class TestHybridRecommender(unittest.TestCase):

    def setUp(self):
        self.model = HybridRecommender(cf_weight=0.6, cb_weight=0.4)
        self.model.fit(MOVIES, RATINGS)

    def test_recommend_returns_list(self):
        recs = self.model.recommend(1, top_n=3)
        self.assertIsInstance(recs, list)

    def test_invalid_weights(self):
        with self.assertRaises(AssertionError):
            HybridRecommender(cf_weight=0.8, cb_weight=0.8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
