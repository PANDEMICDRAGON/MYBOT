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
| **Wi-Fi Cyber Scanner** | Async Socket & Banner Fingerprint | Dedicated multi-port scanner auditing 20-35 services on Wi-Fi devices (Google Cast, Roku, ADB, HTTP, SSH) across mobile and desktop. |
| **High-Tech Typography Matrix** | Google Fonts + CSS Engine | Replaces cramped legacy fonts with movie-grade Oxanium display headers, Plus Jakarta Sans & Inter hyper-crisp body text, Space Grotesk HUD labels, JetBrains Mono telemetry, and an interactive 6-preset selector (Quantum, Stark, Cortana, Minimalist, Night City, Retro). |

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
SYNC_INTERVAL=300
TELEGRAM_DISPATCH_INTERVAL=1800
```

---

```powershell
.\.venv\Scripts\python setup_phone.py
```
This utility validates your Telegram credentials and sends an instant test ping to your phone.

### 6. Launch the 24/7 Autonomous Daemon
Run the cognitive engine:
```powershell
.\.venv\Scripts\python bot.py
```
Your phone will receive an initialization ping:
> `Tactical Intelligence Construct Online. Kinetic War, Macro-Economic Shocks & Protective Protocols active.`

---

## 💬 How to Interact With Cortana / J.A.R.V.I.S.

You don't need rigid commands anymore; talk or speak naturally via Telegram:

- **On-Demand Intelligence Updates ("when I ask")**:
  - *"Give me an update"* / *"SitRep"* / *"Briefing"* / *"Latest update"* / *"What's happening"* -> Instantly returns the full, high-fidelity tactical intelligence briefing on demand, resetting the 30-minute broadcast timer.
- **Disciplined Broadcast Cadence**:
  - Routine proactive SitReps to Telegram are strictly rate-limited to **after 30 minutes** (`TELEGRAM_DISPATCH_INTERVAL=1800`). Continuous sensor sweeps (every 5 mins) silently refresh Supabase and the live Web HUD without cluttering your phone.
- **Deep OSINT & Human Profiling**: *"Investigate Alex Vance—we have a meeting tomorrow regarding a software partnership."*  
  -> *Sweeps LinkedIn, X, GitHub, Reddit, Kenya business filings & PDFs concurrently. Computes psychological drivers, cognitive biases, and gives 3 negotiation anchors.*
- **Crowd Psychology & Sentiment Analysis**: *"Analyze crowd psychology right now around NSE banking stocks and interest rate sentiment."*  
  -> *Scans Reddit, HN, X dorks, and financial media to diagnose FOMO vs. capitulation and compute contrarian positioning.*
- **Geospatial Reconnaissance**: *"Run a deep dive on Kitengela Commercial Corridor and its strategic value."*  
  -> *Queries OpenStreetMap Nominatim, local infrastructure data, and economic drivers.*
- **Negotiation & Message Deconstruction**: *"Why is this person acting defensive in these messages? [Forwarded text]"*  
  -> *Cross-references against behavioral psychology & negotiation doctrine in `bot_memory`, decoding status drivers and crafting frame-control responses.*
- **War & Macro Query**: *"Give me the latest Red Sea war impact on Kenya shipping and how to position my NSE portfolio."*  
  -> *Queries live `conflict_and_macro_intel` and synthesizes defensive & asymmetric financial maneuvers.*
- **Voice Memo**: Hold the mic and say: *"Remind me to push the Docker containers tomorrow at 10 AM EAT."*  
  -> *Transcribed via Whisper, calculates timestamp, schedules task in database, and notifies you when due.*
- **Two-Way Voice Dialogue**: Speak to the bot via voice note. Cortana will think, execute commands, reply in text, AND send a neural voice note (`en-US-AriaNeural`) straight back to your Telegram chat while optionally vocalizing through your room speakers.
- **Smart TV Control**: *"Turn on the Living Room TV and put YouTube on."*  
  -> *Sends Wake-on-LAN packet, connects via wireless ADB (`adb connect <ip>:5555`), and launches the URL or powers on the screen.*
- **Nearby Wi-Fi Reconnaissance & RF Spectrum Scan**:
  - *"Scan nearby wifis"* / *"View nearby wifis"* / *"Show available wifi networks"* -> Performs an in-flight RF sweep across 2.4 GHz, 5 GHz and 6 GHz bands. Returns a formatted tactical matrix detailing visible SSIDs, signal percentages, signal bars, channels, radio types (802.11ax/ac/n), and security standards (WPA2-Personal/WPA3/Open).
- **Authenticated Wi-Fi Association**:
  - *"Connect to wifi Olalo-5G with password 2011@Olalo"* or *"Connect wifi \"MyNetwork\" \"secretKey\""* -> Dynamically generates a native Windows WLAN XML profile conforming to Microsoft networking schemas, associates the interface, verifies 4-way WPA handshake completion, and purges temporary credential artifacts.
  - *"What wifi am I connected to?"* / *"Wifi status"* -> Retrieves live adapter telemetry including connected SSID, BSSID, RSSI/Signal %, radio channel, and Rx/Tx data link rates.
  - *"Disconnect wifi"* -> Gracefully unbinds the active WLAN interface.
- **Wi-Fi Network Device Sweep**: *"Scan my Wi-Fi network and tell me what gadgets are connected."*  
  -> *Sweeps the local ARP cache table, detects all connected TVs, laptops, and IoT nodes, and synchronizes their online status with Supabase.*
- **Laptop Operational Control (Speech, Chrome & Hardware)**:
  - *"Speak: Protocol activated and standing by."* -> Vocalizes directly through your laptop's physical speakers via Windows SAPI / System TTS.
  - *"Open Chrome"* or *"Open Chrome https://youtube.com"* -> Launches Google Chrome browser or navigates directly to a target destination.
  - *"Close Chrome"* -> Immediately terminates and force-kills all running Chrome browser processes cleanly.
  - *"Turn up laptop volume"* / *"Volume down"* / *"Mute laptop"* -> Adjusts workstation master volume level.
  - *"Lock laptop"* -> Locks the Windows workstation screen instantly.
- **Laptop & PC Automation**: *"Wake up my laptop and open the tactical HUD."*  
  -> *Transmits WoL magic packet to the PC's MAC address and launches the command.*
- **Receipt / M-Pesa Photo**: Send a photo of a restaurant receipt or M-Pesa screenshot.  
  -> *Vision model extracts merchant name, amount, date, reference code, and logs it to your ledger.*
- **Tactical Query**: *"Cortana, are any active CVEs impacting PostgreSQL or Linux right now?"*  
  -> *Executes `query_telemetry` tool call and responds with strategic impact assessment.*
- **Web Inspection**: *"Check the status page at https://example.com and summarize any outages."*  
  -> *Executes `live_web_probe` tool call and provides instant tactical synopsis.*
- **Idea Logging**: *"Log a project idea: Decentralized voice mesh using libp2p."*  
  -> *Executes `log_vault_note` and stores in your Idea Vault.*

---

## 🎙️ Two-Way Natural Voice & Ambient Room Listener

### 1. Cortana Halo Persona & Neural TTS Voice
The construct uses Microsoft's Neural Speech engine (`edge-tts`) with zero API keys and zero subscriptions required:
- **Default Voice**: `en-US-AriaNeural` (Halo Cortana persona: calm tactical authority, razor-sharp intellect, protective cadence).
- **Alternative Style**: `en-GB-RyanNeural` (British J.A.R.V.I.S. cadence).
- Every response generated by Cortana is synthesized into high-fidelity neural audio, pushed back as an instant playable voice note to Telegram (`sendVoice`), and played through host speakers when enabled.

### 2. Ambient Room Wake-Word Listener ("Cortana" / "Jarvis")
Run the bot with the `--wake` flag or set `ENABLE_WAKEWORD=true` in your `.env`:
```powershell
.\.venv\Scripts\python bot.py --wake --speak
```
When Cortana hears **"Cortana"** or **"Jarvis"** spoken out loud in your room, it transcribes your speech via Groq Whisper (`whisper-large-v3-turbo`) in ~250ms, executes your directive, and answers aloud over your room/laptop speakers.

### 3. Direct System-Level Audio Driver & Terminal TTS Bridge (`speak.py`)
Direct COM hook into your laptop's physical sound card (via in-process `win32com` SAPI and `edge-tts` Cortana neural engine):
1. **Direct Terminal Vocalization**:
   ```powershell
   .\.venv\Scripts\python speak.py "Construct operational. Standing by for directives, Michael."
   ```
2. **Piped STDIN (Pipe ANY CLI output straight into laptop speakers)**:
   ```powershell
   git status | .\.venv\Scripts\python speak.py
   Write-Output "Perimeter scan complete. Defensive posture green." | .\.venv\Scripts\python speak.py
   ```
3. **Interactive Voice REPL**:
   ```powershell
   .\.venv\Scripts\python speak.py --interactive
   ```
4. **Python Module Import**:
   ```python
   from speak import speak, speak_async
   speak("Audio driver online and hooked directly into sound card.")
   ```


---

## 📡 RF Spectrum Wi-Fi Reconnaissance & Authenticated Connection (`wifi_manager.py`)

The construct includes a dedicated physical-layer 802.11 Wi-Fi management subsystem capable of in-flight radio frequency reconnaissance, cryptographic profile synthesis, and association handshakes:

### 1. In-Flight Spectrum Scanning
- Queries physical WLAN adapters via native `netsh wlan show networks mode=bssid`.
- De-duplicates and parses multi-BSSID mesh beacons, radio spectrum bands (2.4 GHz vs 5 GHz vs 6 GHz), RF channels, encryption algorithms (CCMP/TKIP/GCMP), and signal RSSI percentages.
- Computes tactical visual indicators: `🟢 Connected`, `🔒 Secured`, `🔓 Open`, plus 4-stage signal strength bars (`📶 4/4 Excellent`, `3/4 Good`, `2/4 Fair`, `1/4 Weak`).

### 2. Authenticated Association & Handshake Verification
- Synthesizes dynamic Microsoft WLAN profile XML schemas (`http://www.microsoft.com/networking/WLAN/profile/v1`) with tailored `WPA2PSK` / `WPA3` / `Open` key material.
- Injects profile into Windows WLAN service via `netsh wlan add profile`.
- Initiates association handshake with 20-second state polling loop to verify the 4-way WPA cryptographic exchange.
- Automatically and securely deletes temporary XML profile artifacts from disk immediately upon registration.

