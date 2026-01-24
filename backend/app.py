from flask import Flask, jsonify,request
from flask_cors import CORS
import psycopg2
from config import DB_CONFIG
import jwt
import datetime
from functools import wraps

SECRET_KEY="secret"

def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization")
        if not header:
            return jsonify({"error": "Missing token"}), 401

        token = header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except:
            return jsonify({"error": "Unauthorised Access"}), 401

        return fn(*args, **kwargs)
    return wrapper


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

app = Flask(__name__)
CORS(app, origins=["https://ocsproject.vercel.app"])

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

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")



    return jsonify({
        "token": token,
        "role": user[1]
    })

@app.route("/api/users/me")
@auth_required
def me():
    return jsonify(request.user)

@app.route("/api/users")
@auth_required
def users():
    role = request.user["role"]
    if role!="admin":
        return jsonify({"error": "Forbidden"}), 403
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
    "SELECT userid,role FROM users")

    users=cur.fetchall()

    cur.close()
    conn.close()

    #Convert data into json
    res={"users":[],"count":0}
    for row in users:
        res["users"].append({
      "userid": row[0],
      "role": row[1]})
        res["count"]+=1

    return jsonify(res)


@app.route("/api/profiles")
@auth_required
def profiles():
    role = request.user["role"]
    userid = request.user["userid"]

    #For students and admin, fetch all profiles
    if role=="admin" or role=="student":
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
        "SELECT * FROM profile")

        profiles=cur.fetchall()

        cur.close()
        conn.close()
    
    #For recruiter, only fetch their profiles
    elif role=="recruiter":
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
        "SELECT * FROM profile WHERE recruiter_email=%s",(userid,))

        profiles=cur.fetchall()

        cur.close()
        conn.close()

    else:
        return jsonify({"error": "Forbidden"}), 403

    #Convert data into json
    res={"profiles":[],"count":0}
    for row in profiles:
        res["profiles"].append({
      "profile_code": row[0],
      "company_name": row[2],
      "designation":  row[3],
      "recruiter_email": row[1]})
        res["count"]+=1

    return jsonify(res)

@app.route("/api/apply",methods=["POST"])
@auth_required
def apply():
    data = request.json
    role = request.user["role"]
    userid = request.user["userid"]

    if role!="student":
        return jsonify({"error": "Forbidden"}), 403

    profile_code=data.get("profile_code")
    if not profile_code:
        return jsonify({"error": "Missing fields"}), 400

    #Check if profile exists
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
    "SELECT * FROM profile WHERE profile_code=%s",(profile_code,))

    res=cur.fetchall()

    cur.close()
    conn.close()
    if not res:
        return jsonify({"error": "Profile does not exist"}), 400

    #Check if student has already applied for this profile
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
    "SELECT * FROM application WHERE profile_code=%s AND entry_number=%s",(profile_code,userid))

    res=cur.fetchall()

    cur.close()
    conn.close()
    if res:
        return jsonify({"error": "Already applied"}), 400


    #Check if student has Selected offer
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
    "SELECT * FROM application WHERE entry_number=%s AND status='Selected'",(userid,))

    res=cur.fetchall()

    cur.close()
    conn.close()
    if res:
        return jsonify({"error": "Selected profile exists"}), 400

    #Apply for offer
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
    "INSERT INTO application (profile_code, entry_number, status) VALUES (%s,%s,'Applied')",(profile_code,userid))
    conn.commit()

    cur.close()
    conn.close()
    return jsonify({
  "message": "Application submitted successfully"
})

@app.route("/api/application/change_status",methods=["POST"])
@auth_required
def change_status():
    data = request.json
    role = request.user["role"]
    userid = request.user["userid"]

    if role=="student":
        return jsonify({"error": "Forbidden"}), 403

    profile_code=data.get("profile_code")
    entry_number=data.get("entry_number")
    new_status=data.get("new_status")
    if not profile_code or not entry_number or not new_status:
        return jsonify({"error": "Missing fields"}), 400

    #Check if recruiter, then it must be their own profile
    if role=="recruiter":
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
        "SELECT * FROM profile WHERE profile_code=%s AND recruiter_email=%s",(profile_code,userid))

        res=cur.fetchone()

        cur.close()
        conn.close()
        if not res:
            return jsonify({"error": "Profile does not belong to recruiter"}), 403

    #Check if application exists
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
    "SELECT * FROM application WHERE entry_number=%s AND profile_code=%s",(entry_number,profile_code))

    res=cur.fetchone()

    cur.close()
    conn.close()
    if not res:
        return jsonify({"error": "Student has not applied for this profile"}), 404
    #Check that new_status is Selected
    if new_status!="Selected" or (role!="recruiter" and new_status=="Rejected"):
        return jsonify({"error": "Invalid new status"}), 400

    #Check if student already has a selected application
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
    "SELECT * FROM application WHERE entry_number=%s AND status='Selected'",(entry_number,))

    res=cur.fetchall()

    cur.close()
    conn.close()
    if res:
        return jsonify({"error": "Selected profile exists"}), 400
    
    #Change status
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
    "UPDATE application SET status=%s WHERE profile_code=%s AND entry_number=%s",(new_status,profile_code,entry_number))
    conn.commit()

    cur.close()
    conn.close()
    return jsonify({
  "message": "Application status updated"
})

