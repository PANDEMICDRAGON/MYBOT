# 🛰️ 24/7 Autonomous Weather, News & Cybersecurity Telemetry Command

A resilient, continuous pipeline that gathers **local & global weather**, **breaking news**, and **cybersecurity threat intelligence** (CISA Known Exploited Vulnerabilities, The Hacker News, BleepingComputer, KE-CIRT), pushes instant alerts to your phone via **Telegram Long Polling**, and renders live telemetry on a glassmorphic **Vercel Web Dashboard**.

---

## 🏛️ System Architecture

```mermaid
graph TD
    subgraph Data Feeds (Keyless)
        Meteo[Open-Meteo API<br/>Weather & Atmospheric] -->|JSON| Bot[bot.py Daemon<br/>24/7 Long Polling]
        CISA[CISA KEV Catalog<br/>Active Zero-Days & CVEs] -->|JSON| Bot
        Feeds[News & Threat RSS Feeds<br/>BBC, Al Jazeera, Hacker News, BleepingComputer, KE-CIRT] -->|XML| Bot
    end

    subgraph Storage & Deduplication
        Bot -->|Upsert Weather| DB[(Supabase PostgreSQL)]
        Bot -->|SHA-256 Deduplicate & Store| DB
    end

    subgraph Two-Way Delivery & Viewing
        Bot -->|Instant Alerts & Commands| Phone[📱 Telegram App on Phone]
        DB -->|Public Read-Only anon RLS| Web[🌐 Vercel Web Dashboard<br/>index.html]
        Web --> Phone
    end
```

### Integrated Feeds:
1. **Weather Engine**: Open-Meteo API (Kitengela, Nairobi, London, New York, Tokyo) — no API keys required.
2. **Cybersecurity Engine**:
   - **CISA KEV Catalog JSON**: Actively exploited vulnerabilities and ransomware zero-days flagged as `CRITICAL` or `HIGH`.
   - **The Hacker News & BleepingComputer**: Global breach disclosures, zero-days, and malware analysis.
   - **Kenya Cyber Monitor**: Local cyber telemetry and KE-CIRT alerts.
3. **News Engine**: Google News Kenya, BBC World, and Al Jazeera via structured XML feeds with SHA-256 hash deduplication.
4. **Telegram Bot**: Long-polling commands (`/cyber`, `/weather`, `/local`, `/global`, `/sync`, `/status`).
5. **Vercel Web Dashboard**: Dark obsidian glassmorphic dashboard with live weather cards, active CVE threat matrix, news dispatch, and real-time unified search.

---

## 📁 Repository Structure

```
MYBOT/
├── bot.py                    # 24/7 Weather, News & Cyber telemetry bot daemon
├── core_bot.py               # General custom web collector bot (any CSS selector)
├── test_cyber_telemetry.py   # Test script for CISA KEV JSON & Cyber RSS feeds
├── test_weather_news.py      # Test script for Open-Meteo & News RSS feeds
├── schema.sql                # Supabase PostgreSQL schema with RLS policies
├── .env.example              # Environment variables template
├── vercel.json               # Vercel deployment configuration
├── index.html                # Telemetry Command Web Dashboard
├── style.css                 # Cyber-telemetry CSS design system
├── app.js                    # Frontend data engine, filtering & settings modal
└── requirements.txt          # Python dependencies (httpx, beautifulsoup4, python-dotenv)
```

---

## ⚡ Quick Setup & Launch

### 1. Database Setup (Supabase)
1. In your [Supabase Dashboard](https://supabase.com), open the **SQL Editor** -> **New Query**.
2. Run the queries from [`schema.sql`](schema.sql) to create `weather_reports`, `news_articles`, and `cyber_alerts` with public read-only RLS policies.
3. Go to **Project Settings** -> **API**:
   - Copy **Project URL** -> `SUPABASE_URL`
   - Copy **service_role secret key** -> `SUPABASE_KEY` (Used strictly by the Python bot)
   - Copy **anon public key** -> `SUPABASE_ANON_KEY` (Used by the Vercel web dashboard)

---

### 2. Telegram Bot Setup
1. Message [@BotFather](https://t.me/BotFather) on Telegram and run `/newbot` to get your `TELEGRAM_TOKEN`.
2. Message [@userinfobot](https://t.me/userinfobot) to get your numeric `TELEGRAM_CHAT_ID`.
3. Send `/start` to your new bot once to initialize the chat.

---

### 3. Local Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Update `.env` with your credentials:
```env
TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_CHAT_ID=123456789
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_secret
SUPABASE_ANON_KEY=your_supabase_anon_public_key
SYNC_INTERVAL=900
```

---

### 4. Test Feeds Offline
Verify that your system can fetch live data without credentials:
```powershell
# Test Weather & News
.\.venv\Scripts\python test_weather_news.py

# Test CISA KEV & Cyber Threat Intelligence
.\.venv\Scripts\python test_cyber_telemetry.py
```

---

### 5. Launch the 24/7 Bot
Start the background daemon:
```powershell
.\.venv\Scripts\python bot.py
```
Your Telegram bot will send you an online ping!
You can query your bot anytime using:
- `/cyber` — Latest actively exploited CVEs and threat intelligence
- `/weather` — Real-time weather snapshot across all cities
- `/local` — Top 5 latest Kenya news headlines
- `/global` — Top 5 latest world news headlines
- `/sync` — Trigger an immediate sync across all feeds
- `/status` — View uptime and database record counts

---

## 🌐 Deploy Web Dashboard to Vercel

### Option A: Via GitHub (Recommended)
1. Push this repository to GitHub:
   ```powershell
   git add .
   git commit -m "Add Cybersecurity threat matrix & CISA KEV integration"
   git push
   ```
2. Open [vercel.com](https://vercel.com) and click **Add New Project**.
3. Select your repository and click **Deploy**. Vercel will immediately deploy [`index.html`](index.html) and give you a free HTTPS URL (e.g. `https://mybot.vercel.app`).

### Option B: Deploy via Vercel CLI
```powershell
npx -y vercel
```

### Connect Dashboard to Supabase:
1. Open your live Vercel site in any browser.
2. Click the **Settings (⚙️)** button in the top navigation bar.
3. Enter your **Supabase URL** and **Anon Public Key**.
4. Click **Save & Connect**. Your credentials will be saved in your browser's `localStorage`, linking your dashboard directly to your live Supabase database!
