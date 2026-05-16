"""
display.py
===========
Pretty-print helpers for recommendation results.
"""

import pandas as pd


def print_recommendations(movie_ids: list, movies: pd.DataFrame, label: str = "Recommendations"):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    if not movie_ids:
        print("  No recommendations available.")
        return
    for rank, mid in enumerate(movie_ids, start=1):
        row = movies[movies["movie_id"] == mid]
        if row.empty:
            continue
        r = row.iloc[0]
        title   = r.get("title", "Unknown")
        genres  = r.get("genres", "N/A")
        year    = r.get("year", "")
        avg_rat = r.get("rating_avg", "")
        yr_str  = f" ({year})" if year else ""
        rat_str = f"  ⭐ {avg_rat}" if avg_rat else ""
        print(f"  {rank:2}. {title}{yr_str}  [{genres}]{rat_str}")


def print_movie_details(movie_id: int, movies: pd.DataFrame):
    row = movies[movies["movie_id"] == movie_id]
    if row.empty:
        print(f"Movie ID {movie_id} not found.")
        return
    r = row.iloc[0]
    print(f"\n{'─'*60}")
    print(f"  🎬 {r.get('title')} ({r.get('year', 'N/A')})")
    print(f"  Genres   : {r.get('genres', 'N/A')}")
    print(f"  Director : {r.get('director', 'N/A')}")
    print(f"  Cast     : {r.get('cast', 'N/A').replace('|', ', ')}")
    print(f"  Rating   : ⭐ {r.get('rating_avg', 'N/A')}")
    print(f"  Synopsis : {r.get('description', 'N/A')}")
    print(f"{'─'*60}")


def print_similar_users(similar_users: pd.Series, users: pd.DataFrame):
    print(f"\n  {'─'*40}")
    print(f"  Similar Users:")
    for uid, score in similar_users.items():
        row = users[users["user_id"] == uid]
        name = row.iloc[0]["name"] if not row.empty else f"User {uid}"
        print(f"    • {name} (similarity: {score:.3f})")
