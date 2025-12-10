
# src/setup_db.py

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "manufacturing.db"
SCHEMA_SQL = ROOT / "sql" / "001_schema.sql"
SEED_SQL = ROOT / "sql" / "002_seed.sql"

def run_sql_file(conn: sqlite3.Connection, sql_path: Path):
    with sql_path.open("r", encoding="utf-8") as f:
        sql = f.read()
    conn.executescript(sql)

def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Creating/Opening DB at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        print(f"[INFO] Applying schema: {SCHEMA_SQL}")
        run_sql_file(conn, SCHEMA_SQL)
        print(f"[INFO] Seeding data: {SEED_SQL}")
        run_sql_file(conn, SEED_SQL)
        conn.commit()
        print("[SUCCESS] Database ready with demo data.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
