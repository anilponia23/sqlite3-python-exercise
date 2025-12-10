
"""
Manufacturing Data Platform – Query Wrappers (SQLite)
----------------------------------------------------
Purpose:
  Thin, readable Python functions that execute the Task 2 SQL queries
  against manufacturing.db, returning lists of dicts suitable for printing
  or further processing.

Notes:
  - Uses parameterized queries (safe, avoids SQL injection).
  - Returns rows as dictionaries (sqlite3.Row + dict()).
  - Date/times expected as ISO 8601 UTC strings: 'YYYY-MM-DDTHH:MM:SSZ'.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "manufacturing.db"

def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def product_output_by_month(month_prefix: str):
    """
    For a given month (YYYY-MM), return per-product:
      - Total good quantity
      - Total scrap quantity
      - Number of work orders involved (with ops in that month)

    Logic:
      We consider operations whose op_start matches 'YYYY-MM%'.
    """
    like = f"{month_prefix}%"
    sql = """
    SELECT p.name AS product_name,
           COALESCE(SUM(o.good_qty), 0)  AS good_qty,
           COALESCE(SUM(o.scrap_qty), 0) AS scrap_qty,
           COUNT(DISTINCT o.work_order_id) AS num_orders
    FROM products p
    LEFT JOIN work_orders w ON w.product_id = p.id
    LEFT JOIN operations o   ON o.work_order_id = w.id
    WHERE o.op_start LIKE ?
    GROUP BY p.name
    ORDER BY p.name;
    """
    with _conn() as conn:
        rows = conn.execute(sql, (like,)).fetchall()
        return [dict(r) for r in rows]

def list_wip(now_iso: str):
    """
    List current work-in-progress orders.

    Definition:
      - status = 'in_progress'
      OR
      - now between planned_start and planned_end AND status NOT IN ('completed','cancelled')
    """
    sql = """
    SELECT w.id,
           p.name AS product,
           w.planned_qty,
           w.status,
           w.planned_start,
           w.planned_end,
           w.machine_id
    FROM work_orders w
    JOIN products p ON p.id = w.product_id
    WHERE w.status = 'in_progress'
       OR ( ? >= w.planned_start AND ? <= w.planned_end
            AND w.status NOT IN ('completed','cancelled') )
    ORDER BY w.planned_start;
    """
    with _conn() as conn:
        rows = conn.execute(sql, (now_iso, now_iso)).fetchall()
        return [dict(r) for r in rows]

def machine_utilization_simple(start_iso: str, end_iso: str):
    """
    Compute simple machine utilization for a date range:
      utilization = runtime_hours / total_hours_in_range

    Notes:
      - runtime_hours: sum of (op_end - op_start) over operations fully within the range
      - total_hours_in_range: computed from start/end ISO timestamps
      - This SQL-only metric does NOT subtract downtime; for adjusted metric use dal.get_machine_utilization().
    """
    sql = """
    SELECT
      m.id   AS machine_id,
      m.name AS machine_name,
      COALESCE(SUM((strftime('%s', o.op_end) - strftime('%s', o.op_start)) / 3600.0), 0.0)
        AS runtime_hours
    FROM machines m
    LEFT JOIN operations o
      ON o.machine_id = m.id
     AND o.op_start >= ?
     AND o.op_end   <= ?
    GROUP BY m.id, m.name
    ORDER BY m.id;
    """
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    start_dt = datetime.strptime(start_iso, fmt)
    end_dt = datetime.strptime(end_iso, fmt)
    total_hours = max(0.0, (end_dt - start_dt).total_seconds() / 3600.0)

    with _conn() as conn:
        rows = conn.execute(sql, (start_iso, end_iso)).fetchall()
        result = []
        for r in rows:
            runtime = float(r["runtime_hours"] or 0.0)
            util = (runtime / total_hours) if total_hours > 0 else 0.0
            result.append({
                "machine_id": r["machine_id"],
                "machine_name": r["machine_name"],
                "runtime_hours": round(runtime, 2),
                "total_hours": round(total_hours, 2),
                "utilization": round(util, 4),
            })
        return result

def work_orders_no_production():
    """
    List all work orders that are released/scheduled but have no operations yet.

    Included statuses: 'released','planned','delayed','in_progress'.
    """
    sql = """
    SELECT w.id,
           p.name AS product,
           w.status,
           w.planned_start,
           w.planned_end,
           w.planned_qty
    FROM work_orders w
    JOIN products p ON p.id = w.product_id
    LEFT JOIN operations o ON o.work_order_id = w.id
    WHERE w.status IN ('released','planned','delayed','in_progress')
      AND o.id IS NULL
    ORDER BY w.planned_start;
    """
    with _conn() as conn:
        rows = conn.execute(sql).fetchall()
        return [dict(r) for r in rows]

def top_scrap_by_product(start_iso: str, end_iso: str):
    """
    For a date range, return scrap drivers by product:
      - scrap_qty
      - total_qty (good + scrap)
      - scrap_rate (scrap / total)
    """
    sql = """
    SELECT p.name AS product_name,
           COALESCE(SUM(o.scrap_qty), 0) AS scrap_qty,
           COALESCE(SUM(o.good_qty + o.scrap_qty), 0) AS total_qty,
           CASE
             WHEN COALESCE(SUM(o.good_qty + o.scrap_qty), 0) = 0 THEN 0.0
             ELSE CAST(SUM(o.scrap_qty) AS REAL) / SUM(o.good_qty + o.scrap_qty)
           END AS scrap_rate
    FROM products p
    JOIN work_orders w ON w.product_id = p.id
    JOIN operations o  ON o.work_order_id = w.id
    WHERE o.op_start >= ?
      AND o.op_end   <= ?
    GROUP BY p.name
    ORDER BY scrap_qty DESC, scrap_rate DESC;
    """
    with _conn() as conn:
        rows = conn.execute(sql, (start_iso, end_iso)).fetchall()
        return [dict(r) for r in rows]

def top_scrap_by_machine(start_iso: str, end_iso: str):
    """
    For a date range, return scrap drivers by machine:
      - scrap_qty
      - total_qty (good + scrap)
      - scrap_rate (scrap / total)
    """
    sql = """
    SELECT m.name AS machine_name,
           COALESCE(SUM(o.scrap_qty), 0) AS scrap_qty,
           COALESCE(SUM(o.good_qty + o.scrap_qty), 0) AS total_qty,
           CASE
             WHEN COALESCE(SUM(o.good_qty + o.scrap_qty), 0) = 0 THEN 0.0
             ELSE CAST(SUM(o.scrap_qty) AS REAL) / SUM(o.good_qty + o.scrap_qty)
           END AS scrap_rate
    FROM machines m
    JOIN operations o ON o.machine_id = m.id
    WHERE o.op_start >= ?
      AND o.op_end   <= ?
    GROUP BY m.name
    ORDER BY scrap_qty DESC, scrap_rate DESC;
    """
    with _conn() as conn:
        rows = conn.execute(sql, (start_iso, end_iso)).fetchall()
        return [dict(r) for r in rows] #
