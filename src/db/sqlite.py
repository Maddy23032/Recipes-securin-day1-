import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "recipes.db")
DB_PATH = os.path.abspath(DB_PATH)

DDL = """
CREATE TABLE IF NOT EXISTS recipes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cuisine TEXT,
  title TEXT,
  rating REAL,
  prep_time INTEGER,
  cook_time INTEGER,
  total_time INTEGER,
  description TEXT,
  nutrients TEXT,
  serves TEXT,
  url TEXT,
  calories_value INTEGER
);
CREATE INDEX IF NOT EXISTS idx_recipes_rating ON recipes(rating DESC);
CREATE INDEX IF NOT EXISTS idx_recipes_title ON recipes(title);
CREATE INDEX IF NOT EXISTS idx_recipes_cuisine ON recipes(cuisine);
CREATE INDEX IF NOT EXISTS idx_recipes_total_time ON recipes(total_time);
CREATE INDEX IF NOT EXISTS idx_recipes_calories ON recipes(calories_value);
"""

INS = (
    "INSERT INTO recipes (cuisine,title,rating,prep_time,cook_time,total_time,description,nutrients,serves,url,calories_value) "
    "VALUES (?,?,?,?,?,?,?,?,?,?,?)"
)

def conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with conn() as c:
        c.executescript(DDL)
        c.commit()
