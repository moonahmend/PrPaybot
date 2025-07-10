import sqlite3
import os
from flask import Flask, render_template_string, request, redirect, url_for, session, flash, Blueprint
import requests

# Create Blueprint instead of Flask app
app = Blueprint('admin', __name__)

# Always use absolute path for users.db
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'users.db'))

def ensure_tables():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        telegram_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        balance INTEGER DEFAULT 0,
        welcomed INTEGER DEFAULT 0,
        subscription_active INTEGER DEFAULT 0
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        order_type TEXT,
        details TEXT,
        amount INTEGER,
        created_at TEXT,
        status TEXT DEFAULT 'completed'
    )
    ''')
    conn.commit()
    conn.close()

ensure_tables()

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'  # Change this for production!

# HTML templates (inline for simplicity)
NAVBAR = '''
<nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
  <div class="container-fluid">
    <a class="navbar-brand" href="{{ url_for('admin.dashboard') }}">PrBot_Pay Admin</a>
    <ul class="navbar-nav me-auto mb-2 mb-lg-0">
      <li class="nav-item"><a class="nav-link {% if active=='dashboard' %}active{% endif %}" href="{{ url_for('admin.dashboard') }}">Dashboard</a></li>
      <li class="nav-item"><a class="nav-link {% if active=='users' %}active{% endif %}" href="{{ url_for('admin.users') }}">Users</a></li>
    </ul>
    <div class="d-flex">
      <a href="{{ url_for('admin.logout') }}" class="btn btn-outline-light">Logout</a>
    </div>
  </div>
