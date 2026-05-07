import os
import re
import math
import random
import string
import bcrypt
import qrcode
import pymongo
from datetime import datetime
from bson import ObjectId
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("landing.html")

if __name__ == "__main__":
    app.run(debug=True)
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify, send_file, flash
)
from flask_login import (
    LoginManager, UserMixin, login_user,
    logout_user, login_required, current_user
)

# ── App setup ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "authiq-dev-secret-2024")

# ── MongoDB ────────────────────────────────────────────────────────────────────
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = pymongo.MongoClient(MONGO_URI)
db = client.authiq

# ── Flask-Login ────────────────────────────────────────────────────────────────
login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, doc):
        self.id = str(doc["_id"])
        self.email = doc["email"]
        self.name = doc["name"]
        self.role = doc.get("role", "user")

    def is_admin(self):
        return self.role == "admin"


@login_manager.user_loader
def load_user(user_id):
    doc = db.users.find_one({"_id": ObjectId(user_id)})
    return User(doc) if doc else None


# ── Seed admin ─────────────────────────────────────────────────────────────────
def seed_admin():
    if not db.users.find_one({"email": "admin@authiq.in"}):
        pw = bcrypt.hashpw(b"admin123", bcrypt.gensalt())
        db.users.insert_one({
            "name": "Admin",
            "email": "admin@authiq.in",
            "password_hash": pw,
            "role": "admin",
            "created_at": datetime.utcnow()
        })
        print("[AuthIQ] Admin seeded → admin@authiq.in / admin123")


# ── Risk Engine ────────────────────────────────────────────────────────────────
SCAM_KEYWORDS = [
    "free-iphone", "win-prize", "lottery", "claim-reward", "click-here-now",
    "limited-offer", "verify-now", "account-suspended", "urgent-action",
    "bitcoin-giveaway", "100x-returns", "guaranteed-profit"
]

