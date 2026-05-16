# 🎬 Movie Recommendation System

> A machine learning project that suggests movies based on user preferences, viewing history, and similar user behaviour — using Collaborative Filtering, Content-Based Filtering, and a Hybrid approach.

---

## 📌 Overview

This system uses three recommendation algorithms to personalise movie suggestions:

- **Collaborative Filtering** — finds users with similar rating patterns and recommends what they liked
- **Content-Based Filtering** — recommends movies similar to ones a user already enjoys, using TF-IDF on genres, cast, and metadata
- **Hybrid Model** — blends both approaches with adjustable weights for better accuracy and coverage

The frontend is a pure **HTML/CSS/JavaScript** single-page app (no framework required). The backend logic is written in **Python** with scikit-learn.

---

## 📁 Project Structure

```
movie recommendation system/
│
├── frontend/                   # Web UI (open index.html in browser)
│   ├── index.html              # Main page
│   ├── style.css               # Cinematic dark theme
│   └── app.js                  # Recommendation logic & interactivity
│
├── data/                       # Dataset files
│   ├── movies.csv              # Movie metadata (id, title, genres, ...)
│   ├── ratings.csv             # User ratings (user_id, movie_id, rating)
│   └── users.csv               # User profiles
│
├── models/                     # ML model implementations
│   ├── __init__.py
│   ├── collaborative_filtering.py   # UserBasedCF & ItemBasedCF classes
│   ├── content_based.py             # ContentBasedFilter (TF-IDF)
│   └── hybrid.py                    # HybridRecommender
│
├── utils/                      # Helper utilities
│   ├── __init__.py
│   ├── data_loader.py          # load_all(), CSV loaders
│   ├── preprocessor.py         # clean_ratings(), filter_active_users(), splits
│   └── display.py              # print_recommendations(), print_movie_details()
│
├── evaluation/                 # Model evaluation
│   ├── metrics.py              # RMSE, MAE, Precision@K, Recall@K, NDCG@K
│   └── evaluate.py             # evaluate_model() runner
│
├── tests/                      # Unit tests
│   ├── test_models.py
│   └── test_utils.py
│
├── main.py                     # Full demo — runs all algorithms end-to-end
├── recommender.py              # Core standalone recommender functions
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Kartikshrivastava16/Movie-recommendation-system.git
cd "movie recommendation system"
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

### ▶ Run the full demo (all algorithms)

```bash
python main.py
```

This fits all four models (User-Based CF, Item-Based CF, Content-Based, Hybrid) and prints top-5 recommendations for several users and seed movies.

### 🌐 Launch the frontend

Just open the file in any browser — no server needed:

```
frontend/index.html
```

Or via terminal:

```bash
# Windows
start frontend/index.html

# macOS
open frontend/index.html

# Linux
xdg-open frontend/index.html
```

---

## 🧠 Algorithms

### User-Based Collaborative Filtering (`UserBasedCF`)

Builds a **user × movie** rating matrix, computes **cosine similarity** between users, then aggregates weighted ratings from the most similar users to score unseen movies.

```python
from models import UserBasedCF

model = UserBasedCF(n_similar_users=5)
model.fit(ratings)
recs = model.recommend(user_id=1, top_n=5)
```

### Item-Based Collaborative Filtering (`ItemBasedCF`)

Computes **item × item** cosine similarity. For a given user, scores unrated movies by how similar they are to the user's already-rated movies, weighted by those ratings.

```python
from models import ItemBasedCF

model = ItemBasedCF()
model.fit(ratings)
recs = model.recommend(user_id=1, top_n=5)
```

### Content-Based Filtering (`ContentBasedFilter`)

Builds a **TF-IDF matrix** from each movie's genres, director, cast, and description. Recommends movies with the highest cosine similarity to a seed movie or a genre query.

```python
from models.content_based import ContentBasedFilter

model = ContentBasedFilter()
model.fit(movies)

# By title
recs = model.recommend_by_title("Inception", top_n=5)

# By genres
recs = model.recommend_by_genres(["Action", "Sci-Fi"], top_n=5)
```

### Hybrid Recommender (`HybridRecommender`)

Combines User-Based CF and Content-Based scores using **reciprocal rank fusion** with configurable weights (default: 60% CF, 40% content-based).

```python
from models.hybrid import HybridRecommender

model = HybridRecommender(cf_weight=0.6, cb_weight=0.4)
model.fit(movies, ratings)
recs = model.recommend(user_id=1, top_n=5)
```

---

## 📊 Evaluation Metrics

Implemented in `evaluation/metrics.py`:

| Metric | Description |
|--------|-------------|
| `RMSE` | Root Mean Squared Error on rating predictions |
| `MAE` | Mean Absolute Error on rating predictions |
| `Precision@K` | Fraction of top-K recommendations that are relevant |
| `Recall@K` | Fraction of all relevant items captured in top-K |
| `NDCG@K` | Normalized Discounted Cumulative Gain — rewards ranking relevant items higher |

```python
from evaluation.metrics import evaluate_model

results = evaluate_model(model, test_ratings, movies, k=5)
# {'Precision@5': 0.42, 'Recall@5': 0.31, 'NDCG@5': 0.38}
```

---

## 🗃️ Dataset

The `data/` folder contains three CSV files:

| File | Columns | Description |
|------|---------|-------------|
| `movies.csv` | `movie_id`, `title`, `genres`, `director`, `cast`, `year` | Movie metadata |
| `ratings.csv` | `user_id`, `movie_id`, `rating` | User–movie ratings (1–5 scale) |
| `users.csv` | `user_id`, `age`, `gender`, `occupation` | User profiles |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.8+ |
| ML / Data | pandas, NumPy, scikit-learn |
| Similarity | Cosine Similarity, TF-IDF |
| Visualisation | Matplotlib, Seaborn |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Charts | Canvas API (custom radar chart) |

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

---

## 👤 Author

**Kartik Shrivastava**
- GitHub: [@Kartikshrivastava16](https://github.com/Kartikshrivastava16)

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