</nav>
'''

LOGIN_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PrBot_Pay Admin Login</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-4">
        <div class="card shadow">
          <div class="card-body">
            <h3 class="card-title text-center mb-4">PrBot_Pay Admin Login</h3>
            <form method="post">
              <div class="mb-3">
                <input type="text" class="form-control" name="username" placeholder="Username" required>
              </div>
              <div class="mb-3">
                <input type="password" class="form-control" name="password" placeholder="Password" required>
              </div>
              <button type="submit" class="btn btn-primary w-100">Login</button>
            </form>
            {% if error %}<div class="alert alert-danger mt-3">{{ error }}</div>{% endif %}
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PrBot_Pay Admin Dashboard</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    .badge-cancelled { background-color: #dc3545; }
    .badge-completed { background-color: #198754; }
    .badge-other { background-color: #6c757d; }
    .dashboard-card { min-width: 180px; }
  </style>
</head>
<body>
{{ navbar|safe }}
<div class="container">
  <h2 class="mb-4">Dashboard</h2>
  <div class="row mb-4">
    <div class="col dashboard-card">
      <div class="card text-bg-primary mb-3">
        <div class="card-body">
          <h5 class="card-title">Total Orders</h5>
          <p class="card-text fs-4">{{ stats.total }}</p>
        </div>
      </div>
    </div>
    <div class="col dashboard-card">
      <div class="card text-bg-success mb-3">
        <div class="card-body">
          <h5 class="card-title">Completed</h5>
          <p class="card-text fs-4">{{ stats.completed }}</p>
        </div>
      </div>
    </div>
    <div class="col dashboard-card">
      <div class="card text-bg-danger mb-3">
        <div class="card-body">
          <h5 class="card-title">Cancelled</h5>
          <p class="card-text fs-4">{{ stats.cancelled }}</p>
        </div>
      </div>
    </div>
    <div class="col dashboard-card">
      <div class="card text-bg-warning mb-3">
        <div class="card-body">
          <h5 class="card-title">Tokens Refunded</h5>
          <p class="card-text fs-4">{{ stats.refunded }}</p>
        </div>
      </div>
    </div>
  </div>
  {% with messages = get_flashed_messages() %}
    {% if messages %}
      {% for msg in messages %}
        <div class="alert alert-info">{{ msg }}</div>
      {% endfor %}
    {% endif %}
  {% endwith %}
  <div class="table-responsive">
    <table class="table table-bordered table-hover align-middle">
      <thead class="table-light">
        <tr>
          <th>ID</th>
          <th>User ID</th>
          <th>Username</th>
          <th>Full Name</th>
          <th>Order Type</th>
          <th>Details</th>
          <th>Amount</th>
          <th>Status</th>
          <th>Created At</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
      {% for order in orders %}
        <tr>
          <td>{{ order['id'] }}</td>
          <td><a href="{{ url_for('admin.user_detail', telegram_id=order['telegram_id']) }}">{{ order['telegram_id'] }}</a></td>
          <td>{{ order['username'] or '' }}</td>
          <td>{{ order['full_name'] or '' }}</td>
          <td>{{ order['order_type'] }}</td>
          <td>{{ order['details'] }}</td>
          <td>{{ order['amount'] }}</td>
          <td>
            {% if order['status'] == 'cancelled' %}
              <span class="badge badge-cancelled">Cancelled</span>
            {% elif order['status'] == 'completed' %}
              <span class="badge badge-completed">Completed</span>
            {% else %}
              <span class="badge badge-other">{{ order['status'] }}</span>
            {% endif %}
          </td>
          <td>{{ order['created_at'] }}</td>
          <td>
            {% if order['status'] != 'cancelled' %}
              <form method="post" action="{{ url_for('admin.cancel_order', order_id=order['id']) }}" style="display:inline">
                <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Cancel this payment?')">Cancel</button>
              </form>
            {% else %}—{% endif %}
          </td>
        </tr>
      {% endfor %}
      </tbody>
    </table>
  </div>
</div>
<footer class="footer mt-5 py-3 bg-light border-top">
  <div class="container text-center">
    <span class="text-muted">&copy; 2024 PrBot_Pay Admin Panel</span>
  </div>
</footer>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

USERS_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PrBot_Pay Admin - Users</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
{{ navbar|safe }}
<div class="container">
  <h2 class="mb-4">All Users</h2>
  <div class="table-responsive">
    <table class="table table-bordered table-hover align-middle">
      <thead class="table-light">
        <tr>
          <th>Telegram ID</th>
          <th>Username</th>
          <th>Full Name</th>
          <th>Balance</th>
          <th>Subscription</th>
          <th>Welcomed</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
      {% for user in users %}
        <tr>
          <td><a href="{{ url_for('admin.user_detail', telegram_id=user['telegram_id']) }}">{{ user['telegram_id'] }}</a></td>
          <td>{{ user['username'] or '' }}</td>
          <td>{{ user['full_name'] or '' }}</td>
          <td>{{ user['balance'] }}</td>
          <td>{% if user['subscription_active'] %}<span class="badge bg-success">Active</span>{% else %}<span class="badge bg-secondary">Inactive</span>{% endif %}</td>
          <td>{{ user['welcomed'] }}</td>
          <td><a href="{{ url_for('admin.user_detail', telegram_id=user['telegram_id']) }}" class="btn btn-sm btn-info">View</a></td>
        </tr>
      {% endfor %}
      </tbody>
    </table>
  </div>
</div>
<footer class="footer mt-5 py-3 bg-light border-top">
  <div class="container text-center">
    <span class="text-muted">&copy; 2024 PrBot_Pay Admin Panel</span>
  </div>
</footer>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

USER_DETAIL_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>User Details - PrBot_Pay Admin</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
{{ navbar|safe }}
<div class="container">
  <h2 class="mb-4">User Details</h2>
  <div class="card mb-4">
    <div class="card-body">
      <h5 class="card-title">{{ user['full_name'] or '' }} <small class="text-muted">@{{ user['username'] or '' }}</small></h5>
      <p><b>Telegram ID:</b> {{ user['telegram_id'] }}</p>
      <p><b>Balance:</b> {{ user['balance'] }}</p>
      <p><b>Subscription:</b> {% if user['subscription_active'] %}<span class="badge bg-success">Active</span>{% else %}<span class="badge bg-secondary">Inactive</span>{% endif %}</p>
      <p><b>Welcomed:</b> {{ user['welcomed'] }}</p>
    </div>
  </div>
  <h4>Customer Profiles</h4>
  <div class="table-responsive mb-4">
    <table class="table table-bordered table-hover align-middle">
      <thead class="table-light">
        <tr>
          <th>Profile #</th>
          <th>Name</th>
          <th>Email</th>
          <th>Phone</th>
          <th>Gender</th>
          <th>City</th>
        </tr>
      </thead>
      <tbody>
      {% for p in profiles %}
        <tr>
          <td>{{ p['profile_number'] }}</td>
          <td>{{ p['first_name'] }} {{ p['last_name'] }}</td>
          <td>{{ p['email'] }}</td>
          <td>{{ p['phone_number'] }}</td>
          <td>{{ p['gender'] }}</td>
          <td>{{ p['city'] }}</td>
        </tr>
      {% endfor %}
      </tbody>
    </table>
    {% if not profiles %}<div class="alert alert-warning">No customer profiles found.</div>{% endif %}
  </div>
  <h4>Order/Payment History</h4>
  <div class="table-responsive">
    <table class="table table-bordered table-hover align-middle">
      <thead class="table-light">
        <tr>
          <th>ID</th>
          <th>Order Type</th>
          <th>Details</th>
          <th>Amount</th>
          <th>Status</th>
          <th>Created At</th>
        </tr>
      </thead>
      <tbody>
      {% for order in orders %}
        <tr>
          <td>{{ order['id'] }}</td>
          <td>{{ order['order_type'] }}</td>
          <td>{{ order['details'] }}</td>
          <td>{{ order['amount'] }}</td>
          <td>
            {% if order['status'] == 'cancelled' %}
              <span class="badge bg-danger">Cancelled</span>
            {% elif order['status'] == 'completed' %}
              <span class="badge bg-success">Completed</span>
            {% else %}
              <span class="badge bg-secondary">{{ order['status'] }}</span>
            {% endif %}
          </td>
          <td>{{ order['created_at'] }}</td>
        </tr>
      {% endfor %}
      </tbody>
    </table>
    {% if not orders %}<div class="alert alert-warning">No orders/payments found.</div>{% endif %}
  </div>
  <a href="{{ url_for('admin.users') }}" class="btn btn-secondary mt-3">Back to Users</a>
</div>
<footer class="footer mt-5 py-3 bg-light border-top">
  <div class="container text-center">
    <span class="text-muted">&copy; 2024 PrBot_Pay Admin Panel</span>
  </div>
</footer>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# 1. Update PAYMENTS_TEMPLATE to show Payment ID and clear cancel button
PAYMENTS_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>USD Payment History - PrBot_Pay Admin</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
{{ navbar|safe }}
<div class="container">
  <h2 class="mb-4">USD Payment History (Oxapay)</h2>
  <div class="table-responsive">
    <table class="table table-bordered table-hover align-middle">
      <thead class="table-light">
        <tr>
          <th>ID</th>
          <th>User</th>
          <th>Username</th>
          <th>Amount</th>
          <th>Order Type</th>
          <th>Details</th>
          <th>Payment ID</th>
          <th>Status</th>
          <th>Created At</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
      {% for p in payments %}
        <tr>
          <td>{{ p['id'] }}</td>
          <td><a href="{{ url_for('admin.user_detail', telegram_id=p['telegram_id']) }}">{{ p['telegram_id'] }}</a></td>
          <td>{{ p['username'] or '' }}</td>
          <td>{{ p['amount'] }}</td>
          <td>{{ p['order_type'] }}</td>
          <td>{{ p['details'] }}</td>
          <td>{% set pid = (p['details'].split('Payment ID: ')[1].split(')')[0] if 'Payment ID:' in p['details'] else '') %}{{ pid }}</td>
          <td>
            {% if p['status'] == 'cancelled' %}
              <span class="badge bg-danger">Cancelled</span>
            {% elif p['status'] == 'completed' %}
              <span class="badge bg-success">Completed</span>
            {% else %}
              <span class="badge bg-secondary">{{ p['status'] }}</span>
            {% endif %}
          </td>
          <td>{{ p['created_at'] }}</td>
          <td>
            {% if p['status'] != 'cancelled' %}
              <form method="post" action="{{ url_for('admin.cancel_payment', payment_id=p['id']) }}" style="display:inline">
                <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Cancel this payment?')">Cancel</button>
              </form>
            {% else %}—{% endif %}
          </td>
        </tr>
      {% endfor %}
      </tbody>
    </table>
    {% if not payments %}<div class="alert alert-warning">No USD/Oxapay payments found.</div>{% endif %}
  </div>
  <a href="{{ url_for('admin.dashboard') }}" class="btn btn-secondary mt-3">Back to Dashboard</a>
</div>
<footer class="footer mt-5 py-3 bg-light border-top">
  <div class="container text-center">
    <span class="text-muted">&copy; 2024 PrBot_Pay Admin Panel</span>
  </div>
</footer>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

def send_telegram_message(telegram_id, message):
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": telegram_id,
        "text": message
    }
    try:
        requests.post(url, data=data, timeout=5)
    except Exception:
        pass

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            error = 'Invalid credentials.'
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))

@app.route('/')
@app.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Join with users for username/full_name
    c.execute("""
        SELECT o.*, u.username, u.full_name FROM orders o
        LEFT JOIN users u ON o.telegram_id = u.telegram_id
        ORDER BY o.created_at DESC
    """)
    orders = c.fetchall()
    # Dashboard stats
    total = len(orders)
    completed = sum(1 for o in orders if o['status'] == 'completed')
    cancelled = sum(1 for o in orders if o['status'] == 'cancelled')
    refunded = sum(o['amount'] for o in orders if o['status'] == 'cancelled')
    stats = dict(total=total, completed=completed, cancelled=cancelled, refunded=refunded)
    conn.close()
    return render_template_string(DASHBOARD_TEMPLATE, orders=orders, stats=stats, navbar=render_template_string(NAVBAR, active='dashboard'))

@app.route('/users')
def users():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users ORDER BY telegram_id DESC")
    users = c.fetchall()
    conn.close()
    return render_template_string(USERS_TEMPLATE, users=users, navbar=render_template_string(NAVBAR, active='users'))

@app.route('/user/<int:telegram_id>')
def user_detail(telegram_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = c.fetchone()
    # Get all customer profiles for this user
    c.execute("SELECT profile_number, first_name, last_name, email, phone_number, gender, city FROM customer_profiles WHERE telegram_id = ? ORDER BY profile_number", (telegram_id,))
    profiles = c.fetchall()
    # Get all orders for this user
    c.execute("SELECT * FROM orders WHERE telegram_id = ? ORDER BY created_at DESC", (telegram_id,))
    orders = c.fetchall()
    conn.close()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.users'))
    return render_template_string(USER_DETAIL_TEMPLATE, user=user, orders=orders, profiles=profiles, navbar=render_template_string(NAVBAR, active='users'))

@app.route('/cancel/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Get order info
    c.execute("SELECT telegram_id, amount, status FROM orders WHERE id = ?", (order_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        flash('Order not found.', 'danger')
        return redirect(url_for('admin.dashboard'))
    telegram_id, amount, status = row
    if status == 'cancelled':
        conn.close()
        flash('Order already cancelled.', 'info')
        return redirect(url_for('admin.dashboard'))
    # Refund tokens if not already cancelled
    c.execute("UPDATE users SET balance = balance + ? WHERE telegram_id = ?", (amount, telegram_id))
    c.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    # Send Telegram message to user
    send_telegram_message(telegram_id, "❗️ Your order/payment has been cancelled by admin. If you have questions, please contact support.")
    flash('Order cancelled, tokens refunded, and user notified.', 'success')
    return redirect(url_for('admin.dashboard'))

@app.route('/payments')
def payments():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Filter for Oxapay/Token/Subscription payments
    c.execute("""
        SELECT o.*, u.username FROM orders o
        LEFT JOIN users u ON o.telegram_id = u.telegram_id
        WHERE (
            o.order_type IN ('token_purchase', 'subscription', 'custom_token', 'payment')
            OR o.details LIKE '%oxapay%'
            OR o.details LIKE '%_sub_%'
            OR o.details LIKE '%_token_%'
        )
        ORDER BY o.created_at DESC
    """)
    payments = c.fetchall()
    conn.close()
    return render_template_string(PAYMENTS_TEMPLATE, payments=payments, navbar=render_template_string(NAVBAR, active='payments'))

@app.route('/cancel_payment/<int:payment_id>', methods=['POST'])
def cancel_payment(payment_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Get payment info
    c.execute("SELECT telegram_id, amount, status FROM orders WHERE id = ?", (payment_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        flash('Payment not found.', 'danger')
        return redirect(url_for('admin.payments'))
    telegram_id, amount, status = row
    if status == 'cancelled':
        conn.close()
        flash('Payment already cancelled.', 'info')
        return redirect(url_for('admin.payments'))
    # Deduct tokens from user
    c.execute("UPDATE users SET balance = balance - ? WHERE telegram_id = ?", (amount, telegram_id))
    c.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (payment_id,))
    conn.commit()
    conn.close()
    # Notify user
    send_telegram_message(telegram_id, f"❗️ Your payment/order (ID: {payment_id}) has been cancelled by admin and the tokens have been deducted. If you have questions, please contact support.")
    flash('Payment cancelled, tokens deducted, and user notified.', 'success')
    return redirect(url_for('admin.payments')) 

if __name__ == "__main__":
    from flask import Flask
    real_app = Flask(__name__)
    real_app.secret_key = 'supersecretkey'  # Change as needed or load from env
    real_app.register_blueprint(app, url_prefix='/')
    real_app.run(debug=True, port=5000) 