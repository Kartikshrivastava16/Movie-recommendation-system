# 🎬 CineMatch — Movie Recommendation System (Django)

> Server runs on **http://127.0.0.1:8000** — all API calls use this base URL.

---

## ✅ Project Structure

```
movie recommendation system/
├── manage.py               ← Django entry point
├── run.bat                 ← One-click launcher
├── requirements.txt
│
├── cinematch/              ← Django project config
│   ├── __init__.py
│   ├── settings.py         ← ALLOWED_HOSTS includes 127.0.0.1
│   ├── urls.py
│   └── wsgi.py
│
├── recommender_app/        ← Django app
│   ├── __init__.py
│   ├── apps.py
│   ├── ml_engine.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   │   └── recommender_app/
│   │       └── index.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js       ← API base: http://127.0.0.1:8000
│
├── models/                 ← ML algorithms
│   ├── __init__.py
│   ├── collaborative_filtering.py
│   ├── content_based.py
│   └── hybrid.py
│
└── data/                   ← CSV data
    ├── movies.csv
    ├── ratings.csv
    └── users.csv
```

---

## 🚀 How to Run

### Option 1 — Double-click `run.bat`

### Option 2 — Terminal
```bash
pip install django pandas numpy scikit-learn
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

### Then open browser:
```
http://127.0.0.1:8000
```

> ⚠️ Use `http://` NOT `https://` — the dev server does not support HTTPS.
> ⚠️ Use `127.0.0.1` NOT `localhost` — the JS API base is hardcoded to `http://127.0.0.1:8000`.

---

## 🌐 API Endpoints (base: http://127.0.0.1:8000)

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/data/stats` | Movie/user/rating counts |
| GET | `/api/data/movies` | All movies |
| GET | `/api/data/users` | All users |
| GET | `/api/search?q=<query>` | Search movies |
| POST | `/api/recommend/collaborative/` | User-based CF |
| POST | `/api/recommend/content-based/` | Content-based |
| POST | `/api/recommend/hybrid/` | Hybrid (CF + CB) |

---

## ❌ Files NOT Needed (Can Delete)

- `api.py` — old Flask server
- `main.py` — old CLI demo
- `recommender.py` — old standalone script
- `install_deps.py` — replaced by pip
- `test_setup.py` — not needed
- `FIXED.md`, `SETUP.md` — old docs
- `frontend/` folder — now inside recommender_app/
- `app/` folder — empty, unused

---

## 👤 Author
Kartik Shrivastava
