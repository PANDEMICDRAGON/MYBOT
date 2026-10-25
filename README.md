# 🛰️ 24/7 Cortana & J.A.R.V.I.S. Cognitive Telemetry Construct

An autonomous tactical intelligence construct combining the strategic threat synthesis of **Cortana (HALO)** and the dry operational precision, multimodal voice/vision execution, and persistent memory of **J.A.R.V.I.S. (Iron Man)**.

Runs 24/7 with **zero VPS and zero paid domain requirements** using Telegram Long Polling, Groq LLM/Whisper/Vision inference, Supabase PostgreSQL episodic memory, and a glassmorphic **Vercel Vocal HUD**.

---

## 🏛️ Cognitive System Architecture

```mermaid
graph TD
    subgraph Operator Inputs
        Voice[🎙️ Telegram Voice Notes] --> Poller[bot.py Cognitive Engine]
        Photos[📸 Telegram Receipt / Ticket Photos] --> Poller
        Text[💬 Natural Language Directives] --> Poller
    end

    subgraph Sensory Telemetry (Keyless)
        Meteo[Open-Meteo Atmospheric Sensors] --> Poller
        CISA[CISA KEV Exploit Catalog] --> Poller
        Feeds[News & Threat Intelligence Feeds] --> Poller
    end

    subgraph Brain & Tool-Calling (ReAct Pattern)
        Poller <-->|llama-3.3-70b-versatile| Groq[Groq AI Cloud]
        Poller <-->|whisper-large-v3-turbo| Groq
        Poller <-->|Vision OCR| Groq
    end

    subgraph Persistent Memory & Operations
        Poller <-->|Operator Directives & Tech Stack| DB[(Supabase PostgreSQL)]
        Poller -->|Tasks & Deadlines| DB
        Poller -->|M-Pesa / Receipt Ledger| DB
        Poller -->|Voice-to-Action Vault| DB
        Poller -->|Tactical SitReps| DB
    end

    subgraph Real-Time Display & Vocal HUD
        DB -->|Public Read-Only anon RLS| Web[🌐 Vercel Web Dashboard<br/>index.html]
        Web -->|Web Speech API Vocalization| Speaker[🔊 Vocal SitRep Audio]
    end
```

---

## 🧠 Autonomous Core Capabilities

| Capability | Model / Engine | Description |
| :--- | :--- | :--- |
| **Tactical Persona** | `llama-3.3-70b-versatile` | Cortana threat synthesis + J.A.R.V.I.S. operational precision. No fluff, no emojis. |
| **Voice Directives** | `whisper-large-v3-turbo` | Speak to your bot on Telegram; transcribes at 228x real-time speed and executes tool loops. |
| **Vision OCR** | `llama-3.2-11b-vision` | Send photos of paper receipts, invoices, or tickets to automatically parse M-Pesa / amount / dates. |
| **Episodic Memory** | `bot_memory` table | Stores standing orders and your tech stack, cross-referencing incoming CVEs against your environment. |
| **Deadlines & Reminders** | `check_due_tasks` loop | Automatically tracks deadlines and pushes alert pings to your phone when tasks are due. |
| **Personal Ledger** | `personal_ledger` table | Automatically organizes M-Pesa statements, merchant receipts, and income into an indexed ledger. |
| **Voice Idea Vault** | `idea_vault` table | Instant spoken logging for code snippets, song lyrics, or project architectures. |
| **Vocal Web HUD** | `window.speechSynthesis` | Web dashboard that reads newly synthesized SitRep briefings aloud with one click. |

---

## 📁 Repository Structure

