from flask import Flask, request, render_template, jsonify
import uuid
import bcrypt
import sqlite3
import os
from functools import wraps
import time

app = Flask(__name__)

SESSION_TTL = 60  # seconds

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')  

def get_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def init_db():
    schema = os.path.join(os.path.dirname(__file__), '..', 'database', 'db.sql')
    con = get_db()
    with open(schema, 'r') as f:
        con.executescript(f.read())
    con.close()

active_sessions = {}

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.json.get('session_token')

        if not token or token not in active_sessions:
            return jsonify({"message": "Unauthorized"}), 401
        
        session = active_sessions[token]
        if time.time() - session["created_at"] > SESSION_TTL:
            del active_sessions[token]
            return jsonify({"message": "Session expired"}), 401
        
        return f(*args, **kwargs)
    return wrapper

def data_check(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        data = request.json

        if not data:
            return jsonify({"message": "Invalid JSON"}), 400
        
        return f(*args, **kwargs)
    return wrapper


@app.route("/signup", methods=["POST"])
@data_check
def signup():
    data = request.json
    username = data.get("username", None)
    password = data.get("password", None)

    # sanity check
    if not username or not password:
        return jsonify({"message": "Invalid Input"}), 400
    
    con = get_db()
    existing = con.execute("SELECT 1 FROM user WHERE user_name = ?", (username,)).fetchone()
    if existing:
        con.close()
        return jsonify({"message": "username taken"}), 400
    
    user_id = str(uuid.uuid4())
    pass_id = str(uuid.uuid4())
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=8)).decode()
    
    con.execute("INSERT INTO user (user_id, user_name) VALUES (?, ?)", (user_id, username))
    con.execute("INSERT INTO password (pass_id, user_id, pass_hash) VALUES (?, ?, ?)", (pass_id, user_id, hashed))
    con.commit()
    con.close()

    return jsonify({"message": "User Created"}), 200 

@app.route("/login", methods=["POST"])
@data_check
def login():
    data = request.json
    username = data.get("username", None)
    password = data.get("password", None)

    if not username or not password:
        return jsonify({"message": "Invalid Input"}), 400

    con = get_db()
    
    row = con.execute(
        "SELECT u.user_id, p.pass_hash FROM user u JOIN password p ON u.user_id = p.user_id WHERE u.user_name = ?",
        (username,)
    ).fetchone()

    if not row:
        con.close()
        return jsonify({"message": "Invalid Credentials"}), 401

    if not bcrypt.checkpw(password.encode(), row["pass_hash"].encode()):
        con.close()
        return jsonify({"message": "Invalid Credentials"}), 401

    # logging in history
    history_id = str(uuid.uuid4())
    ip = request.remote_addr
    con.execute(
        "INSERT INTO history (history_id, user_id, ip_addr) VALUES (?, ?, ?)",
        (history_id, row["user_id"], ip)
    )
    con.commit()
    con.close()
    
    token = str(uuid.uuid4())
    active_sessions[token] = {
        "username": username,
        "user_id": row["user_id"],
        "history_id": history_id,
        "created_at": time.time()
    }

    return jsonify({"session_token": token}), 200

@app.route("/history", methods=["POST"])
@data_check
@require_auth
def history():
    data = request.json
    token = data.get("session_token")
    user_id = active_sessions[token]["user_id"]

    con = get_db()
    rows = con.execute(
        "SELECT ip_addr, login_time, logout_time FROM history WHERE user_id = ? ORDER BY login_time DESC",
        (user_id,)
    ).fetchall()
    con.close()

    return jsonify({"history": [dict(r) for r in rows]})

@app.route("/")
def auther_server():
    return "Home"

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# health check
@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(debug=True)