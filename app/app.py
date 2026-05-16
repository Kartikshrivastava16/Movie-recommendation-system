"""
app.py
=======
Simple CLI interface for the Movie Recommendation System.
Lets the user interactively pick a mode and get recommendations.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils import load_all, clean_ratings
from models import UserBasedCF, ItemBasedCF, HybridRecommender
from models.content_based import ContentBasedFilter
from utils.display import print_recommendations, print_movie_details, print_similar_users


def banner():
    print("""
╔══════════════════════════════════════════════════╗
║       🎬  MOVIE RECOMMENDATION SYSTEM  🎬        ║
║   Collaborative | Content-Based | Hybrid         ║
╚══════════════════════════════════════════════════╝
""")


def menu():
    print("  Select Mode:")
    print("  [1] Recommend for a User       (User-Based CF)")
    print("  [2] Find Similar Movies        (Content-Based)")
    print("  [3] Hybrid Recommendations     (CF + Content)")
    print("  [4] Item-Based CF              (Item-Based CF)")
    print("  [5] View Movie Details")
    print("  [6] Show Similar Users")
    print("  [0] Exit")
    return input("\n  Enter choice: ").strip()


def main():
    banner()
    print("  Loading data...")
    movies, ratings, users = load_all()
    ratings = clean_ratings(ratings)

    # Fit models
    ub_model     = UserBasedCF(n_similar_users=5);   ub_model.fit(ratings)
    ib_model     = ItemBasedCF();                     ib_model.fit(ratings)
    cb_model     = ContentBasedFilter();              cb_model.fit(movies)
    hybrid_model = HybridRecommender();               hybrid_model.fit(movies, ratings)

    print("\n  ✅ All models ready!\n")

    while True:
        choice = menu()

        if choice == "0":
            print("\n  👋 Goodbye!\n")
            break

        elif choice == "1":
            uid = input("  Enter User ID (1-10): ").strip()
            try:
                recs = ub_model.recommend(int(uid), top_n=5)
                print_recommendations(recs, movies, f"User-Based CF — Top 5 for User {uid}")
            except ValueError:
                print("  Invalid User ID.")

        elif choice == "2":
            title = input("  Enter movie title: ").strip()
            recs = cb_model.recommend_by_title(title, top_n=5)
            print_recommendations(recs, movies, f"Content-Based — Similar to '{title}'")

        elif choice == "3":
            uid = input("  Enter User ID (1-10): ").strip()
            try:
                recs = hybrid_model.recommend(int(uid), top_n=5)
                print_recommendations(recs, movies, f"Hybrid — Top 5 for User {uid}")
            except ValueError:
                print("  Invalid User ID.")

        elif choice == "4":
            uid = input("  Enter User ID (1-10): ").strip()
            try:
                recs = ib_model.recommend(int(uid), top_n=5)
                print_recommendations(recs, movies, f"Item-Based CF — Top 5 for User {uid}")
            except ValueError:
                print("  Invalid User ID.")

        elif choice == "5":
            mid = input("  Enter Movie ID (1-30): ").strip()
            try:
                print_movie_details(int(mid), movies)
            except ValueError:
                print("  Invalid Movie ID.")

        elif choice == "6":
            uid = input("  Enter User ID (1-10): ").strip()
            try:
                similar = ub_model.get_similar_users(int(uid), top_n=5)
                print_similar_users(similar, users)
            except ValueError:
                print("  Invalid User ID.")

        else:
            print("  Invalid choice. Try again.")

        print()


if __name__ == "__main__":
    main()