TRUSTED_TLDS = [".in", ".com", ".org", ".gov", ".edu", ".net"]
SUSPICIOUS_TLDS = [".xyz", ".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".click"]

TRUSTED_DOMAINS = [
    "amazon", "flipkart", "myntra", "snapdeal", "meesho",
    "reliancedigital", "tatacliq", "nykaa", "ajio", "jiomart",
    "google", "microsoft", "apple", "facebook", "instagram"
]


def mock_whois_age(url):
    """Simulate WHOIS domain age in days."""
    domain = extract_domain(url)
    # Deterministically assign age based on domain hash for consistency
    h = sum(ord(c) for c in domain)
    return (h % 3000) + 10  # 10–3010 days


def mock_scrape(url):
    """Simulate page content keywords."""
    domain = extract_domain(url).lower()
    # Trusted domains get full content
    for td in TRUSTED_DOMAINS:
        if td in domain:
            return "privacy policy contact us about us return policy terms"
    # Scam-keyword domains get sparse content
    for kw in SCAM_KEYWORDS:
        if kw.replace("-", "") in domain.replace("-", ""):
            return "click win free offer"
    # Random sparse/full based on domain hash
    h = sum(ord(c) for c in domain)
    if h % 3 == 0:
        return "privacy policy contact us about us terms refund"
    if h % 3 == 1:
        return "buy now offer discount"
    return "shop deals"


def extract_domain(url):
    url = url.lower().strip()
    url = re.sub(r'^https?://', '', url)
    url = url.split('/')[0].split('?')[0]
    return url


def get_tld(url):
    domain = extract_domain(url)
    parts = domain.split('.')
    if len(parts) >= 2:
        return '.' + parts[-1]
    return ''


def get_risk_score(url):
    url = url.strip().lower()
    if not url.startswith("http"):
        url = "https://" + url

    reasons = []
    score = 100
    domain = extract_domain(url)

    # 1. Trusted domain fast-path
    for td in TRUSTED_DOMAINS:
        if td in domain:
            return 92 + random.randint(0, 8), "Low", ["Recognised trusted e-commerce/brand domain"]

    # 2. Scam keyword in URL
    for kw in SCAM_KEYWORDS:
        if kw.replace("-", "") in url.replace("-", "").replace(".", ""):
            score -= 35
            reasons.append(f"Scam-pattern keyword detected in URL: '{kw}'")
            break

    # 3. Domain age
    age = mock_whois_age(url)
    if age < 30:
        score -= 25
        reasons.append(f"Domain very new (< 30 days old) — high scam risk")
    elif age < 90:
        score -= 12
        reasons.append(f"Domain relatively new (< 90 days old)")
    elif age < 365:
        score -= 5
        reasons.append("Domain less than 1 year old")

    # 4. Suspicious TLD
    tld = get_tld(url)
    if tld in SUSPICIOUS_TLDS:
        score -= 20
        reasons.append(f"Suspicious free/low-trust TLD: {tld}")
    elif tld not in TRUSTED_TLDS:
        score -= 8
        reasons.append(f"Uncommon TLD: {tld}")

    # 5. Page content checks (mock scrape)
    content = mock_scrape(url)
    if "privacy" not in content and "policy" not in content:
        score -= 15
        reasons.append("No Privacy Policy page detected")
    if "contact" not in content:
        score -= 10
        reasons.append("No Contact Us page detected")
    if "return" not in content and "refund" not in content:
        score -= 8
        reasons.append("No Return/Refund policy found")
    if "about" not in content:
        score -= 5
        reasons.append("No About Us page detected")

    # 6. Numeric subdomain / excessive hyphens
    if re.search(r'\d{4,}', domain):
        score -= 10
        reasons.append("Domain contains suspicious long numeric string")
    if domain.count('-') >= 3:
        score -= 8
        reasons.append("Excessive hyphens in domain — common in scam URLs")

    # 7. Very long domain
    if len(domain) > 30:
        score -= 5
        reasons.append("Unusually long domain name")

    score = max(0, min(100, score))

    if score >= 75:
        level = "Low"
    elif score >= 50:
        level = "Medium"
    elif score >= 25:
        level = "High"
    else:
        level = "Dangerous"

    if not reasons:
        reasons.append("No major risk signals detected")

    return score, level, reasons


# ── QR / Badge helper ──────────────────────────────────────────────────────────
def generate_qr(seller_id, seller_name):
    os.makedirs("static/qr_badges", exist_ok=True)
    verify_url = f"https://authiq.in/verify/{seller_id}"
    img = qrcode.make(verify_url)
    path = f"static/qr_badges/{seller_id}.png"
    img.save(path)
    return path


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("landing.html")


# -- Auth --
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").encode()
        doc = db.users.find_one({"email": email})
        if doc and bcrypt.checkpw(password, doc["password_hash"]):
            login_user(User(doc))
            flash("Welcome back!", "success")
            return redirect(url_for("admin") if doc.get("role") == "admin" else url_for("index"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").encode()
        if db.users.find_one({"email": email}):
            flash("Email already registered.", "warning")
            return render_template("register.html")
        pw_hash = bcrypt.hashpw(password, bcrypt.gensalt())
        db.users.insert_one({
            "name": name, "email": email,
            "password_hash": pw_hash, "role": "user",
            "created_at": datetime.utcnow()
        })
        flash("Account created! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# -- Risk Check --
@app.route("/risk", methods=["POST"])
def risk():
    data = request.get_json(silent=True) or request.form
    url = (data.get("url") or "").strip()
    if not url:
        return jsonify({"error": "URL required"}), 400

    # Check cache
    cached = db.websites.find_one({"url": url})
    if cached:
        return jsonify({
            "score": cached["risk_score"],
            "level": cached["level"],
            "reasons": cached["reasons"],
            "cached": True
        })

    score, level, reasons = get_risk_score(url)
    db.websites.insert_one({
        "url": url, "risk_score": score,
        "level": level, "reasons": reasons,
        "checked_at": datetime.utcnow()
    })
    return jsonify({"score": score, "level": level, "reasons": reasons, "cached": False})


# -- Reports --
@app.route("/report", methods=["POST"])
def report():
    data = request.get_json(silent=True) or request.form
    url = (data.get("website_url") or "").strip()
    desc = (data.get("desc") or "").strip()
    upi = (data.get("upi") or "").strip()
    if not url or not desc:
        return jsonify({"error": "URL and description required"}), 400
    db.reports.insert_one({
        "website_url": url, "desc": desc, "upi": upi,
        "reported_at": datetime.utcnow(),
        "status": "pending"
    })
    return jsonify({"success": True, "message": "Report submitted. Thank you!"})


# -- Seller --
@app.route("/seller", methods=["GET", "POST"])
def seller():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        gst = request.form.get("gst", "").strip().upper()
        email = request.form.get("email", "").strip().lower()
        website = request.form.get("website", "").strip()
        if not name or not gst or not email:
            flash("All fields required.", "warning")
            return render_template("seller.html")

        # Basic GST format check (15 chars alphanumeric)
        if len(gst) != 15:
            flash("Invalid GST number (must be 15 characters).", "danger")
            return render_template("seller.html")

        existing = db.sellers.find_one({"gst": gst})
        if existing:
            flash("GST already registered.", "warning")
            return render_template("seller.html")

        result = db.sellers.insert_one({
            "name": name, "gst": gst, "email": email,
            "website": website, "verified": False,
            "badge_url": "", "qr_path": "",
            "registered_at": datetime.utcnow()
        })
        seller_id = str(result.inserted_id)
        qr_path = generate_qr(seller_id, name)
        db.sellers.update_one(
            {"_id": result.inserted_id},
            {"$set": {"qr_path": qr_path, "badge_url": f"/qr/{seller_id}"}}
        )
        flash("Registration submitted! Your QR badge is ready.", "success")
        return redirect(url_for("seller_success", seller_id=seller_id))
    return render_template("seller.html")


@app.route("/seller/success/<seller_id>")
def seller_success(seller_id):
    try:
        doc = db.sellers.find_one({"_id": ObjectId(seller_id)})
    except Exception:
        doc = None
    if not doc:
        flash("Seller not found.", "danger")
        return redirect(url_for("seller"))
    return render_template("seller_success.html", seller=doc, seller_id=seller_id)


@app.route("/qr/<seller_id>")
def qr(seller_id):
    path = f"static/qr_badges/{seller_id}.png"
    if os.path.exists(path):
        return send_file(path, mimetype="image/png")
    return "QR not found", 404


@app.route("/verify/<seller_id>")
def verify_seller(seller_id):
    try:
        doc = db.sellers.find_one({"_id": ObjectId(seller_id)})
    except Exception:
        doc = None
    return render_template("verify_seller.html", seller=doc, seller_id=seller_id)


# -- Admin --
@app.route("/admin")
@login_required
def admin():
    if not current_user.is_admin():
        flash("Admin access only.", "danger")
        return redirect(url_for("index"))
    sellers = list(db.sellers.find().sort("registered_at", -1))
    reports = list(db.reports.find().sort("reported_at", -1))
    stats = {
        "total_sellers": db.sellers.count_documents({}),
        "verified_sellers": db.sellers.count_documents({"verified": True}),
        "total_reports": db.reports.count_documents({}),
        "total_checks": db.websites.count_documents({}),
    }
    return render_template("admin.html", sellers=sellers, reports=reports, stats=stats)


@app.route("/admin/approve/<seller_id>", methods=["POST"])
@login_required
def approve_seller(seller_id):
    if not current_user.is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    db.sellers.update_one(
        {"_id": ObjectId(seller_id)},
        {"$set": {"verified": True}}
    )
    return jsonify({"success": True})


@app.route("/admin/reject/<seller_id>", methods=["POST"])
@login_required
def reject_seller(seller_id):
    if not current_user.is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    db.sellers.delete_one({"_id": ObjectId(seller_id)})
    return jsonify({"success": True})


# -- Legacy sim (kept as fallback) --
@app.route("/verify", methods=["POST"])
def verify_legacy():
    name = request.form.get("name", "")
    score = random.randint(60, 99)
    return jsonify({"name": name, "score": score, "status": "Simulated"})


# ── Dev test route ─────────────────────────────────────────────────────────────
@app.route("/risk/test")
def risk_test():
    test_urls = [
        "https://free-iphone-win-prize.xyz",
        "https://flipkart.com",
        "https://some-new-shop.tk",
        "https://amazon.in/products",
        "https://legit-store.com"
    ]
    results = []
    for u in test_urls:
        s, l, r = get_risk_score(u)
        results.append({"url": u, "score": s, "level": l, "top_reason": r[0]})
    return jsonify(results)


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    seed_admin()
    os.makedirs("static/qr_badges", exist_ok=True)
    app.run(debug=True, port=5000)
