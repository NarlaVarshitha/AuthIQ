# AuthIQ: Digital Trust Intelligence platform

![AuthIQ Banner](https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&q=80&w=1200&h=400)

**AuthIQ** is an advanced verification ecosystem designed to restore faith in digital commerce. By leveraging the **Digital Commerce Trust Index (DCTI)**, AuthIQ provides a 0–100 real-time transparency score for any e-commerce platform, helping consumers avoid scams and helping legitimate sellers build professional credibility.

## 🚀 Key Features

### 🛡️ For Consumers (Trust Checker)
- **Real-time URL Scanning:** Instantly evaluate any website or payment link.
- **DCTI Breakdown:** Detailed analysis of SSL security, domain authority, and reputation signals.
- **Deep AI Scan:** Behavioral analysis to detect "dark patterns" and fraudulent intent.
- **Crowdsourced Intelligence:** Integrated scam reporting database.

### 🏪 For Sellers (Verification Hub)
- **Trust Roadmap:** Step-by-step guidance to improve store legitimacy.
- **Verification Badge:** A dynamic, fraud-proof trust seal to embed on store-fronts.
- **Document Vault:** Securely upload and verify business identification (GST, Registration).
- **Optimization roadmap:** Actionable suggestions to boost trust scores and conversion rates.

### 🛠️ For Developers (API)
- **Trust Endpoints:** Programmatically check domain safety within third-party apps.
- **Scam Feed:** Access the global AuthIQ blacklist via REST API.

## 💻 Tech Stack

- **Frontend:** HTML5, CSS3 (Modern UI with Glassmorphism), Vanilla JavaScript.
- **Backend:** Node.js, Express.js, TypeScript.
- **Security:** CSRF Protection, URL Sanitization, SSL/TLS analysis algorithms.
- **Dev Tooling:** Vite, npx, tsx.

## ⚙️ Installation & Setup

### Prerequisites
- [Node.js](https://nodejs.org/) (v18 or higher)
- npm or yarn

### Quick Start
1. **Clone the repository:**
   ```bash
   git clone https://github.com/NarlaVarshitha/authiq.git
   cd authiq
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Environment Setup:**
   Create a `.env` file in the root (see `.env.example`):
   ```env
   PORT=3000
   NODE_ENV=development
   ```

4. **Run the Development Server:**
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:3000`.

## 📊 DCTI Scoring Logic
The **Digital Commerce Trust Index** evaluates four major pillars:
1. **SSL/TLS Integrity (25%):** Protocol strength and certificate authority verification.
2. **Domain Metadata (25%):** Age of domain, TLD reputation, and DNS health.
3. **Policy Transparency (25%):** Link detection for Refund, Privacy, and Shipping policies.
4. **Reputation Signals (25%):** Cross-referencing against global scam reports and phishing keywords.

## 🗺️ Project Structure
```text
├── src/                # Shared assets and styles
├── server.ts           # Express server with Trust Scoring API
├── user-dashboard.html # Consumer portal
├── seller-dashboard.html# Merchant portal
├── report-scam.html    # Crowdsourced reporting interface
├── api-docs.html       # Developer documentation
└── package.json        # Project configuration
```

## 🤝 Contributing
We welcome contributions to the AuthIQ Trust Network! 
1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

---
*Built to make the internet a safer place for commerce.*

