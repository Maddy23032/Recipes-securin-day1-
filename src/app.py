from fastapi import FastAPI, Query
import sqlite3
from src.db.sqlite import conn
from src.utils.parser import to_i, to_f

app = FastAPI(title="Recipe API", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Recipe API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

cols = "id,cuisine,title,rating,prep_time,cook_time,total_time,description,nutrients,serves,url,calories_value"

def parse_sort(s):
    f = "rating"
    d = "desc"
    if s:
        p = s.split(":")
        if len(p) == 2 and p[0]:
            f = p[0]
            d = p[1]
    dirv = "DESC" if str(d).lower() in ("desc","-1","descending") else "ASC"
    if f not in {"rating","total_time","calories_value","title","cuisine","id"}:
        f = "rating"
    if f == "rating":
        return "ORDER BY rating IS NULL, rating {}".format(dirv)
    return "ORDER BY {} {}".format(f, dirv)

@app.get("/api/recipes")
def get_recipes(page=Query(1), limit=Query(10)):
    p = to_i(page)
    l = to_i(limit)
    if not p or p < 1:
        p = 1
    if not l or l < 1:
        l = 10
    if l > 100:
        l = 100
    off = (p - 1) * l
    with conn() as c:
        c.row_factory = sqlite3.Row
        t = c.execute("SELECT COUNT(*) AS n FROM recipes").fetchone()[0]
        srt = parse_sort("rating:desc")
        q = "SELECT {} FROM recipes {} LIMIT ? OFFSET ?".format(cols, srt)
        rows = c.execute(q, (l, off)).fetchall()
        data = [dict(r) for r in rows]
    return {"page": p, "limit": l, "total": t, "data": data}

@app.get("/api/recipes/search")
def search_recipes(
    page=Query(1),
    limit=Query(10),
    title=None,
    cuisine=None,
    rating_gt=None,
    rating_gte=None,
    rating_lt=None,
    rating_lte=None,
    rating_eq=None,
    total_time_gt=None,
    total_time_gte=None,
    total_time_lt=None,
    total_time_lte=None,
    total_time_eq=None,
    calories_gt=None,
    calories_gte=None,
    calories_lt=None,
    calories_lte=None,
    calories_eq=None,
    sort=Query("rating:desc"),
):
    p = to_i(page)
    l = to_i(limit)
    if not p or p < 1:
        p = 1
    if not l or l < 1:
        l = 10
    if l > 100:
        l = 100
    off = (p - 1) * l
    wh = []
    pa = []
    if title:
        wh.append("LOWER(title) LIKE ?")
        pa.append("%" + title.lower() + "%")
    if cuisine:
        wh.append("cuisine = ?")
        pa.append(cuisine)
    def add_num(f, gt, gte, lt, lte, eq, is_int=False):
        if eq is not None:
            v = to_i(eq) if is_int else to_f(eq)
            if v is not None:
                wh.append(f+" = ?")
                pa.append(v)
            return
        if gt is not None:
            v = to_i(gt) if is_int else to_f(gt)
            if v is not None:
                wh.append(f+" > ?")
                pa.append(v)
        if gte is not None:
            v = to_i(gte) if is_int else to_f(gte)
            if v is not None:
                wh.append(f+" >= ?")
                pa.append(v)
        if lt is not None:
            v = to_i(lt) if is_int else to_f(lt)
            if v is not None:
                wh.append(f+" < ?")
                pa.append(v)
        if lte is not None:
            v = to_i(lte) if is_int else to_f(lte)
            if v is not None:
                wh.append(f+" <= ?")
                pa.append(v)
    add_num("rating", rating_gt, rating_gte, rating_lt, rating_lte, rating_eq, False)
    add_num("total_time", total_time_gt, total_time_gte, total_time_lt, total_time_lte, total_time_eq, True)
    add_num("calories_value", calories_gt, calories_gte, calories_lt, calories_lte, calories_eq, True)
    sqlw = (" WHERE " + " AND ".join(wh)) if wh else ""
    srt = parse_sort(sort)
    with conn() as c:
        c.row_factory = sqlite3.Row
        t = c.execute("SELECT COUNT(*) AS n FROM recipes" + sqlw, tuple(pa)).fetchone()[0]
        q = "SELECT {} FROM recipes{} {} LIMIT ? OFFSET ?".format(cols, sqlw, srt)
        rows = c.execute(q, tuple(pa)+ (l, off)).fetchall()
        data = [dict(r) for r in rows]
    return {"page": p, "limit": l, "total": t, "data": data}

@app.get("/api/cuisines")
def list_cuisines(q: str | None = Query(None), limit: int = Query(200)):
    l = to_i(limit) or 200
    if l < 1:
        l = 1
    if l > 1000:
        l = 1000
    wh = []
    pa = []
    wh.append("cuisine IS NOT NULL")
    if q:
        wh.append("LOWER(cuisine) LIKE ?")
        pa.append("%" + q.lower() + "%")
    sqlw = (" WHERE " + " AND ".join(wh)) if wh else ""
    with conn() as c:
        c.row_factory = sqlite3.Row
        rows = c.execute(
            f"SELECT cuisine, COUNT(*) AS n FROM recipes{sqlw} GROUP BY cuisine ORDER BY n DESC LIMIT ?",
            tuple(pa) + (l,),
        ).fetchall()
        data = [{"cuisine": r["cuisine"], "count": r["n"]} for r in rows]
    return {"data": data}

@app.get("/api/titles")
def list_titles(q: str | None = Query(None), limit: int = Query(200)):
    l = to_i(limit) or 200
    if l < 1:
        l = 1
    if l > 1000:
        l = 1000
    wh = ["title IS NOT NULL"]
    pa = []
    if q:
        wh.append("LOWER(title) LIKE ?")
        pa.append("%" + q.lower() + "%")
    sqlw = " WHERE " + " AND ".join(wh)
    with conn() as c:
        c.row_factory = sqlite3.Row
        rows = c.execute(
            f"SELECT title, COUNT(*) AS n FROM recipes{sqlw} GROUP BY title ORDER BY n DESC LIMIT ?",
            tuple(pa) + (l,),
        ).fetchall()
        data = [{"title": r["title"], "count": r["n"]} for r in rows]
    return {"data": data}
