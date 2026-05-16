"""
preprocessor.py
================
Data cleaning and preprocessing utilities.
"""

import pandas as pd
import numpy as np


def clean_ratings(ratings: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates, drop nulls, and clip ratings to [0.5, 5.0]."""
    df = ratings.drop_duplicates(subset=["user_id", "movie_id"])
    df = df.dropna(subset=["rating"])
    df["rating"] = df["rating"].clip(0.5, 5.0)
    print(f"[Preprocessor] Clean ratings: {len(df)} rows.")
    return df.reset_index(drop=True)


def normalize_ratings(ratings: pd.DataFrame) -> pd.DataFrame:
    """Mean-center ratings per user (subtract user mean)."""
    df = ratings.copy()
    user_means = df.groupby("user_id")["rating"].transform("mean")
    df["rating_normalized"] = df["rating"] - user_means
    return df


def filter_active_users(ratings: pd.DataFrame, min_ratings: int = 3) -> pd.DataFrame:
    """Keep only users who have rated at least min_ratings movies."""
    counts = ratings.groupby("user_id")["movie_id"].count()
    active = counts[counts >= min_ratings].index
    filtered = ratings[ratings["user_id"].isin(active)]
    print(f"[Preprocessor] Active users (>= {min_ratings} ratings): {filtered['user_id'].nunique()}")
    return filtered.reset_index(drop=True)


def filter_popular_movies(ratings: pd.DataFrame, min_ratings: int = 2) -> pd.DataFrame:
    """Keep only movies that have received at least min_ratings ratings."""
    counts = ratings.groupby("movie_id")["user_id"].count()
    popular = counts[counts >= min_ratings].index
    filtered = ratings[ratings["movie_id"].isin(popular)]
    print(f"[Preprocessor] Popular movies (>= {min_ratings} ratings): {filtered['movie_id'].nunique()}")
    return filtered.reset_index(drop=True)


def train_test_split_ratings(ratings: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """Split ratings into train/test by randomly holding out rows per user."""
    np.random.seed(random_state)
    test_indices = []
    for _, group in ratings.groupby("user_id"):
        n_test = max(1, int(len(group) * test_size))
        test_idx = np.random.choice(group.index, size=n_test, replace=False)
        test_indices.extend(test_idx)
    test_df = ratings.loc[test_indices]
    train_df = ratings.drop(test_indices)
    print(f"[Preprocessor] Train: {len(train_df)} | Test: {len(test_df)}")
    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)
