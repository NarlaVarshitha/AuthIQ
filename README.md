# AuthiQ — Complete Setup Guide (Windows / PowerShell)

## FOLDER STRUCTURE

```
authiq/
├── backend/
│   ├── package.json
│   └── server.js
└── frontend/
    ├── package.json
    ├── public/
    │   └── index.html
    └── src/
        ├── index.js
        ├── index.css
        ├── App.js
        ├── components/
        │   └── ProtectedRoute.js
        └── pages/
            ├── LoginPage.js
            ├── RegisterPage.js
            └── DashboardPage.js
```

---

## STEP-BY-STEP SETUP (Windows PowerShell)

### STEP 1 — Create the folder structure

Open PowerShell and run these commands ONE BY ONE:

```powershell
mkdir authiq
cd authiq
mkdir backend
mkdir frontend
```

### STEP 2 — Copy all the files

Copy each file from the provided code into the correct locations.
Use VS Code to create and paste the files (right-click folder → New File).

DO NOT use the `touch` command — it doesn't work on Windows.
Instead, in VS Code's Explorer panel, right-click a folder and choose "New File".

### STEP 3 — Install backend dependencies

```powershell
cd backend
npm install
```

This installs: express, cors, bcryptjs, jsonwebtoken, nodemon

### STEP 4 — Install frontend dependencies

Open a NEW PowerShell window (keep the backend one open):

```powershell
cd authiq\frontend
npm install
```

This installs: react, react-dom, react-router-dom, react-scripts

> ⚠️ npm install may take 2–5 minutes on first run. This is normal.

### STEP 5 — Start the backend

In your FIRST PowerShell window (inside authiq/backend):

```powershell
npm start
```

You should see:
```
🚀 AuthiQ backend running at http://localhost:5000
📋 Available routes:
   GET  http://localhost:5000/
   POST http://localhost:5000/api/register
   POST http://localhost:5000/api/login
   GET  http://localhost:5000/api/dashboard
```

### STEP 6 — Start the frontend

In your SECOND PowerShell window (inside authiq/frontend):

```powershell
npm start
```

Your browser will automatically open http://localhost:3000

---

## HOW TO USE THE APP

1. Go to http://localhost:3000 → you'll be redirected to /login
2. Click "Create one here" to go to /register
3. Create an account (username min 3 chars, password min 6 chars)
4. You'll be redirected back to /login
5. Log in with your credentials
6. You'll land on /dashboard — you're authenticated!
7. Click "Sign Out" to log out and return to login

---

## COMMON ERRORS AND FIXES

### ❌ Error: "Cannot connect to server" or "Failed to fetch"
**Cause:** Backend is not running.
**Fix:**
1. Make sure you ran `npm start` inside the `backend` folder
2. Check that it says "running at http://localhost:5000"
3. Visit http://localhost:5000 in your browser — you should see a JSON response

---

### ❌ Error: "npm is not recognized"
**Cause:** Node.js is not installed or not in your PATH.
**Fix:**
1. Download Node.js from https://nodejs.org (choose "LTS" version)
2. Restart PowerShell after installing
3. Run: `node --version` and `npm --version` to verify

---

### ❌ Error: "Port 5000 already in use"
**Cause:** Another program is using port 5000.
**Fix (PowerShell):**
```powershell
netstat -ano | findstr :5000
```
Note the PID number at the end, then:
```powershell
taskkill /PID <PID_NUMBER> /F
```
Then try `npm start` again.

---

### ❌ Error: "Port 3000 already in use"
**Fix:** When prompted "Something is already running on port 3000. Would you like to run the app on another port?", press `Y`.
Or kill it the same way as port 5000 above.

---

### ❌ Error: "Cannot GET /"
**Cause:** You're visiting a backend route directly in the browser.
- http://localhost:5000/ → Shows JSON (this is correct ✅)
- http://localhost:5000/api/register → Won't work in browser (needs POST request) ✅ normal

---

### ❌ Error: "User not found" / "Invalid username or password"
**Cause:** The in-memory database resets every time the backend restarts.
**Fix:** After restarting the backend, register a new account first, then log in.

---

### ❌ Error: "Invalid or expired token"
**Cause:** JWT tokens expire after 1 hour OR the backend was restarted (which resets the secret).
**Fix:** Log out and log in again to get a fresh token.

---

### ❌ Error: "Module not found" (React)
**Cause:** Dependencies weren't installed.
**Fix:**
```powershell
cd authiq\frontend
npm install
```

---

### ❌ Error: "Cannot find module 'express'" (Backend)
**Cause:** Backend dependencies weren't installed.
**Fix:**
```powershell
cd authiq\backend
npm install
```

---

### ❌ White screen / nothing loads
**Cause:** A JavaScript error in React.
**Fix:** Open your browser DevTools (press F12) → Console tab → read the error message.

---

## TECH STACK SUMMARY

| Layer     | Technology         | Port |
|-----------|--------------------|------|
| Frontend  | React (CRA)        | 3000 |
| Backend   | Express + Node.js  | 5000 |
| Auth      | JWT + bcryptjs     | —    |
| Storage   | In-memory (array)  | —    |

---

## API REFERENCE

| Method | URL                          | Auth Required | Description        |
|--------|------------------------------|---------------|--------------------|
| GET    | http://localhost:5000/       | No            | Health check       |
| POST   | http://localhost:5000/api/register | No      | Create account     |
| POST   | http://localhost:5000/api/login    | No      | Login + get token  |
| GET    | http://localhost:5000/api/dashboard | Yes (Bearer token) | Protected data |
