import json
import os
from pathlib import Path
from src.utils.parser import transform
from src.db.sqlite import conn, init_db, INS

_repo_root = Path(__file__).resolve().parents[2]
SRC = os.environ.get("RECIPES_JSON", str(_repo_root / "US_recipes_null.json"))

init_db()

def to_row(x):
    return (
        x.get("cuisine"),
        x.get("title"),
        x.get("rating"),
        x.get("prep_time"),
        x.get("cook_time"),
        x.get("total_time"),
        x.get("description"),
        json.dumps(x.get("nutrients")) if x.get("nutrients") is not None else None,
        x.get("serves"),
        x.get("url"),
        x.get("calories_value"),
    )

xs = transform(SRC)

with conn() as c:
    c.executemany(INS, map(to_row, xs))
    c.commit()

print(len(xs))
