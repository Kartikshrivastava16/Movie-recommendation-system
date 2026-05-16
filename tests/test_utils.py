"""
test_utils.py
==============
Unit tests for utility functions.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
import pandas as pd
from utils.preprocessor import (
    clean_ratings, normalize_ratings,
    filter_active_users, filter_popular_movies,
    train_test_split_ratings,
)
from evaluation.metrics import precision_at_k, recall_at_k, ndcg_at_k


RATINGS = pd.DataFrame({
    "user_id":  [1, 1, 1, 1, 2, 2, 2, 3, 3],
    "movie_id": [1, 2, 3, 3, 1, 4, 5, 2, 3],
    "rating":   [5.0, 3.0, 4.0, 4.0, 4.0, None, 3.5, 4.5, 5.0],
})


class TestPreprocessor(unittest.TestCase):

    def test_clean_removes_duplicates(self):
        cleaned = clean_ratings(RATINGS)
        self.assertEqual(len(cleaned), len(RATINGS.drop_duplicates(subset=["user_id", "movie_id"]).dropna(subset=["rating"])))

    def test_clean_removes_nulls(self):
        cleaned = clean_ratings(RATINGS)
        self.assertEqual(cleaned["rating"].isnull().sum(), 0)

    def test_normalize_creates_column(self):
        cleaned = clean_ratings(RATINGS)
        normed  = normalize_ratings(cleaned)
        self.assertIn("rating_normalized", normed.columns)

    def test_filter_active_users(self):
        cleaned  = clean_ratings(RATINGS)
        filtered = filter_active_users(cleaned, min_ratings=3)
        for uid, grp in filtered.groupby("user_id"):
            self.assertGreaterEqual(len(grp), 3)

    def test_train_test_split_no_overlap(self):
        cleaned = clean_ratings(RATINGS)
        train, test = train_test_split_ratings(cleaned, test_size=0.3)
        overlap = set(train.index) & set(test.index)
        self.assertEqual(len(overlap), 0)


class TestMetrics(unittest.TestCase):

    def test_precision_perfect(self):
        self.assertEqual(precision_at_k([1, 2, 3], {1, 2, 3}, k=3), 1.0)

    def test_precision_none(self):
        self.assertEqual(precision_at_k([4, 5, 6], {1, 2, 3}, k=3), 0.0)

    def test_recall_perfect(self):
        self.assertEqual(recall_at_k([1, 2, 3], {1, 2, 3}, k=3), 1.0)

    def test_recall_partial(self):
        self.assertAlmostEqual(recall_at_k([1, 4, 5], {1, 2, 3}, k=3), 1/3, places=5)

    def test_ndcg_perfect(self):
        self.assertAlmostEqual(ndcg_at_k([1, 2, 3], {1, 2, 3}, k=3), 1.0, places=5)

    def test_ndcg_empty_relevant(self):
        self.assertEqual(ndcg_at_k([1, 2, 3], set(), k=3), 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