```
MYBOT/
├── bot.py                    # 24/7 Cortana / J.A.R.V.I.S. cognitive daemon & tool executor
├── core_bot.py               # Baseline custom web collector bot
├── test_cyber_telemetry.py   # Test utility for CISA KEV JSON & Threat feeds
├── test_weather_news.py      # Test utility for Open-Meteo & RSS feeds
├── schema.sql                # Supabase schema (Memory, SitReps, Tasks, Ledger, Vault, RLS)
├── .env.example              # Environment variables template (Telegram, Supabase, Groq)
├── vercel.json               # Vercel deployment configuration
├── index.html                # Cognitive Command HUD (Vocalizer + Ops Matrix + Telemetry)
├── style.css                 # Cyber-telemetry CSS design system
├── app.js                    # Frontend data engine, Web Speech API & settings modal
└── requirements.txt          # Python dependencies
```

---

## ⚡ Quick Setup & Launch

### 1. Database Setup (Supabase)
1. Open your [Supabase Dashboard](https://supabase.com) -> **SQL Editor** -> **New Query**.
2. Run the queries from [`schema.sql`](schema.sql) to provision all tables (`bot_memory`, `tactical_briefings`, `personal_tasks`, `personal_ledger`, `idea_vault`, `weather_reports`, `news_articles`, `cyber_alerts`) and public RLS policies.
3. Under **Project Settings -> API**, copy:
   - **Project URL** (`SUPABASE_URL`)
   - **service_role key** (`SUPABASE_KEY` for Python bot)
   - **anon key** (`SUPABASE_ANON_KEY` for Vercel Web HUD)

---

### 2. Groq AI API Key (Free)
1. Navigate to [console.groq.com](https://console.groq.com) and create a free account.
2. Generate an API Key -> `GROQ_API_KEY`.

---

### 3. Telegram Bot Setup
1. Message [@BotFather](https://t.me/BotFather) on Telegram and run `/newbot` to get your `TELEGRAM_TOKEN`.
2. Message [@userinfobot](https://t.me/userinfobot) to get your numeric `TELEGRAM_CHAT_ID`.
3. Send `/start` to your new bot once to initialize the session.

---

### 4. Configure Local `.env`
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
GROQ_API_KEY=gsk_your_groq_api_key_here
SYNC_INTERVAL=900
```

---

### 5. Launch the Autonomous Construct
Run the daemon:
```powershell
.\.venv\Scripts\python bot.py
```
Your phone will receive an initialization ping:
> `Tactical Intelligence Construct Online. Awaiting natural language or voice directives.`

---

## 💬 How to Interact With Cortana / J.A.R.V.I.S.

You don't need rigid commands anymore; talk or speak naturally via Telegram:

- **Voice Memo**: Hold the mic and say: *"Remind me to push the Docker containers tomorrow at 10 AM EAT."*  
  -> *Transcribed via Whisper, calculates timestamp, schedules task in database, and notifies you when due.*
- **Receipt / M-Pesa Photo**: Send a photo of a restaurant receipt or M-Pesa screenshot.  
  -> *Vision model extracts merchant name, amount, date, reference code, and logs it to your ledger.*
- **Tactical Query**: *"Cortana, are any active CVEs impacting PostgreSQL or Linux right now?"*  
  -> *Executes `query_telemetry` tool call and responds with strategic impact assessment.*
- **Web Inspection**: *"Check the status page at https://example.com and summarize any outages."*  
  -> *Executes `live_web_probe` tool call and provides instant tactical synopsis.*
- **Idea Logging**: *"Log a project idea: Decentralized voice mesh using libp2p."*  
  -> *Executes `log_vault_note` and stores in your Idea Vault.*

---

## 🌐 Deploy Web Dashboard to Vercel

```powershell
git add .
git commit -m "Deploy Cortana / J.A.R.V.I.S. Cognitive Command HUD"
git push
```
Connect your GitHub repository to [Vercel](https://vercel.com) for instant deployment.

On your live Vercel site:
1. Click **Settings (⚙️)** in the top navigation bar.
2. Enter your **Supabase URL** and **Anon Public Key**.
3. Click **Save & Connect HUD**.
4. Click **VOCALIZE SITREP** to hear the AI briefing spoken aloud!
