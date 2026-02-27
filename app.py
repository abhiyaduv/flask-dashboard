from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE CONNECTION ---------------- #

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- DATABASE SETUP ---------------- #

def init_db():
    conn = get_db()

    # USERS TABLE
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
    """)
create_table()

    # PRODUCTS TABLE
    conn.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        quantity INTEGER NOT NULL
    )
    """)

    # CREATE DEFAULT ADMIN USER
    user = conn.execute(
        "SELECT * FROM users WHERE username='admin'"
    ).fetchone()

    if not user:
        conn.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            ("admin", "123")
        )

    conn.commit()
    conn.close()


# RUN DATABASE SETUP
init_db()


# ---------------- LOGIN ---------------- #

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")

    return render_template("login.html")


# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    conn = get_db()

    total_users = conn.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    total_products = conn.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]

    products = conn.execute(
        "SELECT * FROM products"
    ).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        users=total_users,
        products_count=total_products,
        products=products
    )


# ---------------- USERS PAGE ---------------- #

@app.route("/users")
def users():

    if "user" not in session:
        return redirect("/")

    conn = get_db()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()

    return render_template("users.html", users=users)
    # ---------------- ADD USER ---------------- #

@app.route("/add_user", methods=["POST"])
def add_user():

    if "user" not in session:
        return redirect("/")

    username = request.form["username"]
    password = request.form["password"]

    conn = get_db()
    conn.execute(
        "INSERT INTO users(username,password) VALUES(?,?)",
        (username, password)
    )
    conn.commit()
    conn.close()

    return redirect("/users")

# ---------------- PRODUCTS PAGE ---------------- #

@app.route("/products")
def products():

    if "user" not in session:
        return redirect("/")

    conn = get_db()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()

    return render_template("products.html", products=products)


# ---------------- ADD PRODUCT ---------------- #

@app.route("/add", methods=["POST"])
def add():

    name = request.form["name"]
    qty = request.form["quantity"]

    conn = get_db()
    conn.execute(
        "INSERT INTO products(name,quantity) VALUES(?,?)",
        (name, qty)
    )
    conn.commit()
    conn.close()

    return redirect("/products")


# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- RUN APP ---------------- #
if __name__ == "__main__":

    app.run(host="0.0.0.0", port=10000)

