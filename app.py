from flask import Flask, request, redirect, make_response, jsonify
import sqlite3
import os
import json
import secrets
import html
from datetime import datetime, timezone
from urllib.parse import quote
import firebase_admin
from firebase_admin import credentials, auth
app = Flask(__name__)
DB = "goodluck.db"
TARGET = 5
if not firebase_admin._apps:
    firebase_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    if firebase_json:
        cred = credentials.Certificate(json.loads(firebase_json))
    else:
        cred = credentials.Certificate("firebase-service-account.json")
    firebase_admin.initialize_app(cred)
def connect():
    return sqlite3.connect(DB)

with connect() as db:
    db.execute("""CREATE TABLE IF NOT EXISTS people (
        code TEXT PRIMARY KEY,
        created TEXT NOT NULL
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        visitor TEXT NOT NULL,
        visited TEXT NOT NULL,
        UNIQUE(code, visitor)
    )""")

def page(content):
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <meta name="theme-color" content="#32143f">
    <title>GOOD LUCK - Rewards & Opportunities</title>
    <style>
    *{box-sizing:border-box}
    body{background:#32143f;color:#fff;font-family:Arial,sans-serif;
    padding:18px;margin:0;max-width:760px;margin:auto}
    header{padding:12px 4px 25px}
    header h1{color:#ff75bd;font-size:27px;margin:8px 0}
    .hero{background:linear-gradient(140deg,#173c30,#17243b 65%,#493719);
    border:1px solid #d879b5;border-radius:22px;padding:28px 22px;
    margin:12px 0 20px}
    .tag{color:#ffb6dc;font-size:12px;letter-spacing:2px;font-weight:bold}
    .hero h2{font-size:32px;line-height:1.15;margin:15px 0}
    .hero p{color:#e0e5e2;line-height:1.6}
    .card{background:#51245f;padding:20px;border-radius:16px;
    margin:15px 0;border:1px solid #854a83}
    .gold{color:#ff75bd}
    button{background:linear-gradient(90deg,#ec4899,#f9a8d4);
    color:#ffffff;border:0;padding:16px;border-radius:10px;
    width:100%;font-weight:bold;font-size:16px}

    form{display:flex;flex-direction:column;gap:9px;margin-top:18px}
    label{display:block;color:#ffb6dc;font-weight:bold;font-size:14px;margin-top:7px}
    input{display:block;width:100%;padding:15px;border-radius:10px;
    border:1px solid #d879b5;background:#32143f;color:#fff;
    font-size:16px;outline:none}
    input:focus{border-color:#f9a8d4;box-shadow:0 0 0 2px #ec489944}
    form button{margin-top:12px;min-height:54px}
    a{color:#ff75bd;overflow-wrap:anywhere}
    .bar{background:#68416f;height:15px;border-radius:20px;overflow:hidden}
    .fill{background:#16a34a;height:15px}
    .small{font-size:12px;color:#b9c4d1;line-height:1.5}
    </style>
    </head>
    <body>
    <header><h1>GOOD LUCK 🍀</h1>
    <div class="small">REWARDS • REFERRALS • OPPORTUNITIES</div></header>
    """ + content + """
    <script type="module" src="/static/auth.js"></script>
    </body></html>
    """

@app.route("/")
def home():
    content = """
    <section style="text-align:center;margin:15px 0 25px">
      <img src="/static/good-luck.jpg"
           alt="GOOD LUCK banner"
           style="width:100%;max-height:390px;object-fit:cover;border-radius:18px">
    </section>

    <section class="hero" style="text-align:center">
      <div class="tag">YOUR NEXT OPPORTUNITY STARTS HERE</div>
      <h2>Discover Rewards. Share Opportunities.</h2>
      <p>Join GOOD LUCK, explore opportunities and create your own invitation link.</p>
      <a href="/join"><button>JOIN NOW — IT'S FREE</button></a>
      <p class="small">Rewards depend on verified activities, sponsor approval
      and available funding. Earnings are not guaranteed.</p>
    </section>

    <h2 class="gold" style="text-align:center;margin-top:30px">
      EXPLORE OPPORTUNITIES
    </h2>

    <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px">

      <div class="card">
        <img src="/static/images/investment.jpg" alt="Investment"
             style="width:100%;height:135px;object-fit:cover;border-radius:12px">
        <h3>Investment</h3>
        <p class="small">Explore investment opportunities and understand the risks.</p>
      </div>

      <div class="card">
        <img src="/static/images/real-estate.jpg" alt="Real estate"
             style="width:100%;height:135px;object-fit:cover;border-radius:12px">
        <h3>Real Estate</h3>
        <p class="small">Discover property and real estate opportunities.</p>
      </div>

      <div class="card">
        <img src="/static/images/crypto.jpg" alt="Cryptocurrency"
             style="width:100%;height:135px;object-fit:cover;border-radius:12px">
        <h3>Cryptocurrency</h3>
        <p class="small">Learn about digital assets and their risks.</p>
      </div>

      <div class="card">
        <img src="/static/images/business.jpg" alt="Business"
             style="width:100%;height:135px;object-fit:cover;border-radius:12px">
        <h3>Business</h3>
        <p class="small">Explore business ideas and opportunities.</p>
      </div>

    </div>

    <section class="card" style="text-align:center;margin-top:20px">
      <h2>JOIN GOOD LUCK</h2>
      <p>Create your participant account and get your invitation link.</p>
      <a href="/join"><button>GET STARTED — IT'S FREE</button></a>
    </section>
    """
    return page(content)



@app.route("/login")
def login():
    content = """
    <section class="card">
      <h2>LOGIN</h2>
      <p>Welcome back to GOOD LUCK.</p>
      <form id="login-form">
        <label>Email address</label>
        <input id="login_email" type="email" required>
        <label>Password</label>
        <input id="login_password" type="password" required>
        <button type="button" id="email-login">LOGIN</button>
        <button type="button" id="google-login">CONTINUE WITH GOOGLE</button>
        <button type="button" id="facebook-login">CONTINUE WITH FACEBOOK</button>
      </form>
      <p class="small">New here? <a href="/join">CREATE ACCOUNT</a></p>
    </section>
    """
    return page(content)

@app.route("/join", methods=["GET", "POST"])
def join():
    first_name = ""
    second_name = ""
    email = ""
    error = ""

    if request.method == "POST":
        error = "Please use the verified email registration buttons."

    content = f"""
    <section class="card">
      <h2>JOIN GOOD LUCK</h2>
      <p>Create your participant account and get your invitation link.</p>
      <p>{html.escape(error)}</p>
      <form id="join-form">
          <label>First name</label>
          <input id="first_name" name="first_name" required maxlength="60"
                 value="{html.escape(first_name, quote=True)}">
          <label>Second name</label>
          <input id="second_name" name="second_name" required maxlength="60"
                 value="{html.escape(second_name, quote=True)}">
          <label>Email address</label>
          <input id="email" type="email" name="email" required
                 value="{html.escape(email, quote=True)}">
          <label>Password</label>
          <input id="password" type="password" minlength="6" required>
          <button type="button" id="google-login">CONTINUE WITH GOOGLE</button>
          <button type="button" id="create-account">CREATE ACCOUNT &amp; SEND VERIFICATION LINK</button>
          <button type="button" id="verified-login">I HAVE VERIFIED MY EMAIL — CONTINUE</button>
        </form>
    </section>
    """
    return page(content)


@app.route("/auth/register", methods=["POST"])
def verified_register():
    data = request.get_json(silent=True) or {}
    token = data.get("token", "")
    first_name = data.get("first_name", "").strip()
    second_name = data.get("second_name", "").strip()

    if not token:
        return jsonify(error="Missing Firebase sign-in token."), 400

    try:
        decoded = auth.verify_id_token(token)
    except Exception:
        return jsonify(error="Invalid or expired Firebase sign-in. Please sign in again."), 401

    if decoded.get("email_verified") is not True:
        return jsonify(error="Please verify your email before continuing."), 403

    email = decoded.get("email", "").strip().lower()
    if not email:
        return jsonify(error="Firebase account has no email address."), 400

    code = secrets.token_urlsafe(8)
    created = datetime.now(timezone.utc).isoformat()

    with connect() as db:
        columns = {
            row[1] for row in db.execute("PRAGMA table_info(people)")
        }
        for column in ("first_name", "second_name", "email"):
            if column not in columns:
                db.execute(
                    f"ALTER TABLE people ADD COLUMN {column} TEXT"
                )

        existing = db.execute(
            "SELECT code FROM people WHERE email=?",
            (email,)
        ).fetchone()

        if existing:
            code = existing[0]
        else:
            if not first_name or not second_name:
                return jsonify(error="Names are required when creating a new participant account."), 400

            db.execute(
                """INSERT INTO people
                (code, created, first_name, second_name, email)
                VALUES (?, ?, ?, ?, ?)""",
                (code, created, first_name, second_name, email)
            )

    return jsonify(redirect="/participant/" + code)


@app.route("/participant/<code>")
def participant(code):
    with connect() as db:
        person = db.execute(
            "SELECT code, first_name, second_name FROM people WHERE code=?", (code,)
        ).fetchone()

        if not person:
            return "Participant not found", 404

        count = db.execute(
            "SELECT COUNT(*) FROM referrals WHERE code=?",
            (code,)
        ).fetchone()[0]

    full_name = " ".join(filter(None, [person[1], person[2]])) or "GOOD LUCK member"
    percent = min(100, int(count / TARGET * 100))
    link = request.url_root.rstrip("/") + "/invite/" + code
    message = (
        "Join the GOOD LUCK invitation programme! "
        + link
    )
    whatsapp = "https://wa.me/?text=" + quote(message)

    content = f"""
    <h2>Welcome, {html.escape(full_name)}</h2>
    <div class="card">
    <h2>Your invitation progress</h2>
    <h1>{percent}%</h1>
    <div class="bar"><div class="fill" style="width:{percent}%"></div></div>
    <p>{count} of {TARGET} unique referral visits</p>
    </div>
    <div class="card">
    <h3>Your personal invitation link</h3>
    <p><a href="{html.escape(link)}">{html.escape(link)}</a></p>
    <a href="{html.escape(whatsapp)}">
    <button>Share invitation on WhatsApp</button></a>
    </div>
    <p>Progress measures unique referral visits.
    Completion does not guarantee a cash or data reward.</p>
    <a href="/">Main dashboard</a>
    """
    return page(content)

@app.route("/invite/<code>")
def invite(code):
    with connect() as db:
        person = db.execute(
            "SELECT code FROM people WHERE code=?", (code,)
        ).fetchone()

        if not person:
            return "Invitation not found", 404

        visitor = request.cookies.get("gl_visitor")
        if not visitor:
            visitor = secrets.token_urlsafe(16)

        db.execute("""
            INSERT OR IGNORE INTO referrals(code,visitor,visited)
            VALUES (?,?,?)
        """, (code,visitor,datetime.now(timezone.utc).isoformat()))

    response = make_response(redirect("/join-info"))
    response.set_cookie(
        "gl_visitor", visitor, max_age=31536000,
        httponly=True, samesite="Lax"
    )
    return response

@app.route("/join-info")
def join_info():
    return page("""
    <div class="card">
    <h2>Welcome to GOOD LUCK 🍀</h2>
    <p>You arrived through an invitation.</p>
    <p>Learn about the invitation programme and its terms.</p>
    <a href="/join"><button>Create your own invitation link</button></a>
    </div>
    """)

if __name__ == "__main__":
    app.run(host="127.0.0.1",port=8082)
