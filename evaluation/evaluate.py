"""
evaluate.py
============
Run full evaluation pipeline comparing all three models.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils import load_all, clean_ratings, filter_active_users, train_test_split_ratings
from models import UserBasedCF, ItemBasedCF, HybridRecommender
from models.content_based import ContentBasedFilter
from evaluation.metrics import evaluate_model


def run_evaluation():
    print("\n🧪  MODEL EVALUATION PIPELINE")
    print("=" * 50)

    movies, ratings, users = load_all()
    ratings = clean_ratings(ratings)
    ratings = filter_active_users(ratings, min_ratings=3)
    train_ratings, test_ratings = train_test_split_ratings(ratings, test_size=0.2)

    results = {}

    # ── User-Based CF ──
    print("\n[1/3] Evaluating User-Based CF...")
    ub_model = UserBasedCF(n_similar_users=5)
    ub_model.fit(train_ratings)
    results["UserBasedCF"] = evaluate_model(ub_model, test_ratings, movies, k=5)

    # ── Item-Based CF ──
    print("\n[2/3] Evaluating Item-Based CF...")
    ib_model = ItemBasedCF()
    ib_model.fit(train_ratings)
    results["ItemBasedCF"] = evaluate_model(ib_model, test_ratings, movies, k=5)

    # ── Hybrid ──
    print("\n[3/3] Evaluating Hybrid Recommender...")
    hybrid_model = HybridRecommender(cf_weight=0.6, cb_weight=0.4)
    hybrid_model.fit(movies, train_ratings)
    results["Hybrid"] = evaluate_model(hybrid_model, test_ratings, movies, k=5)

    # ── Print Summary ──
    print(f"\n{'='*50}")
    print("  EVALUATION RESULTS (K=5)")
    print(f"{'='*50}")
    header = f"  {'Model':<20} {'Precision@5':>12} {'Recall@5':>10} {'NDCG@5':>10}"
    print(header)
    print(f"  {'-'*52}")
    for model_name, scores in results.items():
        row = (
            f"  {model_name:<20}"
            f" {scores['Precision@5']:>12.4f}"
            f" {scores['Recall@5']:>10.4f}"
            f" {scores['NDCG@5']:>10.4f}"
        )
        print(row)
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run_evaluation()
