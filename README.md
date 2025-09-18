# Recipes (FastAPI + Streamlit)

Simple steps to run the backend API and frontend UI on Windows (PowerShell).

## 1) Setup
```powershell
py -m venv .venv
.\.venv\Scripts\activate
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

Place the data file `US_recipes_null.json` in the project root.

## 2) Seed the database (SQLite)
```powershell
py -m src.db.seed_sqlite
```

## 3) Run the backend (FastAPI)
```powershell
uvicorn src.app:app --reload
```
Backend URL: http://127.0.0.1:8000

## 4) Run the frontend (Streamlit)
Open a new PowerShell window in the project directory and run:
```powershell
streamlit run src/ui_streamlit.py
```

If your API runs on a different host/port:
```powershell
$env:RECIPES_API_BASE = "http://localhost:8000"; streamlit run src/ui_streamlit.py
```

## API (quick reference)

- GET `/` → `{ "message": "Recipe API is running" }`
- GET `/health` → `{ "status": "ok" }`
- GET `/api/recipes` → paginated list
	- Query: `page` (default 1), `limit` (default 10)
- GET `/api/recipes/search` → filtered + paginated list
	- Query (all optional unless noted):
		- `page`, `limit`, `sort` as `field:dir` (e.g., `rating:desc`)
		- Text: `title` (partial/contains), `cuisine` (exact value)
		- Rating: `rating_gt|gte|lt|lte|eq` (float 0–5)
		- Total time (minutes): `total_time_gt|gte|lt|lte|eq` (int)
		- Calories: `calories_gt|gte|lt|lte|eq` (int)
	- Sortable fields: `rating`, `total_time`, `calories_value`, `title`, `cuisine`, `id`
- GET `/api/cuisines` → `{ data: [{ cuisine, count }] }` (for dropdowns)
- GET `/api/titles` → `{ data: [{ title, count }] }` (for dropdowns)

Example:
```
http://127.0.0.1:8000/api/recipes/search?title=pie&rating_gte=4.5&calories_lte=600&sort=rating:desc
```

## Data model (columns)

Each recipe row has:
- `id` (int) unique id
- `cuisine` (string) e.g., "Southern Recipes"
- `title` (string)
- `rating` (float 0–5)
- `prep_time` (int minutes)
- `cook_time` (int minutes)
- `total_time` (int minutes)
- `description` (string)
- `nutrients` (object) keys may include:
	- `calories`, `carbohydrateContent`, `cholesterolContent`, `fiberContent`,
		`proteinContent`, `saturatedFatContent`, `sodiumContent`, `sugarContent`, `fatContent`
- `serves` (int or string, source-dependent)
- `url` (string)
- `calories_value` (int) normalized calories (derived from `nutrients`)
