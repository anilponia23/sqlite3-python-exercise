
/* =============================================================================
   Manufacturing Data Platform – Task 2 Queries (SQLite)
   -----------------------------------------------------------------------------
   Purpose:
     Answer common business questions using SQL against our normalized schema.

   Conventions:
     • Parameters are bound from Python using '?' placeholders.
     • Timestamps are ISO 8601 UTC strings: 'YYYY-MM-DDTHH:MM:SSZ'.
     • Where we need ranges, we filter on op_start/op_end (fully contained).
     • For "month" queries, we match op_start LIKE 'YYYY-MM%'.

   This file includes:
     1) Product output by month (good, scrap, number of work orders)
     2) Current work-in-progress (WIP) based on status/time window
     3) Machine utilization (simple SQL metric: runtime/calendar hours)
     4) Work orders with no production yet
     5) Top defect/scrap drivers (by product and by machine) with scrap rate
   ========================================================================== */

-- ============================================================================
-- 1) Product output by month
--    For a given month, show per product:
--      • Total good quantity
--      • Total scrap quantity
--      • Number of distinct work orders involved
--    NOTE: bind parameter: month_prefix LIKE 'YYYY-MM%'
-- ============================================================================
-- Example shape (bind with one '?', e.g. '2025-12%'):
-- SELECT p.name AS product_name,
--        COALESCE(SUM(o.good_qty), 0)  AS good_qty,
--        COALESCE(SUM(o.scrap_qty), 0) AS scrap_qty,
--        COUNT(DISTINCT o.work_order_id) AS num_orders
-- FROM products p
-- LEFT JOIN work_orders w ON w.product_id = p.id
-- LEFT JOIN operations  o ON o.work_order_id = w.id
-- WHERE o.op_start LIKE ?
-- GROUP BY p.name
-- ORDER BY p.name;

-- ============================================================================
-- 2) Current work-in-progress (WIP)
--    Definition:
--      • status = 'in_progress'
--        OR
--      • now BETWEEN planned_start AND planned_end
--        AND status NOT IN ('completed','cancelled')
--    NOTE: bind parameter twice (now_iso, now_iso)
-- ============================================================================
-- SELECT w.id,
--        p.name AS product,
--        w.planned_qty,
--        w.status,
--        w.planned_start,
--        w.planned_end,
--        w.machine_id
-- FROM work_orders w
-- JOIN products p ON p.id = w.product_id
-- WHERE w.status = 'in_progress'
--    OR ( ? >= w.planned_start AND ? <= w.planned_end
--         AND w.status NOT IN ('completed','cancelled') )
-- ORDER BY w.planned_start;

-- ============================================================================
-- 3) Machine utilization (SQL-only simple metric)
--    For a given [start, end] date range:
--      • runtime_hours = SUM(op_end - op_start) / 3600 over operations
--      • utilization   = runtime_hours / total_hours_in_range (computed in app)
--    NOTE: bind parameters (start_iso, end_iso). Denominator handled in Python.
-- ============================================================================
-- SELECT
--   m.id   AS machine_id,
--   m.name AS machine_name,
--   COALESCE(
--     SUM( (strftime('%s', o.op_end) - strftime('%s', o.op_start)) / 3600.0 ),
--     0.0
--   ) AS runtime_hours
-- FROM machines m
-- LEFT JOIN operations o
--   ON o.machine_id = m.id
--  AND o.op_start >= ?
--  AND o.op_end   <= ?
-- GROUP BY m.id, m.name
-- ORDER BY m.id;

-- ============================================================================
-- 4) Work orders with no production yet
--    List all WOs that are released/scheduled/in_progress/delayed
--    but have no operations.
-- ============================================================================
-- SELECT w.id,
--        p.name AS product,
--        w.status,
--        w.planned_start,
--        w.planned_end,
--        w.planned_qty
-- FROM work_orders w
-- JOIN products p ON p.id = w.product_id
-- LEFT JOIN operations o ON o.work_order_id = w.id
-- WHERE w.status IN ('released','planned','delayed','in_progress')
--   AND o.id IS NULL
-- ORDER BY w.planned_start;

-- ============================================================================
-- 5) Top defect / scrap drivers
--    For a given date range, identify top scrap contributors and rates.
--    A) By product
--    B) By machine
--    NOTE: bind parameters (start_iso, end_iso)
-- ============================================================================
-- A) by product
-- SELECT p.name AS product_name,
--        COALESCE(SUM(o.scrap_qty), 0) AS scrap_qty,
--        COALESCE(SUM(o.good_qty + o.scrap_qty), 0) AS total_qty,
--        CASE
--          WHEN COALESCE(SUM(o.good_qty + o.scrap_qty), 0) = 0 THEN 0.0
--          ELSE CAST(SUM(o.scrap_qty) AS REAL) / SUM(o.good_qty + o.scrap_qty)
--        END AS scrap_rate
-- FROM products p
-- JOIN work_orders w ON w.product_id = p.id
-- JOIN operations  o ON o.work_order_id = w.id
-- WHERE o.op_start >= ?
--   AND o.op_end   <= ?
-- GROUP BY p.name
-- ORDER BY scrap_qty DESC, scrap_rate DESC;

-- B) by machine
-- SELECT m.name AS machine_name,
--        COALESCE(SUM(o.scrap_qty), 0) AS scrap_qty,
--        COALESCE(SUM(o.good_qty + o.scrap_qty), 0) AS total_qty,
--        CASE
--          WHEN COALESCE(SUM(o.good_qty + o.scrap_qty), 0) = 0 THEN 0.0
--          ELSE CAST(SUM(o.scrap_qty) AS REAL) / SUM(o.good_qty + o.scrap_qty)
--        END AS scrap_rate
-- FROM machines m
-- JOIN operations o ON o.machine_id = m.id
-- WHERE o.op_start >= ?
--   AND o.op_end   <= ?
-- GROUP BY m.name
-- ORDER BY scrap_qty DESC, scrap_rate DESC;
