
"""
Manufacturing Data Platform – Data Access Layer (SQLite)
--------------------------------------------------------
Purpose:
  Python functions that provide a simple, safe interface to the database for
  the take-home exercise. These directly satisfy Task 3 requirements.

Conventions:
  - SQLite connections enforce foreign keys (PRAGMA).
  - Timestamps are ISO 8601 UTC strings: 'YYYY-MM-DDTHH:MM:SSZ'.
  - Parameterized queries everywhere (avoid SQL injection).
"""

import sqlite3
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "manufacturing.db"

# --------------------------------------------------------------------------- #
# Connection helper
# --------------------------------------------------------------------------- #

def get_conn() -> sqlite3.Connection:
    """Return a SQLite connection with rows as dict-like objects."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# --------------------------------------------------------------------------- #
# Task 3: Required functions
# --------------------------------------------------------------------------- #

def get_product_summary(product_name: str, start_date: str, end_date: str):
    """
    Return a summary for a product within a date range:
      { product_id, product_name, good_qty, scrap_qty, num_orders }

    Notes:
      - Counts operations whose op_start/op_end fall fully inside the range.
      - num_orders = distinct work_orders that have operations in range.
    """
    with get_conn() as conn:
        product = conn.execute(
            "SELECT id, name FROM products WHERE name = ?;",
            (product_name,)
        ).fetchone()
        if not product:
            raise ValueError(f"Product '{product_name}' not found")

        product_id = product["id"]

        totals = conn.execute("""
            SELECT
              COALESCE(SUM(o.good_qty), 0)  AS good_qty,
              COALESCE(SUM(o.scrap_qty), 0) AS scrap_qty
            FROM operations o
            JOIN work_orders w ON w.id = o.work_order_id
            WHERE w.product_id = ?
              AND o.op_start >= ?
              AND o.op_end   <= ?;
        """, (product_id, start_date, end_date)).fetchone()

        num_orders = conn.execute("""
            SELECT COUNT(DISTINCT w.id) AS cnt
            FROM work_orders w
            JOIN operations o ON o.work_order_id = w.id
            WHERE w.product_id = ?
              AND o.op_start >= ?
              AND o.op_end   <= ?;
        """, (product_id, start_date, end_date)).fetchone()["cnt"]

        return {
            "product_id": product_id,
            "product_name": product["name"],
            "good_qty": int(totals["good_qty"] or 0),
            "scrap_qty": int(totals["scrap_qty"] or 0),
            "num_orders": int(num_orders or 0),
        }

def get_wip_orders(now_iso: str):
    """
    Return all Work-In-Progress orders at a given timestamp.

    Definition:
      status='in_progress'
      OR (now BETWEEN planned_start AND planned_end AND status NOT IN ('completed','cancelled'))
    """
    with get_conn() as conn:
        rows = conn.execute("""
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
        """, (now_iso, now_iso)).fetchall()
        return [dict(r) for r in rows]

def get_machine_utilization(start_date: str, end_date: str, adjusted: bool = True):
    """
    Compute machine utilization for a date range:
      utilization = runtime_hours / available_hours

    Where:
      - runtime_hours = sum(op_end - op_start) across operations for the machine
                        (only operations fully inside the range)
      - available_hours:
            Simple  : total_hours_in_range
            Adjusted: total_hours_in_range - downtime_hours (from downtime_events)

    Returns:
      List of dicts per machine:
        { machine_id, machine_name, runtime_hours, available_hours, downtime_hours, utilization }
    """
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    start_dt = datetime.strptime(start_date, fmt)
    end_dt = datetime.strptime(end_date, fmt)
    total_hours = max(0.0, (end_dt - start_dt).total_seconds() / 3600.0)

    with get_conn() as conn:
        machines = conn.execute("SELECT id, name FROM machines;").fetchall()
        results = []

        for m in machines:
            mid = m["id"]
            name = m["name"]

            # Sum runtime from operations inside the window
            ops = conn.execute("""
                SELECT op_start, op_end
                FROM operations
                WHERE machine_id = ?
                  AND op_start >= ?
                  AND op_end   <= ?;
            """, (mid, start_date, end_date)).fetchall()

            runtime_seconds = 0.0
            for op in ops:
                s = datetime.strptime(op["op_start"], fmt)
                e = datetime.strptime(op["op_end"], fmt)
                runtime_seconds += max(0.0, (e - s).total_seconds())
            runtime_hours = runtime_seconds / 3600.0

            # Compute available hours
            downtime_hours = 0.0
            available_hours = total_hours
            if adjusted:
                dts = conn.execute("""
                    SELECT dt_start, dt_end
                    FROM downtime_events
                    WHERE machine_id = ?
                      AND dt_start >= ?
                      AND dt_end   <= ?;
                """, (mid, start_date, end_date)).fetchall()
                for dt in dts:
                    ds = datetime.strptime(dt["dt_start"], fmt)
                    de = datetime.strptime(dt["dt_end"], fmt)
                    downtime_hours += max(0.0, (de - ds).total_seconds()) / 3600.0
                available_hours = max(0.0, total_hours - downtime_hours)

            utilization = 0.0
            if available_hours > 0:
                utilization = runtime_hours / available_hours

            results.append({
                "machine_id": mid,
                "machine_name": name,
                "runtime_hours": round(runtime_hours, 2),
                "available_hours": round(available_hours, 2),
                "downtime_hours": round(downtime_hours, 2),
                "utilization": round(utilization, 4),
            })

        return results

def create_work_order(product_id: int, planned_qty: int, planned_start: str, planned_end: str, machine_id: int | None = None):
    """
    Create a new work order with status='planned' and return its ID.

    Validations:
      - planned_qty must be > 0
      - planned_start < planned_end
      - product_id exists
      - machine_id exists (if provided)

    Default:
      - plant_id = 1 (single-plant seed; adjust as needed)
    """
    if planned_qty <= 0:
        raise ValueError("planned_qty must be > 0")
    if planned_start >= planned_end:
        raise ValueError("planned_start must be < planned_end")

    with get_conn() as conn:
        p = conn.execute("SELECT id FROM products WHERE id = ?;", (product_id,)).fetchone()
        if not p:
            raise ValueError(f"product_id {product_id} not found")

        if machine_id is not None:
            m = conn.execute("SELECT id FROM machines WHERE id = ?;", (machine_id,)).fetchone()
            if not m:
                raise ValueError(f"machine_id {machine_id} not found")

        cur = conn.execute("""
            INSERT INTO work_orders (product_id, plant_id, planned_qty, status, planned_start, planned_end, machine_id)
            VALUES (?, 1, ?, 'planned', ?, ?, ?);
        """, (product_id, planned_qty, planned_start, planned_end, machine_id))
        conn.commit()
        return cur.lastrowid

# --------------------------------------------------------------------------- #
# Optional helper (nice-to-have)
# --------------------------------------------------------------------------- #

def add_production_record(work_order_id: int, machine_id: int,
                          op_start: str, op_end: str,
                          good_qty: int, scrap_qty: int,
                          defect_code: str | None = None):
    """
    Insert a production operation row for a work order.

    Validations:
      - work_order_id exists
      - machine_id exists
    """
    with get_conn() as conn:
        wo = conn.execute("SELECT id FROM work_orders WHERE id = ?;", (work_order_id,)).fetchone()
        if not wo:
            raise ValueError(f"work_order_id {work_order_id} not found")
        m = conn.execute("SELECT id FROM machines WHERE id = ?;", (machine_id,)).fetchone()
        if not m:
            raise ValueError(f"machine_id {machine_id} not found")

        conn.execute("""
            INSERT INTO operations (work_order_id, machine_id, op_start, op_end, good_qty, scrap_qty, defect_code)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (work_order_id, machine_id, op_start, op_end, good_qty, scrap_qty, defect_code))
        conn.commit()
