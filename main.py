# main.py
from flask import Flask, render_template, request, redirect, url_for, flash
import database as db
import os

app = Flask(__name__)
# Secret key is needed for flashing messages
app.secret_key = os.urandom(24) # Replace with a fixed secret key in production/persistent env

@app.before_request
def initialize_database():
    """Initialize the database before the first request."""
    # This ensures the DB is set up when the app starts
    # In a production scenario, you might run init_db() separately
    # Check if the DB file exists, initialize if not.
    if not os.path.exists(db.DATABASE_FILE):
         db.init_db()


@app.route('/')
def index():
    """Dashboard route."""
    stats = db.get_dashboard_stats()
    low_stock = db.get_low_stock_items()
    out_of_stock = db.get_out_of_stock_items()
    return render_template('index.html', stats=stats, low_stock=low_stock, out_of_stock=out_of_stock)

@app.route('/items')
def items_list():
    """Items list route."""
    search = request.args.get('search')
    items = db.get_all_items(search_term=search)
    return render_template('items_list.html', items=items, search_term=search or "")

@app.route('/items/add', methods=['GET', 'POST'])
def add_item():
    """Add new item route."""
    if request.method == 'POST':
        # Basic validation (can be improved)
        sku = request.form.get('sku')
        name = request.form.get('name')
        quantity = request.form.get('quantity', type=int, default=0)
        reorder_level = request.form.get('reorder_level', type=int, default=0)
        cost_price = request.form.get('cost_price', type=float)
        selling_price = request.form.get('selling_price', type=float)
        category = request.form.get('category')

        if not sku or not name:
            flash('SKU and Name are required.', 'error')
            return render_template('item_form.html', form_action='add', item={}) # Pass empty item dict

        # Check if SKU already exists
        existing_item = db.get_item_by_sku(sku)
        if existing_item:
            flash(f'SKU "{sku}" already exists. Please use a unique SKU.', 'error')
            # Pass submitted data back to the form
            item_data = request.form.to_dict()
            return render_template('item_form.html', form_action='add', item=item_data)

        item_id = db.add_item(sku, name, category, quantity, reorder_level, cost_price, selling_price)

        if item_id:
             # Log initial stock if quantity > 0
             if quantity > 0:
                 db.adjust_stock(item_id, quantity, 'IN', 'Initial Stock')
             flash(f'Item "{name}" added successfully!', 'success')
             return redirect(url_for('items_list'))
        else:
             flash('Error adding item.', 'error')

    # For GET request
    return render_template('item_form.html', form_action='add', item={}) # Pass empty dict for add form

@app.route('/items/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    """Edit item route."""
    item = db.get_item_by_id(item_id)
    if not item:
        flash('Item not found.', 'error')
        return redirect(url_for('items_list'))

    if request.method == 'POST':
        sku = request.form.get('sku')
        name = request.form.get('name')
        reorder_level = request.form.get('reorder_level', type=int, default=0)
        cost_price = request.form.get('cost_price', type=float)
        selling_price = request.form.get('selling_price', type=float)
        category = request.form.get('category')

        if not sku or not name:
            flash('SKU and Name are required.', 'error')
            # Pass existing item data back to the form for correction
            return render_template('item_form.html', item=item, form_action='edit')

        # Check if SKU is being changed to one that already exists (excluding itself)
        existing_item = db.get_item_by_sku(sku)
        if existing_item and existing_item['id'] != item_id:
             flash(f'SKU "{sku}" already exists for another item. Please use a unique SKU.', 'error')
             # Pass submitted data back, merging with original item id
             submitted_data = request.form.to_dict()
             submitted_data['id'] = item_id
             return render_template('item_form.html', item=submitted_data, form_action='edit')

        db.update_item(item_id, sku, name, category, reorder_level, cost_price, selling_price)
        flash(f'Item "{name}" updated successfully!', 'success')
        return redirect(url_for('items_list'))

    # For GET request
    return render_template('item_form.html', item=item, form_action='edit')

@app.route('/items/delete/<int:item_id>', methods=['POST']) # Use POST for deletion
def delete_item(item_id):
    """Delete item route."""
    item = db.get_item_by_id(item_id)
    if item:
        db.delete_item(item_id)
        flash(f'Item "{item["name"]}" deleted successfully!', 'success')
    else:
        flash('Item not found or already deleted.', 'error')
    return redirect(url_for('items_list'))


@app.route('/stock/adjust', methods=['GET', 'POST'])
def adjust_stock_route():
    """Adjust stock route."""
    if request.method == 'POST':
        item_id = request.form.get('item_id', type=int)
        adjustment_type = request.form.get('adjustment_type')
        quantity_change = request.form.get('quantity_change', type=int)
        reason = request.form.get('reason')

        if not item_id or not adjustment_type or quantity_change is None or quantity_change <= 0:
            flash('Invalid input. Please select an item, type, and positive quantity.', 'error')
            items = db.get_all_items() # Need items for the dropdown again
            return render_template('adjust_stock.html', items=items)

        success = db.adjust_stock(item_id, quantity_change, adjustment_type, reason)

        if success:
            flash('Stock adjusted successfully!', 'success')
            return redirect(url_for('items_list')) # Redirect to item list or stock log
        else:
            flash('Error adjusting stock. Check quantity or item.', 'error')

    # For GET request
    items = db.get_all_items()
    return render_template('adjust_stock.html', items=items)

@app.route('/stock/log')
def stock_log():
    """Stock movement log route."""
    movements = db.get_stock_movements()
    return render_template('stock_log.html', movements=movements)


@app.route('/about')
def about_developer():
    """About developer page route."""
    return render_template('about_developer.html')
# if __name__ == '__main__':
#     # Check if running in Replit environment and set host/port accordingly
#     # host = '0.0.0.0' if 'REPL_ID' in os.environ else '127.0.0.1'
#     # port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=8080, debug=True) # debug=True is helpful during development
if __name__ == '__main__':
    db.init_db()  # Ensures DB is created before the app starts
    app.run(host='0.0.0.0', port=8080, debug=True)