@app.route("/api/application/respond",methods=["POST"])
@auth_required
def accept():
    data = request.json
    role = request.user["role"]
    userid = request.user["userid"]

    if role!="student":
        return jsonify({"error": "Forbidden"}), 403

    profile_code=data.get("profile_code")
    new_status=data.get("new_status")
    if not profile_code or not new_status:
        return jsonify({"error": "Missing fields"}), 400
    if new_status not in ["Accepted","Rejected"]:
        return jsonify({"Error": "Invalid new status"}), 400

    #Check if profile exists
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
    "SELECT * FROM profile WHERE profile_code=%s",(profile_code,))

    res=cur.fetchall()

    cur.close()
    conn.close()
    if not res:
        return jsonify({"error": "Profile does not exist"}), 400

    #Check if student has applied for this profile and is selected
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
    "SELECT * FROM application WHERE profile_code=%s AND entry_number=%s",(profile_code,userid))

    res=cur.fetchone()

    cur.close()
    conn.close()
    if not res:
        return jsonify({"error": "Not applied"}), 400
    if res[2]!="Selected":
        return jsonify({"error": "Not selected"}), 400

    #Change status
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
    "UPDATE application SET status=%s WHERE profile_code=%s AND entry_number=%s",(new_status,profile_code,userid))
    conn.commit()

    cur.close()
    conn.close()
    return jsonify({
  "message": f"Offer {new_status} successfully"
})

@app.route("/api/create_profile",methods=["POST"])
@auth_required
def create_profile():
    data = request.json
    role = request.user["role"]
    userid = request.user["userid"]

    if role=="student":
        return jsonify({"error": "Forbidden"}), 403

    company_name=data.get("company_name")
    designation=data.get("designation")
    recruiter_email=data.get("recruiter_email") if role=="admin" else userid
    if not company_name or not designation or (role=="admin" and not recruiter_email):
        return jsonify({"error": "Missing fields"}), 400

    #Check if recruiter exists, if role is admin
    if role=="admin":
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
        "SELECT userid,role FROM users WHERE userid=%s",(recruiter_email,))

        res=cur.fetchone()

        cur.close()
        conn.close()
        if not res:
            return jsonify({"error": "Recruiter does not exist"}), 404
        if res[1]!="recruiter":
            return jsonify({"error": "Not a recruiter"}), 400

    #Create profile
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
    "INSERT INTO profile (recruiter_email,company_name,designation) VALUES (%s,%s,%s)",(recruiter_email,company_name,designation))
    conn.commit()

    cur.close()
    conn.close()
    return jsonify({
  "message": "Profile created successfully"
})

@app.route("/api/application/me")
@auth_required
def myapplications():
    role = request.user["role"]
    userid = request.user["userid"]

    if role=="student":
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
        "SELECT a.profile_code,p.company_name,p.designation,a.status FROM application a JOIN profile p ON a.profile_code = p.profile_code WHERE a.entry_number = %s",(userid,))

        profiles=cur.fetchall()

        cur.close()
        conn.close()

        res={"applications":[],"count":0}
        for row in profiles:
            res["applications"].append({
          "profile_code": row[0],
          "company_name": row[1],
          "designation":  row[2],
          "status": row[3]})
            res["count"]+=1

        return jsonify(res)
    elif role=="recruiter":
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
        "SELECT a.profile_code,a.entry_number,a.status FROM application a JOIN profile p ON a.profile_code = p.profile_code WHERE p.recruiter_email = %s",(userid,))

        profiles=cur.fetchall()

        cur.close()
        conn.close()

        res={"applications":[],"count":0}
        for row in profiles:
            res["applications"].append({
          "profile_code": row[0],
          "entry_number": row[1],
          "status": row[2]})
            res["count"]+=1

        return jsonify(res)

    else:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
        "SELECT * FROM application")

        profiles=cur.fetchall()

        cur.close()
        conn.close()

        res={"applications":[],"count":0}
        for row in profiles:
            res["applications"].append({
          "profile_code": row[0],
          "entry_number": row[1],
          "status": row[2]})
            res["count"]+=1

        return jsonify(res)




if __name__ == "__main__":
    app.run(debug=True,port=8000)

