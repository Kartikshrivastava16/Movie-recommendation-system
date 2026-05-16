"""
metrics.py
===========
Evaluation metrics: RMSE, MAE, Precision@K, Recall@K, NDCG@K.
"""

import numpy as np
import pandas as pd


def rmse(actual: list, predicted: list) -> float:
    """Root Mean Squared Error."""
    a, p = np.array(actual), np.array(predicted)
    return float(np.sqrt(np.mean((a - p) ** 2)))


def mae(actual: list, predicted: list) -> float:
    """Mean Absolute Error."""
    a, p = np.array(actual), np.array(predicted)
    return float(np.mean(np.abs(a - p)))


def precision_at_k(recommended: list, relevant: set, k: int = 5) -> float:
    """Fraction of recommended items in top-K that are relevant."""
    top_k = recommended[:k]
    hits = len([m for m in top_k if m in relevant])
    return hits / k if k > 0 else 0.0


def recall_at_k(recommended: list, relevant: set, k: int = 5) -> float:
    """Fraction of relevant items that appear in top-K recommendations."""
    if not relevant:
        return 0.0
    top_k = recommended[:k]
    hits = len([m for m in top_k if m in relevant])
    return hits / len(relevant)


def ndcg_at_k(recommended: list, relevant: set, k: int = 5) -> float:
    """Normalized Discounted Cumulative Gain at K."""
    top_k = recommended[:k]
    dcg = sum(
        1 / np.log2(i + 2)
        for i, movie in enumerate(top_k)
        if movie in relevant
    )
    ideal_hits = min(len(relevant), k)
    idcg = sum(1 / np.log2(i + 2) for i in range(ideal_hits))
    return dcg / idcg if idcg > 0 else 0.0


def evaluate_model(model, test_ratings: pd.DataFrame, movies: pd.DataFrame, k: int = 5) -> dict:
    """
    Evaluate a recommendation model on test data.
    Returns average Precision@K, Recall@K, and NDCG@K across all users.
    """
    precisions, recalls, ndcgs = [], [], []

    for user_id in test_ratings["user_id"].unique():
        relevant = set(test_ratings[test_ratings["user_id"] == user_id]["movie_id"])
        recommended = model.recommend(user_id, top_n=k)

        precisions.append(precision_at_k(recommended, relevant, k))
        recalls.append(recall_at_k(recommended, relevant, k))
        ndcgs.append(ndcg_at_k(recommended, relevant, k))

    results = {
        f"Precision@{k}": round(np.mean(precisions), 4),
        f"Recall@{k}":    round(np.mean(recalls),    4),
        f"NDCG@{k}":      round(np.mean(ndcgs),      4),
    }
    return results
