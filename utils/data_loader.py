"""
data_loader.py
===============
Handles loading and basic validation of all CSV datasets.
"""

import pandas as pd
import os


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_movies(path: str = None) -> pd.DataFrame:
    path = path or os.path.join(DATA_DIR, "movies.csv")
    df = pd.read_csv(path)
    assert "movie_id" in df.columns and "title" in df.columns, "Invalid movies file."
    print(f"[DataLoader] Loaded {len(df)} movies.")
    return df


def load_ratings(path: str = None) -> pd.DataFrame:
    path = path or os.path.join(DATA_DIR, "ratings.csv")
    df = pd.read_csv(path)
    assert {"user_id", "movie_id", "rating"}.issubset(df.columns), "Invalid ratings file."
    print(f"[DataLoader] Loaded {len(df)} ratings.")
    return df


def load_users(path: str = None) -> pd.DataFrame:
    path = path or os.path.join(DATA_DIR, "users.csv")
    df = pd.read_csv(path)
    print(f"[DataLoader] Loaded {len(df)} users.")
    return df


def load_all():
    """Load and return all three datasets."""
    return load_movies(), load_ratings(), load_users()