### 3. CLI Command Suite
```powershell
# In-flight spectrum scan (prints formatted ASCII tactical matrix)
.\.venv\Scripts\python wifi_manager.py scan

# Check active link status, BSSID, RSSI %, band & link rates
.\.venv\Scripts\python wifi_manager.py status

# Associate to target network with passphrase
.\.venv\Scripts\python wifi_manager.py connect "Olalo-5G" "2011@Olalo"

# Disconnect WLAN interface
.\.venv\Scripts\python wifi_manager.py disconnect
```

### 4. Live Cyber HUD Modal (`#wifi-scanner-modal`)
- **Radar Laser Sweep Animation**: High-tech visual scanner overlay when refreshing spectrum.
- **Active Connection Card**: Real-time connected SSID, band, signal badge, and link status.
- **One-Click Connect Drawer**: Click any discovered network to pop up the association drawer, enter the password (with instant show/hide toggle), and trigger authenticated connection in real time.
- **Quick Access**: Triggered directly via `📡 Scan Nearby Wi-Fi` or `🔑 Connect Wi-Fi` terminal chips or the Device Inspector action matrix.

---

## 📺 Local Wi-Fi & Smart TV Command Matrix

### 60-Second Setup for Smart TVs & Laptops:
1. **Android TV / Google TV / Sony / TCL / Hisense / Fire TV**:
   - Go to TV **Settings -> Device Preferences -> About** -> click **Build** 7 times to enable Developer Options.
   - Turn on **Network Debugging / Wireless ADB**.
   - Note the TV's IP (e.g. `192.168.1.105`).
   - Tell Cortana on Telegram or Web HUD:  
     *"Register my Living Room TV as an Android TV at 192.168.1.105."*
2. **Roku TV**:
   - Note the Roku TV's IP. Cortana commands it via native ECP HTTP REST on port `8060` (power, mute, volume, home).
3. **Laptops & PCs**:
   - Enable Wake-on-LAN (WoL) in BIOS/adapter properties.
   - Tell Cortana:  
     *"Register my Main Laptop as a LAPTOP-PC at 192.168.1.10 with MAC AA:BB:CC:DD:EE:FF."*

---

## 🌐 Live Web Command HUD (Vercel)

Production URL: **[https://telemetry-news-weather.vercel.app](https://telemetry-news-weather.vercel.app)**

To deploy updates directly from PowerShell:
```powershell
npx vercel --prod --yes
```

On your live Vercel site:
1. Click **Settings (⚙️)** in the top navigation bar.
2. Enter your **Supabase URL** and **Anon Public Key**.
3. Click **Save & Connect HUD**.
4. Click **VOICE COMM (MIC)** to speak directly to Cortana through your browser with real-time speech recognition!
5. Click **VOCALIZE SITREP** to hear Cortana read the complete strategic briefing aloud.
6. Monitor the **Local Wi-Fi & LAN Device Mesh** grid for live device statuses, IP/MAC addresses, and one-click hardware controls.


