console.log("[AuthIQ Server] Starting server script...");

import express from "express";
import { createServer as createViteServer } from "vite";
import path from "path";
import { fileURLToPath } from "url";
import { createServer as createHttpServer } from "http";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function startServer() {
  const app = express();
  const PORT = 3000;
  const httpServer = createHttpServer(app);

  app.use(express.json());

  app.use((req, res, next) => {
    console.log(`[AuthIQ Server] ${req.method} ${req.url}`);
    next();
  });

  // Mock Scam Database
  const SCAM_DATABASE = [
    "scammy-shop.in",
    "cheap-iphones-free.com",
    "win-prize-now.xyz",
    "verified-scam.biz"
  ];

  // AIAgent Scoring Logic
  const calculateTrustScore = async (urlStr: string) => {
    // Timeout promise for the analysis (set to 8 seconds)
    const ANALYSIS_TIMEOUT = 8000;
    
    const analysisPromise = (async () => {
      let score = 50; // Starting baseline
      const breakdown = {
        ssl_security: 0,
        domain_authority: 0,
        policy_transparency: 0,
        reputation_signals: 0
      };

      try {
        const url = new URL(urlStr.startsWith('http') ? urlStr : `https://${urlStr}`);
        const hostname = url.hostname.toLowerCase();
        
        console.log(`[AuthIQ Debug] START ANALYZING: ${urlStr} (Host: ${hostname})`);

        // Simulate a small "processing" delay for realistic deep-scan feel
        await new Promise(resolve => setTimeout(resolve, 800));

        // 1. SSL/TLS Signal (Heuristic)
        if (url.protocol === 'https:') {
          breakdown.ssl_security = 95;
          score += 20;
        } else {
          breakdown.ssl_security = 10;
          score -= 30;
        }

        // 2. Domain Authority & Age Signals
        const tld = hostname.split('.').pop();
        const trustedTlds = ['com', 'org', 'net', 'edu', 'gov', 'in'];
        const suspiciousTlds = ['xyz', 'biz', 'top', 'win', 'click', 'icu'];

        if (trustedTlds.includes(tld || '')) {
          breakdown.domain_authority = 85;
          score += 10;
        } else if (suspiciousTlds.includes(tld || '')) {
          breakdown.domain_authority = 30;
          score -= 20;
        } else {
          breakdown.domain_authority = 60;
        }

        // Length and Hyphens
        if (hostname.length > 25) score -= 10;
        if ((hostname.match(/-/g) || []).length > 2) score -= 15;

        // 3. Reputation & Scam Database
        if (SCAM_DATABASE.some(scam => hostname.includes(scam))) {
          breakdown.reputation_signals = 5;
          score = 15; // Hard drop for known scams
        } else {
          const suspiciousKeywords = ['cheap', 'free', 'discount', 'deal', 'win', 'offer', 'gift'];
          const matches = suspiciousKeywords.filter(k => hostname.includes(k));
          if (matches.length > 0) {
            breakdown.reputation_signals = 40;
            score -= (matches.length * 10);
          } else {
            breakdown.reputation_signals = 90;
            score += 5;
          }
        }

        // 4. Policy/Metadata Heuristic
        breakdown.policy_transparency = hostname.length < 15 ? 85 : 65;

        // Normalize score
        score = Math.max(0, Math.min(100, score));

        console.log(`[AuthIQ Debug] COMPLETED ANALYSIS: ${urlStr} -> Score: ${score}`);

        return {
          url: urlStr,
          dcti_score: score,
          risk_level: score > 75 ? "LOW" : score > 40 ? "MEDIUM" : "HIGH",
          breakdown,
          scanned_at: new Date().toISOString()
        };
      } catch (error) {
        console.error(`[AuthIQ Error] Scoring failed for ${urlStr}:`, error);
        throw new Error("Invalid URL or domain unreachable");
      }
    })();

    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error("Analysis timed out. The domain is taking too long to respond.")), ANALYSIS_TIMEOUT);
    });

    return Promise.race([analysisPromise, timeoutPromise]);
  };

  // API routes FIRST
  app.get("/api/health", (req, res) => {
    res.json({ status: "ok", time: new Date().toISOString() });
  });

  // API Route: Trust Score
  app.get("/api/trust", async (req, res) => {
    const { url } = req.query;
    
    if (!url || typeof url !== 'string') {
      return res.status(400).json({ status: "error", message: "URL parameter is required" });
    }

    try {
      const result = await calculateTrustScore(url);
      res.json({
        status: "success",
        data: result
      });
    } catch (err: any) {
      res.status(422).json({ status: "error", message: err.message });
    }
  });

  // API Route: Report Scam (Mock)
  app.post("/api/report-scam", (req, res) => {
    const report = req.body;
    console.log("[AuthIQ Debug] New Scam Report Received:", report);
    SCAM_DATABASE.push(new URL(report.domain.startsWith('http') ? report.domain : `https://${report.domain}`).hostname);
    res.json({ status: "success", message: "Report processed and database updated" });
  });

  // Vite middle-ware setup
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  const server = httpServer.listen(PORT, "0.0.0.0", () => {
    console.log(`AuthIQ Server running on http://localhost:${PORT}`);
  });

  server.on("error", (err) => {
    console.error("Express server error:", err);
  });
}

startServer().catch((err) => {
  console.error("Failed to start server:", err);
  process.exit(1);
});
