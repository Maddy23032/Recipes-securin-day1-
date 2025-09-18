import os
import json
import requests
import streamlit as st
from typing import Any, Dict, List, Optional
import os
import json
import requests
import streamlit as st

API = os.environ.get("RECIPES_API_BASE", "http://127.0.0.1:8000")
st.set_page_config(page_title="Recipes", layout="wide")

def stars(x):
    try:
        v = float(x)
    except Exception:
        return "—"
    f = int(v)
    h = 1 if v - f >= 0.5 else 0
    e = 5 - f - h
    return "".join(["★"*f, "☆"*h, "✩"*max(0, e)])

@st.cache_data(show_spinner=False)
def get_list(p, l):
    r = requests.get(f"{API}/api/recipes", params={"page": p, "limit": l}, timeout=20)
    r.raise_for_status()
    return r.json()

@st.cache_data(show_spinner=False)
def get_search(q):
    r = requests.get(f"{API}/api/recipes/search", params=q, timeout=20)
    r.raise_for_status()
    return r.json()

@st.cache_data(show_spinner=False)
def get_cuis():
    r = requests.get(f"{API}/api/cuisines", params={"limit": 200}, timeout=20)
    r.raise_for_status()
    d = r.json().get("data", [])
    return [x.get("cuisine") for x in d if x.get("cuisine")]

@st.cache_data(show_spinner=False)
def get_titles():
    r = requests.get(f"{API}/api/titles", params={"limit": 200}, timeout=20)
    r.raise_for_status()
    d = r.json().get("data", [])
    return [x.get("title") for x in d if x.get("title")]

with st.sidebar:
    tsel = st.selectbox("Title (exact)", ["(Any)"] + get_titles(), index=0)
    tcontains = st.text_input("Or: Title contains")
    csel = st.selectbox("Cuisine (exact)", ["(Any)"] + get_cuis(), index=0)
    a, b = st.columns(2)
    with a:
        rmin = st.number_input("Rating ≥", 0.0, 5.0, 0.0, 0.1)
    with b:
        rmax = st.number_input("Rating ≤", 0.0, 5.0, 5.0, 0.1)
    c, d = st.columns(2)
    with c:
        ttl = st.number_input("Total Time ≤ (min)", min_value=0, step=5)
    with d:
        cal = st.number_input("Calories ≤", min_value=0, step=10)
    sort = st.selectbox(
        "Sort by",
        [
            "rating:desc","rating:asc","total_time:asc","total_time:desc",
            "calories_value:asc","calories_value:desc","title:asc","title:desc",
            "cuisine:asc","cuisine:desc","id:asc","id:desc",
        ],
        index=0,
    )
    st.markdown("---")
    ps = st.select_slider("Results per page", [15,20,25,30,40,50], value=15)

q = {"page": st.session_state.get("page", 1), "limit": int(ps), "sort": sort}
if tsel and tsel != "(Any)":
    q["title"] = tsel
elif tcontains:
    q["title"] = tcontains
if csel and csel != "(Any)":
    q["cuisine"] = csel
if rmin > 0:
    q["rating_gte"] = rmin
if rmax < 5:
    q["rating_lte"] = rmax
if ttl > 0:
    q["total_time_lte"] = int(ttl)
if cal > 0:
    q["calories_lte"] = int(cal)

use_s = any(k in q for k in ("title","cuisine","rating_gte","rating_lte","total_time_lte","calories_lte"))
try:
    res = get_search(q) if use_s else get_list(q["page"], q["limit"])
except requests.RequestException as e:
    st.error(f"Failed to fetch recipes: {e}")
    st.stop()

p = res.get("page", 1)
l = res.get("limit", int(ps))
t = res.get("total", 0)
rows = res.get("data", [])

L, R = st.columns([3,2])
with L:
    st.subheader("Recipes")
    if not rows and t == 0:
        st.info("No data found. Seed the database first or adjust filters.")
    elif not rows and t > 0:
        st.warning("No results match your filters.")
    else:
        h1,h2,h3,h4,h5 = st.columns([4,2,2,2,2])
        h1.write("**Title**"); h2.write("**Cuisine**"); h3.write("**Rating**"); h4.write("**Total Time**"); h5.write("**Serves**")
        for r in rows:
            c1,c2,c3,c4,c5 = st.columns([4,2,2,2,2])
            ttlbl = r.get("title") or "(untitled)"
            tt = ttlbl[:67] + "…" if len(ttlbl) > 70 else ttlbl
            if c1.button(tt, key=f"rowbtn_{r.get('id')}", type="primary"):
                st.session_state["selected"] = r
            c2.write(r.get("cuisine") or "—")
            c3.write(stars(r.get("rating")))
            c4.write(str(r.get("total_time") or "—"))
            c5.write(str(r.get("serves") or "—"))

    st.markdown("---")
    tp = max(1, (t + l - 1) // l)
    dp = min(max(1, p), tp)
    cp = st.number_input("Page", 1, tp, dp, 1)
    x,y,z = st.columns(3)
    with x:
        if st.button("Prev", disabled=cp <= 1):
            st.session_state["page"] = max(1, cp - 1); st.rerun()
    with y:
        st.write(f"Page {cp} of {tp}")
    with z:
        if st.button("Next", disabled=cp >= tp):
            st.session_state["page"] = min(tp, cp + 1); st.rerun()
    if cp != p:
        st.session_state["page"] = int(cp); st.rerun()

with R:
    st.subheader("Details")
    s = st.session_state.get("selected")
    if not s:
        st.caption("Select a recipe row to view details.")
    else:
        st.markdown(f"### {s.get('title') or '(untitled)'}")
        st.caption(s.get("cuisine") or "")
        d = s.get("description") or "—"
        st.write(f"**Description**: {d}")
        with st.expander("Total Time details"):
            st.write(f"Total Time: {s.get('total_time') or '—'}")
            a,b = st.columns(2)
            with a: st.write(f"Prep Time: {s.get('prep_time') or '—'}")
            with b: st.write(f"Cook Time: {s.get('cook_time') or '—'}")
        st.markdown("#### Nutrition")
        n = s.get("nutrients")
        if isinstance(n, str):
            try: n = json.loads(n)
            except Exception: n = None
        if not n:
            st.caption("No nutrition data.")
        else:
            ks = ["calories","carbohydrateContent","cholesterolContent","fiberContent","proteinContent","saturatedFatContent","sodiumContent","sugarContent","fatContent"]
            m = {k: n.get(k) for k in ks}
            st.table({"Nutrient": list(m.keys()), "Value": list(m.values())})

st.caption("API: " + API)
            # Title as a button to open details
