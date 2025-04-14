-- schema.sql
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS stock_movements;

CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category TEXT,
    quantity INTEGER NOT NULL DEFAULT 0,
    reorder_level INTEGER NOT NULL DEFAULT 0,
    cost_price REAL,
    selling_price REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Note: Requires trigger or app logic to update on change
);

CREATE TABLE stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    sku TEXT NOT NULL,
    item_name TEXT NOT NULL,
    adjustment_type TEXT NOT NULL, -- 'IN' or 'OUT'
    quantity_change INTEGER NOT NULL,
    reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE -- Cascade delete if item is removed
);

-- Optional: Trigger to update the 'updated_at' timestamp on items table changes
-- SQLite syntax for triggers can vary, doing this in app logic might be simpler for this project.
-- CREATE TRIGGER update_item_timestamp AFTER UPDATE ON items
-- BEGIN
--     UPDATE items SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
-- END;