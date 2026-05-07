# AuthIQ — E-Commerce Fraud Intelligence Platform
> Shop Smart. Shop Authenticated. 🇮🇳

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start MongoDB (in a separate terminal)
mongod

# 3. Run the app
python app.py
# → http://127.0.0.1:5000
```

## Verify in MongoDB Compass
- Connect: `mongodb://localhost:27017`
- DB: `authiq`
- Collections: `users`, `sellers`, `websites`, `reports`
- Admin auto-seeded: `admin@authiq.in` / `admin123`

## Features

| Route | Description |
|-------|-------------|
| `/` | Landing + URL Risk Scanner |
| `/risk` (POST) | Risk score API — `{"url": "..."}` → `{"score", "level", "reasons"}` |
| `/seller` | Seller badge/QR registration |
| `/verify/<id>` | Public seller verification page (linked from QR) |
| `/qr/<id>` | Download QR badge image |
| `/report` (POST) | Report a scam site |
| `/login` `/register` `/logout` | Auth |
| `/admin` | Admin dashboard (login required) |
| `/risk/test` | Test the risk engine with sample URLs |

## Test the Risk Engine

```bash
# Via browser
http://127.0.0.1:5000/risk/test

# Via curl
curl -X POST http://127.0.0.1:5000/risk \
  -H "Content-Type: application/json" \
  -d '{"url": "free-iphone-win.xyz"}'
# → {"score": 5, "level": "Dangerous", "reasons": [...]}

curl -X POST http://127.0.0.1:5000/risk \
  -H "Content-Type: application/json" \
  -d '{"url": "flipkart.com"}'
# → {"score": 96, "level": "Low", ...}
```

## Risk Score Signals (12+)
- Domain age (WHOIS mock → real with `python-whois`)
- Suspicious TLD (.xyz, .tk, .ml, .ga, .cf...)
- Scam keywords in URL
- Missing Privacy Policy / Contact / About / Refund pages
- Numeric strings in domain
- Excessive hyphens
- Domain length

## Deploy to Render

1. Push to GitHub
2. New Web Service → connect repo
3. Set env var: `MONGO_URI=mongodb+srv://...` (MongoDB Atlas free tier)
4. Build: `pip install -r requirements.txt`
5. Start: `python app.py`

## Stack
- **Backend**: Flask + Flask-Login + Flask-PyMongo
- **Database**: MongoDB (local dev → Atlas in prod)
- **Frontend**: Bootstrap 5 + vanilla JS + custom CSS
- **Security**: bcrypt password hashing, Flask sessions
- **QR**: `qrcode[pil]` library
