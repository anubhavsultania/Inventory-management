# database.py
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(BASE_DIR, 'inventory.db')

def get_db_connection():
    """Establishes a connection to the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # Return rows as dictionary-like objects
    return conn

def init_db():
    """Initializes the database using schema.sql if it doesn't exist."""
    if not os.path.exists(DATABASE_FILE):
        print("Database not found. Initializing...")
        conn = get_db_connection()
        try:
            with open('schema.sql') as f:
                conn.executescript(f.read())
            conn.commit()
            print("Database initialized successfully.")
        except Exception as e:
            print(f"Error initializing database: {e}")
            # Clean up potentially partially created file
            conn.close()
            os.remove(DATABASE_FILE)
        finally:
            conn.close()
    else:
         print("Database already exists.")

def execute_query(query, args=(), fetchone=False, commit=False):
    """Executes a generic SQL query."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, args)
        if commit:
            conn.commit()
            return cursor.lastrowid # Return ID for inserts
        if fetchone:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
        return result
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback() # Rollback changes on error
        return None
    finally:
        conn.close()

# --- Item Functions ---

def add_item(sku, name, category, quantity, reorder_level, cost_price, selling_price):
    query = """
        INSERT INTO items (sku, name, category, quantity, reorder_level, cost_price, selling_price, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """
    args = (sku, name, category, quantity, reorder_level, cost_price, selling_price)
    return execute_query(query, args, commit=True)

def get_all_items(search_term=None):
    query = "SELECT * FROM items"
    args = ()
    if search_term:
        query += " WHERE name LIKE ? OR sku LIKE ?"
        args = (f'%{search_term}%', f'%{search_term}%')
    query += " ORDER BY name ASC"
    return execute_query(query, args)

def get_item_by_id(item_id):
    query = "SELECT * FROM items WHERE id = ?"
    return execute_query(query, (item_id,), fetchone=True)

def get_item_by_sku(sku):
    query = "SELECT * FROM items WHERE sku = ?"
    return execute_query(query, (sku,), fetchone=True)

def update_item(item_id, sku, name, category, reorder_level, cost_price, selling_price):
    # Note: We don't update quantity directly here, use adjust_stock for that.
    query = """
        UPDATE items
        SET sku = ?, name = ?, category = ?, reorder_level = ?, cost_price = ?, selling_price = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """
    args = (sku, name, category, reorder_level, cost_price, selling_price, item_id)
    execute_query(query, args, commit=True)

def delete_item(item_id):
    # Ensure stock movements related to this item are handled (ON DELETE CASCADE helps)
    query = "DELETE FROM items WHERE id = ?"
    execute_query(query, (item_id,), commit=True)

# --- Stock Functions ---

def adjust_stock(item_id, quantity_change, adjustment_type, reason=""):
    """Adjusts stock quantity and logs the movement."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Get current item details
        cursor.execute("SELECT sku, name, quantity FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        if not item:
            raise ValueError("Item not found")

        sku, name, current_quantity = item['sku'], item['name'], item['quantity']

        # 2. Calculate new quantity
        if adjustment_type.upper() == 'IN':
            new_quantity = current_quantity + quantity_change
        elif adjustment_type.upper() == 'OUT':
            new_quantity = current_quantity - quantity_change
            if new_quantity < 0:
                 # Optional: Prevent going below zero, depends on requirements
                 # raise ValueError("Stock quantity cannot go below zero")
                 print(f"Warning: Stock for item {sku} is now negative ({new_quantity})")
                 pass # Allow negative stock for now
        else:
            raise ValueError("Invalid adjustment type")

        # 3. Update item quantity
        cursor.execute(
            "UPDATE items SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_quantity, item_id)
        )

        # 4. Log the movement
        cursor.execute("""
            INSERT INTO stock_movements (item_id, sku, item_name, adjustment_type, quantity_change, reason)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (item_id, sku, name, adjustment_type.upper(), quantity_change, reason))

        conn.commit()
        return True

    except (sqlite3.Error, ValueError) as e:
        print(f"Stock adjustment error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# --- Reporting / Dashboard Functions ---

def get_low_stock_items():
    query = "SELECT id, sku, name, quantity, reorder_level FROM items WHERE quantity <= reorder_level AND quantity > 0 ORDER BY quantity ASC"
    return execute_query(query)

def get_out_of_stock_items():
     query = "SELECT id, sku, name, quantity, reorder_level FROM items WHERE quantity <= 0 ORDER BY name ASC"
     return execute_query(query)


def get_dashboard_stats():
    stats = {}
    query_total_items = "SELECT COUNT(id) as count FROM items"
    query_total_qty = "SELECT SUM(quantity) as total_qty FROM items"

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query_total_items)
        stats['total_items'] = cursor.fetchone()['count']

        cursor.execute(query_total_qty)
        total_qty = cursor.fetchone()['total_qty']
        stats['total_quantity'] = total_qty if total_qty is not None else 0

    except sqlite3.Error as e:
        print(f"Error fetching dashboard stats: {e}")
        stats = {'total_items': 'Error', 'total_quantity': 'Error'}
    finally:
        conn.close()
    return stats

def get_stock_movements(limit=50):
    query = """
        SELECT sm.timestamp, sm.item_name, sm.sku, sm.adjustment_type, sm.quantity_change, sm.reason
        FROM stock_movements sm
        ORDER BY sm.timestamp DESC
        LIMIT ?
    """
    return execute_query(query, (limit,))