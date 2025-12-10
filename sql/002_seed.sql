
-- sql/002_seed.sql

BEGIN TRANSACTION;

-- Plant
INSERT INTO plants (id, name) VALUES
  (1, 'Main Plant')
ON CONFLICT DO NOTHING;

-- Products
INSERT INTO products (id, sku, name, uom) VALUES
  (1, 'WID-A', 'Widget A', 'ea'),
  (2, 'WID-B', 'Widget B', 'ea'),
  (3, 'WID-C', 'Widget C', 'ea')
ON CONFLICT DO NOTHING;

-- Machines
INSERT INTO machines (id, plant_id, name, type, capacity_per_hour) VALUES
  (1, 1, 'Milling-01', 'Milling', 120),
  (2, 1, 'Milling-02', 'Milling', 100),
  (3, 1, 'Assembly-01', 'Assembly', 80),
  (4, 1, 'Assembly-02', 'Assembly', 90),
  (5, 1, 'Packaging-01', 'Packaging', 150)
ON CONFLICT DO NOTHING;

-- Work Orders (Nov–Dec 2025)
INSERT INTO work_orders (id, product_id, plant_id, planned_qty, status, planned_start, planned_end, machine_id, created_at) VALUES
  (101, 1, 1, 500, 'planned',     '2025-12-10T08:00:00Z', '2025-12-12T18:00:00Z', 1, '2025-12-01T09:00:00Z'),
  (102, 1, 1, 400, 'released',    '2025-12-07T08:00:00Z', '2025-12-09T18:00:00Z', 2, '2025-12-01T09:10:00Z'),
  (103, 1, 1, 300, 'in_progress', '2025-12-08T08:00:00Z', '2025-12-10T18:00:00Z', 1, '2025-12-02T10:00:00Z'),
  (104, 2, 1, 450, 'completed',   '2025-11-28T08:00:00Z', '2025-11-30T18:00:00Z', 3, '2025-11-25T09:00:00Z'),
  (105, 2, 1, 350, 'completed',   '2025-12-02T08:00:00Z', '2025-12-03T18:00:00Z', 4, '2025-11-29T10:00:00Z'),
  (106, 2, 1, 600, 'released',    '2025-12-11T08:00:00Z', '2025-12-13T18:00:00Z', 3, '2025-12-03T11:00:00Z'),
  (107, 3, 1, 200, 'cancelled',   '2025-12-05T08:00:00Z', '2025-12-06T18:00:00Z', 5, '2025-12-01T12:00:00Z'),
  (108, 3, 1, 250, 'released',    '2025-12-06T08:00:00Z', '2025-12-08T18:00:00Z', NULL, '2025-12-02T12:30:00Z'),
  (109, 3, 1, 500, 'delayed',     '2025-12-09T08:00:00Z', '2025-12-11T18:00:00Z', 5, '2025-12-03T14:00:00Z'),
  (110, 1, 1, 200, 'completed',   '2025-11-20T08:00:00Z', '2025-11-21T18:00:00Z', 2, '2025-11-18T09:00:00Z'),
  (111, 2, 1, 300, 'in_progress', '2025-12-09T08:00:00Z', '2025-12-11T18:00:00Z', 4, '2025-12-04T15:00:00Z'),
  (112, 1, 1, 150, 'released',    '2025-12-09T12:00:00Z', '2025-12-09T20:00:00Z', 2, '2025-12-07T09:00:00Z')
ON CONFLICT DO NOTHING;

-- Operations (mix of good vs scrap)
INSERT INTO operations (work_order_id, machine_id, op_start, op_end, good_qty, scrap_qty, defect_code) VALUES
  (104, 3, '2025-11-28T08:00:00Z', '2025-11-28T12:00:00Z', 180, 10, 'DEF-A'),
  (104, 3, '2025-11-29T09:00:00Z', '2025-11-29T17:00:00Z', 240, 20, 'DEF-B'),
  (105, 4, '2025-12-02T08:00:00Z', '2025-12-02T15:00:00Z', 260, 15, 'DEF-A'),
  (105, 4, '2025-12-03T09:00:00Z', '2025-12-03T12:00:00Z', 70, 5, NULL),
  (110, 2, '2025-11-20T08:00:00Z', '2025-11-20T10:00:00Z', 180, 10, 'DEF-C'),
  (103, 1, '2025-12-08T09:00:00Z', '2025-12-08T13:00:00Z', 120, 10, NULL),
  (103, 1, '2025-12-09T09:00:00Z', '2025-12-09T11:00:00Z', 80, 8, 'DEF-B'),
  (111, 4, '2025-12-09T08:30:00Z', '2025-12-09T12:00:00Z', 140, 12, 'DEF-A'),
  (102, 2, '2025-12-07T08:30:00Z', '2025-12-07T12:30:00Z', 160, 6, NULL),
  (112, 2, '2025-12-09T12:30:00Z', '2025-12-09T17:30:00Z', 120, 10, 'DEF-C');

-- Downtime (optional)
INSERT INTO downtime_events (machine_id, dt_start, dt_end, reason, category) VALUES
  (1, '2025-12-08T14:00:00Z', '2025-12-08T16:00:00Z', 'Tool change', 'planned'),
  (2, '2025-12-07T13:00:00Z', '2025-12-07T14:30:00Z', 'Sensor fault', 'unplanned'),
  (4, '2025-12-09T13:00:00Z', '2025-12-09T14:00:00Z', 'Maintenance', 'planned');

COMMIT;
