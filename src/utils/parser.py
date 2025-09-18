import json
import math
import re

_nan = {"nan", "na", "none", "", "null", "-"}

def _n(v):
    if v is None:
        return True
    if isinstance(v, float) and math.isnan(v):
        return True
    if isinstance(v, str) and v.strip().lower() in _nan:
        return True
    return False

def to_i(v):
    if _n(v):
        return None
    m = re.search(r"-?\d+(\.\d+)?", str(v))
    if not m:
        return None
    s = m.group(0)
    return int(float(s)) if "." in s else int(s)

def to_f(v):
    if _n(v):
        return None
    s = str(v).strip()
    if s == "":
        return None
    m = re.search(r"-?\d+(\.\d+)?", s)
    if not m:
        return None
    return float(m.group(0))

def cal(n):
    if not n:
        return None
    r = n.get("calories") or n.get("calorie") or n.get("Calories") or n.get("kcal") or n.get("energy")
    if _n(r):
        return None
    return to_i(r)

def clean(x):
    def v(d, ks):
        for k in ks:
            if k in d:
                return d.get(k)
            lk = k.lower()
            if lk in d:
                return d.get(lk)
            uk = k.upper()
            if uk in d:
                return d.get(uk)
            rk = k.replace(" ", "_")
            if rk in d:
                return d.get(rk)
            rk2 = rk.lower()
            if rk2 in d:
                return d.get(rk2)
        return None
    c = v(x, ["cuisine","Cuisine"]) or x.get("Country_State") or x.get("Contient")
    t = v(x, ["title","Title","name","recipe_title","recipeTitle"]) 
    r = to_f(v(x, ["rating","Rating","avg_rating","averageRating"]))
    if r is None:
        ar = v(x, ["aggregateRating"]) if isinstance(v(x,["aggregateRating"]), dict) else None
        if ar:
            r = to_f(ar.get("ratingValue"))
    p = to_i(v(x, ["prep_time","prep time","preparationTime","prepTime"]))
    k = to_i(v(x, ["cook_time","cook time","cookingTime","cookTime"]))
    tt = to_i(v(x, ["total_time","total time","totalTime","readyInMinutes","ready_in_minutes"]))
    d = v(x, ["description","summary","desc"])
    nraw = v(x, ["nutrients","nutrition","nutritionInfo","nutritional_info"]) 
    n = nraw if isinstance(nraw, dict) else None
    s = v(x, ["serves","servings","yield","yields","makes"]) 
    u = v(x, ["URL","url","link","sourceUrl"]) 
    cv = cal(n)
    if tt is None and (p is not None and k is not None):
        tt = p + k
    o = {
        "cuisine": c,
        "title": t,
        "rating": r,
        "prep_time": p,
        "cook_time": k,
        "total_time": tt,
        "description": d,
        "nutrients": n,
        "serves": s,
        "url": u,
        "calories_value": cv,
    }
    return {k: v for k, v in o.items() if v is not None}

def load(pth):
    with open(pth, "r", encoding="utf-8") as f:
        txt = f.read()
    s = txt.strip()
    if s == "":
        return []
    if s[0] in "[{":
        d = json.loads(s)
    else:
        xs = []
        for ln in txt.splitlines():
            t = ln.strip()
            if not t:
                continue
            if t[0] != "{":
                continue
            y = json.loads(t)
            if isinstance(y, dict):
                xs.append(y)
        return xs
    if isinstance(d, list):
        return d
    if isinstance(d, dict):
        if "data" in d and isinstance(d["data"], list):
            return d["data"]
        if d and all(isinstance(v, dict) for v in d.values()):
            return list(d.values())
        for _, v in d.items():
            if isinstance(v, list):
                return v
        return [d]
    return []

def transform(pth):
    xs = load(pth)
    ys = []
    for x in xs:
        if isinstance(x, dict):
            z = clean(x)
            if z.get("title"):
                ys.append(z)
    return ys
