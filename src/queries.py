
# src/queries.py

import sqlite3
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "manufacturing.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def product_output_by_month(month_prefix: str):
    """
    month_prefix: 'YYYY-MM' (we match op_start LIKE 'YYYY-MM%')
    Returns list of rows per product with good_qty, scrap_qty, num_orders.
    """
    like = f"{month_prefix}%"
    sql = """
    SELECT p.name AS product_name,
           COALESCE(SUM(o.good_qty),0)  AS good_qty,
           COALESCE(SUM(o.scrap_qty),0) AS scrap_qty,
           COUNT(DISTINCT o.work_order_id) AS num_orders
    FROM products p
    LEFT JOIN work_orders w ON w.product_id = p.id
    LEFT JOIN operations o   ON o.work_order_id = w.id
    WHERE o.op_start LIKE ?
    GROUP BY p.name
    ORDER BY p.name;
    """
    with get_conn() as conn:
        rows = conn.execute(sql, (like,)).fetchall()
        return [dict(r) for r in rows]

def list_wip(now_iso: str):
    sql = """
    SELECT w.id, p.name AS product, w.planned_qty, w.status, w.planned_start, w.planned_end, w.machine_id
    FROM work_orders w
    JOIN products p ON p.id = w.product_id
    WHERE w.status = 'in_progress'
       OR ( ? >= w.planned_start AND ? <= w.planned_end
            AND w.status NOT IN ('completed','cancelled') )
    ORDER BY w.planned_start;
    """
    with get_conn() as conn:
        rows = conn.execute(sql, (now_iso, now_iso)).fetchall()
        return [dict(r) for r in rows]

def machine_utilization_simple(start_iso: str, end_iso: str):
    """
    SQL-only simple utilization: runtime_hours / total_hours_in_range.
    """
    sql = """
    SELECT
      m.id AS machine_id,
      m.name AS machine_name,
      COALESCE(SUM((strftime('%s', o.op_end) - strftime('%s', o.op_start)) / 3600.0), 0.0) AS runtime_hours
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
    total_hours = (end_dt - start_dt).total_seconds() / 3600.0

    with get_conn() as conn:
        rows = conn.execute(sql, (start_iso, end_iso)).fetchall()
        result = []
        for r in rows:
            runtime_hours = float(r["runtime_hours"] or 0.0)
            util = (runtime_hours / total_hours) if total_hours > 0 else 0.0
            result.append({
                "machine_id": r["machine_id"],
                "machine_name": r["machine_name"],
                "runtime_hours": round(runtime_hours, 2),
                "total_hours": round(total_hours, 2),
                "utilization": round(util, 4),
            })
        return result

def work_orders_no_production():
    sql = """
    SELECT w.id, p.name AS product, w.status, w.planned_start, w.planned_end, w.planned_qty
    FROM work_orders w
    JOIN products p ON p.id = w.product_id
    LEFT JOIN operations o ON o.work_order_id = w.id
    WHERE w.status IN ('released','planned','delayed','in_progress')
      AND o.id IS NULL
    ORDER BY w.planned_start;
    """
    with get_conn() as conn:
        rows = conn.execute(sql).fetchall()
        return [dict(r) for r in rows]

def top_scrap_by_product(start_iso: str, end_iso: str):
    sql = """
    SELECT p.name AS product_name,
           COALESCE(SUM(o.scrap_qty),0) AS scrap_qty,
           COALESCE(SUM(o.good_qty + o.scrap_qty),0) AS total_qty,
           CASE
             WHEN COALESCE(SUM(o.good_qty + o.scrap_qty),0) = 0 THEN 0.0
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
    with get_conn() as conn:
        rows = conn.execute(sql, (start_iso, end_iso)).fetchall()
        return [dict(r) for r in rows]

def top_scrap_by_machine(start_iso: str, end_iso: str):
    sql = """
    SELECT m.name AS machine_name,
           COALESCE(SUM(o.scrap_qty),0) AS scrap_qty,
           COALESCE(SUM(o.good_qty + o.scrap_qty),0) AS total_qty,
           CASE
             WHEN COALESCE(SUM(o.good_qty + o.scrap_qty),0) = 0 THEN 0.0
             ELSE CAST(SUM(o.scrap_qty) AS REAL) / SUM(o.good_qty + o.scrap_qty)
           END AS scrap_rate
    FROM machines m
    JOIN operations o ON o.machine_id = m.id
    WHERE o.op_start >= ?
      AND o.op_end   <= ?
    GROUP BY m.name
    ORDER BY scrap_qty DESC, scrap_rate DESC;
    """
    with get_conn() as conn:
        rows = conn.execute(sql, (start_iso, end_iso)).fetchall()
        return [dict(r) for r in rows]
