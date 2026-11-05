from flask import Flask, request, redirect, make_response
import sqlite3
import secrets
import html
from datetime import datetime, timezone
from urllib.parse import quote

app = Flask(__name__)
DB = "goodluck.db"
TARGET = 5

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
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
    body{background:#101827;color:white;font-family:Arial;
    padding:20px;max-width:650px;margin:auto}
    .card{background:#1d2b40;padding:20px;border-radius:14px;
    margin:15px 0}
    button{background:#16a34a;color:white;border:0;
    padding:14px;border-radius:9px;width:100%;font-weight:bold}
    a{color:#4ade80;overflow-wrap:anywhere}
    .bar{background:#39465b;height:15px;border-radius:20px;overflow:hidden}
    .fill{background:#16a34a;height:15px}
    </style>
    <h1>GOOD LUCK 🍀</h1>
    """ + content

@app.route("/")
def home():
    with connect() as db:
        people = db.execute(
            "SELECT code,created FROM people ORDER BY created DESC"
        ).fetchall()
        total = db.execute(
            "SELECT COUNT(*) FROM referrals"
        ).fetchone()[0]

    content = f"""
    <div class="card">
    <h2>Invitation Dashboard</h2>
    <h1>{total}</h1>
    <p>Total unique referral visits</p>
    <a href="/join"><button>Join Invitation Programme</button></a>
    </div>
    <div class="card">
    <h3>Participant records</h3>
    """

    for code, created in people:
        content += f"""
        <p>Participant: {html.escape(code)}
        <br><a href="/participant/{quote(code)}">View progress</a></p>
        """

    content += "</div>"
    return page(content)

@app.route("/join")
def join():
    code = secrets.token_urlsafe(8)
    created = datetime.now(timezone.utc).isoformat()

    with connect() as db:
        db.execute(
            "INSERT INTO people VALUES (?,?)", (code,created)
        )

    return redirect("/participant/" + code)

@app.route("/participant/<code>")
def participant(code):
    with connect() as db:
        person = db.execute(
            "SELECT code FROM people WHERE code=?", (code,)
        ).fetchone()

        if not person:
            return "Participant not found", 404

        count = db.execute(
            "SELECT COUNT(*) FROM referrals WHERE code=?",
            (code,)
        ).fetchone()[0]

    percent = min(100, int(count / TARGET * 100))
    link = request.url_root.rstrip("/") + "/invite/" + code
    message = (
        "Join the GOOD LUCK invitation programme! "
        + link
    )
    whatsapp = "https://wa.me/?text=" + quote(message)

    content = f"""
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
