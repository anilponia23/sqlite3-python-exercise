
-- sql/001_schema.sql

PRAGMA foreign_keys = ON;

-- Plants (future-proofing, single plant seeded)
CREATE TABLE IF NOT EXISTS plants (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

-- Products manufactured
CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY,
  sku TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  uom TEXT NOT NULL DEFAULT 'ea' -- unit of measure
);

-- Machines (assigned to a plant)
CREATE TABLE IF NOT EXISTS machines (
  id INTEGER PRIMARY KEY,
  plant_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  type TEXT,
  capacity_per_hour REAL, -- optional metadata
  FOREIGN KEY (plant_id) REFERENCES plants(id)
);

-- Work orders (planned/scheduled/released/etc.)
CREATE TABLE IF NOT EXISTS work_orders (
  id INTEGER PRIMARY KEY,
  product_id INTEGER NOT NULL,
  plant_id INTEGER NOT NULL,
  planned_qty INTEGER NOT NULL,
  status TEXT NOT NULL CHECK (
    status IN ('planned','released','in_progress','completed','cancelled','delayed')
  ),
  planned_start TEXT NOT NULL, -- ISO 8601 timestamp
  planned_end   TEXT NOT NULL, -- ISO 8601 timestamp
  machine_id INTEGER,          -- optional planned machine
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (product_id) REFERENCES products(id),
  FOREIGN KEY (plant_id) REFERENCES plants(id),
  FOREIGN KEY (machine_id) REFERENCES machines(id)
);

-- Operations (actual execution records)
CREATE TABLE IF NOT EXISTS operations (
  id INTEGER PRIMARY KEY,
  work_order_id INTEGER NOT NULL,
  machine_id INTEGER NOT NULL,
  op_start TEXT NOT NULL, -- ISO 8601
  op_end   TEXT NOT NULL,
  good_qty INTEGER NOT NULL DEFAULT 0,
  scrap_qty INTEGER NOT NULL DEFAULT 0,
  defect_code TEXT, -- optional simple classification
  FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
  FOREIGN KEY (machine_id) REFERENCES machines(id)
);

-- Optional: Downtime events per machine
CREATE TABLE IF NOT EXISTS downtime_events (
  id INTEGER PRIMARY KEY,
  machine_id INTEGER NOT NULL,
  dt_start TEXT NOT NULL,
  dt_end   TEXT NOT NULL,
  reason   TEXT,
  category TEXT, -- e.g., planned, unplanned
  FOREIGN KEY (machine_id) REFERENCES machines(id)
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_machines_plant ON machines(plant_id);
CREATE INDEX IF NOT EXISTS idx_wo_product ON work_orders(product_id);
CREATE INDEX IF NOT EXISTS idx_wo_status ON work_orders(status);
CREATE INDEX IF NOT EXISTS idx_ops_wo ON operations(work_order_id);
CREATE INDEX IF NOT EXISTS idx_ops_machine ON operations(machine_id);
CREATE INDEX IF NOT EXISTS idx_ops_time ON operations(op_start, op_end);
CREATE INDEX IF NOT EXISTS idx_dt_machine ON downtime_events(machine_id);
CREATE INDEX IF NOT EXISTS idx_dt_time ON downtime_events(dt_start, dt_end);
