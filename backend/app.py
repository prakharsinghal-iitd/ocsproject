from flask import Flask, jsonify,request
from flask_cors import CORS
import psycopg2
from config import DB_CONFIG
import jwt
import datetime
from functools import wraps

def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization")
        if not header:
            return jsonify({"error": "Missing token"}), 401

        token = header.split(" ")[0]
        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401

        return fn(*args, **kwargs)
    return wrapper


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

app = Flask(__name__)
CORS(app)

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/db-test")
def db_test():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    cur.close()
    conn.close()
    return jsonify({"db": "connected"})

@app.route("/api/login",methods=["POST"])
def login():
    data = request.json
    userid = data.get("userid")
    password_md5 = data.get("password_md5")

    if not userid or not password_md5:
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT userid, role FROM users WHERE userid=%s AND password_hash=%s",
        (userid, password_md5)
    )
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    payload = {
        "userid": user[0],
        "role": user[1],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }

    token = jwt.encode(payload, "secret", algorithm="HS256")



    return jsonify({
        "token": token,
        "role": user[1]
    })
@app.route("/api/users/me")
@auth_required
def me():
    return jsonify(request.user)

if __name__ == "__main__":
    app.run(debug=True,port=8000)

