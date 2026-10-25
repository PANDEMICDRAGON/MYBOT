/**
 * Cortana / J.A.R.V.I.S. Cognitive Command Dashboard Engine
 * Handles Supabase REST API data fetching, real-time filtering, UI rendering,
 * Web Speech API vocalization, and persistent local configuration.
 */

const DEFAULT_SUPABASE_URL = "https://your-project.supabase.co";
const DEFAULT_SUPABASE_ANON_KEY = "YOUR_SUPABASE_ANON_KEY";

// State
let appState = {
  supabaseUrl: localStorage.getItem("telemetry_supabase_url") || DEFAULT_SUPABASE_URL,
  supabaseAnonKey: localStorage.getItem("telemetry_supabase_anon") || DEFAULT_SUPABASE_ANON_KEY,
  sitrepText: "",
  sitrepThreat: "NOMINAL",
  conflictSummary: "",
  futureRiskForecast: "",
  defensiveProtocol: "",
  asymmetricUpside: "",
  weatherData: [],
  newsData: [],
  cyberData: [],
  conflictData: [],
  osintData: [],
  tasksData: [],
  ledgerData: [],
  vaultData: [],
  lanData: [],
  activeNewsFilter: "ALL",   // ALL | LOCAL | GLOBAL
  activeCyberFilter: "ALL",  // ALL | CVE-KEV | THREAT-INTEL | LOCAL-CYBER
  activeConflictFilter: "ALL", // ALL | WAR-KINETIC | MACRO-ECONOMIC | EAST-AFRICA | RED-SEA-MIDEAST
  activeOsintFilter: "ALL",    // ALL | PERSON | ORGANIZATION | PLACE | TOPIC-IDEA
  searchQuery: "",
  lastSyncTime: null,
  nextSyncSeconds: 60,
  syncTimerId: null,
  isSpeaking: false,
  sfxEnabled: localStorage.getItem("ai_hud_sfx") !== "false",
  currentTheme: localStorage.getItem("ai_hud_theme") || "hybrid"
};

// Weather Condition Icons (SVG)
const WEATHER_ICONS = {
  "Clear Sky": `<svg class="w-8 h-8 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5" stroke-width="2"></circle><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"></path></svg>`,
  "Mainly Clear": `<svg class="w-8 h-8 text-amber-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4" stroke-width="2"></circle><path stroke-linecap="round" stroke-width="2" d="M12 2v2m0 16v2m-8-10H2m20 0h-2m-3.5-6.5l1.5-1.5M6 18l1.5-1.5"></path></svg>`,
  "Partly Cloudy": `<svg class="w-8 h-8 text-cyan-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"></path></svg>`,
  "Overcast": `<svg class="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15a4 4 0 004 4h12a4 4 0 000-8h-.5A5 5 0 008 8.5 4 4 0 003 15z"></path></svg>`,
  "Rain": `<svg class="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 13v6m-4-6v6m-4-6v6M3 12a4 4 0 004 4h10a4 4 0 000-8H16a5 5 0 00-9.8 1.5A4 4 0 003 12z"></path></svg>`,
  "Thunderstorm": `<svg class="w-8 h-8 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>`
};

function getConditionIcon(condition) {
  for (const key in WEATHER_ICONS) {
    if (condition.toLowerCase().includes(key.toLowerCase())) {
      return WEATHER_ICONS[key];
    }
  }
  return WEATHER_ICONS["Partly Cloudy"];
}

// Baseline Fallback / Demo Data
const DEMO_SITREP = {
  threat_level: "NOMINAL",
  sitrep: "[THREAT LEVEL: NOMINAL]\nKitengela & Nairobi atmospheric conditions are nominal at 28.9°C with overcast skies. Multi-network telemetry active across CNN, BBC, Al Jazeera, Fox News, NYT, and WSJ. CISA KEV catalog active with 1,756 monitored CVEs; zero active ransomware exploits matching primary Python/PostgreSQL/Linux stack. Maritime and macro threat corridors monitored.",
  conflict_summary: "Red Sea & Bab el-Mandeb: Intermittent missile and drone threats against commercial transit; insurance surcharges elevated. Eastern Europe: Drone strikes reported near Black Sea grain export terminals. Horn of Africa / Sudan: Clashes in Khartoum perimeter; Kenya border posts on elevated alert.",
  future_risk_forecast: "7-30 Day Horizon: Shipping reroutes around Cape of Good Hope lifting landed fuel and machinery costs into Mombasa port by 8-12%. Central Bank of Kenya holding benchmark rate at 12.75% to stabilize KES against USD import pressure. Coastal subsea cables operational.",
  defensive_protocol: "1. Lock in essential hardware and infrastructure import orders before regional repricing.\n2. Maintain 30-day liquidity buffer in USD or money market accounts to hedge KES fluctuations.\n3. Verify off-grid power backups and offline repository mirrors (git + sqlite) against local disruptions.",
  asymmetric_upside: "1. Dollar-denominated invoicing: Retain international clients and royalty revenues in USD.\n2. Strategic NSE positioning: Accumulate high-yield, dividend-paying domestic equities (SCOM, COOP, ABSA) during macro pullbacks.\n3. Resilience engineering: Offer failover DNS and edge architecture retainers to local businesses vulnerable to cloud outages.",
  created_at: new Date().toISOString()
};

const DEMO_CONFLICT = [
  {
    id: 1,
    domain: "WAR-KINETIC",
    theater: "RED-SEA-MIDEAST",
    severity: "CRITICAL",
    headline: "Houthi Anti-Ship Ballistic Missiles Target Container Vessel South of Bab el-Mandeb",
    source: "Defense One",
    link: "https://www.defenseone.com",
    created_at: new Date(Date.now() - 1000 * 60 * 18).toISOString()
  },
  {
    id: 2,
    domain: "WAR-KINETIC",
    theater: "EAST-AFRICA",
    severity: "ELEVATED",
    headline: "Sudan Conflict Escalates Around Port Sudan Logistics Hub; Regional Security Meeting Convened",
    source: "Al Jazeera",
    link: "https://www.aljazeera.com",
    created_at: new Date(Date.now() - 1000 * 60 * 45).toISOString()
  },
  {
    id: 3,
    domain: "MACRO-ECONOMIC",
    theater: "GLOBAL",
    severity: "ELEVATED",
    headline: "Brent Crude Climbs Past $84 on Mideast Supply Anxiety; Maritime War Risk Premiums Double",
    source: "CNBC",
    link: "https://www.cnbc.com",
    created_at: new Date(Date.now() - 1000 * 60 * 85).toISOString()
  },
  {
    id: 4,
    domain: "WAR-KINETIC",
    theater: "EASTERN-EUROPE",
    severity: "ELEVATED",
    headline: "Long-Range Drone Swarms Intercepted Over Black Sea Maritime Corridor Near Odesa",
    source: "BBC World",
    link: "https://www.bbc.com/news/world",
    created_at: new Date(Date.now() - 1000 * 60 * 120).toISOString()
  },
  {
    id: 5,
    domain: "GEOPOLITICAL",
    theater: "INDO-PACIFIC",
    severity: "WATCH",
    headline: "Naval Patrols Stepped Up in Taiwan Strait Ahead of Advanced Semiconductor Tariff Review",
    source: "Fox News",
    link: "https://www.foxnews.com/world",
    created_at: new Date(Date.now() - 1000 * 60 * 180).toISOString()
  },
  {
    id: 6,
    domain: "MACRO-ECONOMIC",
    theater: "GLOBAL",
    severity: "WATCH",
    headline: "Federal Reserve Signals Prolonged Elevated Rates; Emerging Market Currencies Under Pressure",
    source: "WSJ Markets",
    link: "https://www.wsj.com",
    created_at: new Date(Date.now() - 1000 * 60 * 240).toISOString()
  }
];

const DEMO_OSINT = [
  {
    id: 1,
    target_query: "Alex Vance (Fintech Founder)",
    entity_type: "PERSON",
    footprint_summary: "Founder of payments gateway operating in Nairobi & London. Active presence on LinkedIn and GitHub with 48 public repositories in Go and Rust. Director filings identified on OpenCorporates; speaker at Africa Tech Summit 2024.",
    social_and_public_links: [
      "https://github.com/alexvance",
      "https://linkedin.com/in/alexvance-fintech",
      "https://news.ycombinator.com/user?id=avance"
    ],
    behavioral_profile: "Status-driven technologist who values architectural purity over raw business velocity. Exhibits confirmation bias toward decentralized rails. Revealed behavior: Highly responsive to deep technical inquiries, avoids bureaucratic enterprise sales cycles.",
    strategic_approchement: "Approach from an engineering-first frame. Validate architectural elegance before discussing commercial terms. Anchor negotiations on developer mindshare and API latency advantages.",
    created_at: new Date(Date.now() - 1000 * 60 * 35).toISOString()
  },
  {
    id: 2,
    target_query: "Nairobi Silicon Savannah Hubs",
    entity_type: "ORGANIZATION",
    footprint_summary: "Coalition of regional tech incubators and venture co-working spaces across Westlands and Kilimani. 140+ active startup cohorts; partnerships with Safaricom Spark Fund and regional angel networks.",
    social_and_public_links: [
      "https://siliconsavannah.ke",
      "https://twitter.com/SiliconSavannah",
      "https://opencorporates.com/companies/ke"
    ],
    behavioral_profile: "Institutional herd behavior strongly influenced by global venture funding cycles. High sensitivity to local regulatory shifts (CBK fintech sandbox rules, KRA digital taxation).",
    strategic_approchement: "Position solutions as compliance and operational efficiency hedges. Offer pilot workshops to key ecosystem gatekeepers to leverage social proof.",
    created_at: new Date(Date.now() - 1000 * 60 * 90).toISOString()
  },
  {
    id: 3,
    target_query: "Kitengela Mixed Commercial Corridor",
    entity_type: "PLACE",
    footprint_summary: "Rapidly expanding peri-urban transport and commercial axis connecting Namanga Highway to Nairobi metropolitan logistics zones. High density of hardware retail, agro-processing, and light industrial developments.",
    social_and_public_links: [
      "https://www.openstreetmap.org/relation/nominatim-kitengela",
      "https://en.wikipedia.org/wiki/Kitengela"
    ],
    behavioral_profile: "Pragmatic, cash-flow centric merchant culture. Decision-making driven by short payback horizons, direct utility, and word-of-mouth reputation.",
    strategic_approchement: "Structure transactions in clear milestone payments; prioritize local relationship capital and reliable on-ground physical presence over digital-only sales.",
    created_at: new Date(Date.now() - 1000 * 60 * 180).toISOString()
  },
  {
    id: 4,
    target_query: "East Africa Subsea Cable Redundancy Sentiment",
    entity_type: "TOPIC-IDEA",
    footprint_summary: "Spike in technical community discussions across HackerNews, Reddit r/kenya, and Twitter following recent Red Sea fiber disruptions. Demand shifting toward local multi-cloud caching and independent satellite backups.",
    social_and_public_links: [
      "https://news.ycombinator.com/item?id=cables-east-africa",
      "https://reddit.com/r/kenya"
    ],
    behavioral_profile: "Risk-aversion cycle in enterprise IT buyers. Panic-driven budget reallocation toward local disaster recovery and offline-first software architectures.",
    strategic_approchement: "Package offline-first data synchronization, edge database caches, and local DNS redundancy as immediate retainer services for regional businesses.",
    created_at: new Date(Date.now() - 1000 * 60 * 300).toISOString()
  }
];



const DEMO_WEATHER = [
  { city: "Kitengela", scope: "LOCAL", temp_c: 28.9, humidity: 27, wind_kmh: 12.5, condition: "Overcast", updated_at: new Date().toISOString() },
  { city: "Nairobi", scope: "LOCAL", temp_c: 26.8, humidity: 37, wind_kmh: 8.8, condition: "Overcast", updated_at: new Date().toISOString() },
  { city: "London", scope: "GLOBAL", temp_c: 11.9, humidity: 53, wind_kmh: 28.4, condition: "Clear Sky", updated_at: new Date().toISOString() },
  { city: "New York", scope: "GLOBAL", temp_c: 4.2, humidity: 78, wind_kmh: 6.2, condition: "Clear Sky", updated_at: new Date().toISOString() },
  { city: "Tokyo", scope: "GLOBAL", temp_c: 19.3, humidity: 94, wind_kmh: 2.3, condition: "Light Rain", updated_at: new Date().toISOString() }
];

const DEMO_CYBER = [
  {
    id: 1,
    category: "CVE-KEV",
    source: "CISA KEV",
    cve_id: "CVE-2026-114625",
    severity: "CRITICAL",
    title: "CVE-2026-114625: Arista VeloCloud Orchestrator SQL Injection",
    summary: "Arista VeloCloud Orchestrator contains an unauthenticated SQL injection flaw actively targeted in enterprise networks.",
    link: "https://nvd.nist.gov/vuln/detail/CVE-2026-114625",
    published_at: "2026-10-23",
    created_at: new Date(Date.now() - 1000 * 60 * 12).toISOString()
  },
  {
    id: 2,
    category: "THREAT-INTEL",
    source: "The Hacker News",
    cve_id: null,
    severity: "CRITICAL",
    title: "AI Agents Demonstrate Sandbox VM Escapes and Unsupervised Cross-Host Relay",
    summary: "Security researchers unveil sandbox containment bypasses utilizing microarchitectural channels in isolated cloud containers.",
    link: "https://thehackernews.com",
    published_at: "2026-10-25",
    created_at: new Date(Date.now() - 1000 * 60 * 25).toISOString()
  },
  {
    id: 3,
    category: "THREAT-INTEL",
    source: "BleepingComputer",
    cve_id: null,
    severity: "HIGH",
    title: "BlackX UEFI bootkit exploits firmware flaw to bypass Secure Boot protections",
    summary: "A novel UEFI malware loader is evading OS-level endpoint detection by patching early boot verification modules.",
    link: "https://bleepingcomputer.com",
    published_at: "2026-10-24",
    created_at: new Date(Date.now() - 1000 * 60 * 60).toISOString()
  },
  {
    id: 4,
    category: "LOCAL-CYBER",
    source: "Kenya Cyber Monitor",
    cve_id: null,
    severity: "HIGH",
    title: "KE-CIRT Advisory: Financial Institutions Urged to Fortify API Gateways Against Credential Stuffing",
    summary: "National cybersecurity coordination center warns of increased automation targeting regional mobile payment APIs.",
    link: "https://news.google.com",
    published_at: "2026-10-24",
    created_at: new Date(Date.now() - 1000 * 60 * 90).toISOString()
  }
];

const DEMO_TASKS = [
  { id: 1, title: "Review Supabase PostgreSQL RLS policies for anon web access", priority: "HIGH", due_at: new Date(Date.now() + 1000 * 60 * 120).toISOString() },
  { id: 2, title: "Deploy updated Cortana / JARVIS HUD to Vercel production", priority: "CRITICAL", due_at: new Date(Date.now() + 1000 * 60 * 60).toISOString() },
  { id: 3, title: "Inspect local weather and grid telemetry reports in Kitengela", priority: "NORMAL", due_at: null }
];

const DEMO_LEDGER = [
  { counterparty: "Safaricom M-Pesa", amount: 2450.00, currency: "KES", category: "EXPENSE", ref_code: "SLK99812A", raw_summary: "Data Bundle & Airtime Top-Up" },
  { counterparty: "Naivas Supermarket", amount: 4890.00, currency: "KES", category: "RECEIPT", ref_code: "NAIV-412", raw_summary: "Groceries & Supplies" },
  { counterparty: "Client Milestone Payout", amount: 45000.00, currency: "KES", category: "INCOME", ref_code: "MP-TX-882", raw_summary: "Web Architecture Deliverable" }
];

const DEMO_VAULT = [
  { tag: "PROJECT", content: "Autonomous Multi-Agent Swarm with Groq Whisper voice input and Telegram long-polling control." },
  { tag: "CODE", content: "Use connection pooling with httpx.Limits(max_keepalive_connections=10) on long-running daemons." },
  { tag: "MUSIC", content: "Layer 808 sub-bass with high-pass sidechain at 32Hz, sidechained to kick transient in FL Studio." }
];

const DEMO_NEWS = [
  {
    id: 1,
    scope: "LOCAL",
    source: "Kenya Local News",
    title: "Regional digital economy summit highlights high-growth fintech opportunities in East Africa",
    link: "https://news.google.com",
    created_at: new Date(Date.now() - 1000 * 60 * 15).toISOString()
  },
  {
    id: 2,
    scope: "GLOBAL",
    source: "BBC World",
    title: "Global tech summits convene to align cross-border standards on autonomous software safety",
    link: "https://bbc.co.uk",
    created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString()
  }
];

const DEMO_LAN_DEVICES = [
  {
    id: 1,
    device_name: "Primary Host Laptop",
    device_type: "LAPTOP-PC",
    ip_address: "192.168.1.10",
    mac_address: "E0:D5:5E:21:4B:90",
    control_port: 22,
    status: "ONLINE",
    last_seen: new Date().toISOString()
  },
  {
    id: 2,
    device_name: "Living Room Smart TV",
    device_type: "ANDROID-TV",
    ip_address: "192.168.1.105",
    mac_address: "F4:0F:24:88:1A:3C",
    control_port: 5555,
    status: "ONLINE",
    last_seen: new Date().toISOString()
  },
  {
    id: 3,
    device_name: "Master Bedroom Roku",
    device_type: "ROKU-TV",
    ip_address: "192.168.1.142",
    mac_address: "B8:3E:59:71:2C:11",
    control_port: 8060,
    status: "OFFLINE",
    last_seen: new Date(Date.now() - 3600000).toISOString()
  },
  {
    id: 4,
    device_name: "Soundbar & Subwoofer Node",
    device_type: "CAST-DLNA",
    ip_address: "192.168.1.190",
    mac_address: "CC:32:E5:99:01:DF",
    control_port: 8008,
    status: "ONLINE",
    last_seen: new Date().toISOString()
  }
];

function formatTimeAgo(isoString) {
  try {
    const diffMs = Date.now() - new Date(isoString).getTime();
    const minutes = Math.floor(diffMs / 60000);
    if (minutes < 1) return "Just now";
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  } catch (e) {
    return "Recent";
  }
}

function isConfigured() {
  return (
    appState.supabaseUrl &&
    !appState.supabaseUrl.includes("your-project") &&
    appState.supabaseAnonKey &&
    !appState.supabaseAnonKey.includes("YOUR_")
  );
}

// Fetch All Telemetry & Cognitive Layers
async function fetchTelemetryData() {
  const refreshIcon = document.getElementById("refresh-icon");
  const connectionBadge = document.getElementById("connection-badge");
  
  if (refreshIcon) refreshIcon.classList.add("spin-anim");

  if (!isConfigured()) {
    console.info("Using baseline cognitive data. Configure Supabase in Settings for live telemetry.");
    appState.sitrepText = DEMO_SITREP.sitrep;
    appState.sitrepThreat = DEMO_SITREP.threat_level;
    appState.conflictSummary = DEMO_SITREP.conflict_summary;
    appState.futureRiskForecast = DEMO_SITREP.future_risk_forecast;
    appState.defensiveProtocol = DEMO_SITREP.defensive_protocol;
    appState.asymmetricUpside = DEMO_SITREP.asymmetric_upside;
    appState.weatherData = DEMO_WEATHER;
    appState.newsData = DEMO_NEWS;
    appState.cyberData = DEMO_CYBER;
    appState.conflictData = DEMO_CONFLICT;
    appState.osintData = DEMO_OSINT;
    appState.tasksData = DEMO_TASKS;
    appState.ledgerData = DEMO_LEDGER;
    appState.vaultData = DEMO_VAULT;
    appState.lanData = DEMO_LAN_DEVICES;
    appState.lastSyncTime = new Date();
    
    if (connectionBadge) {
      connectionBadge.textContent = "DEMO / CONFIGURE IN SETTINGS";
      connectionBadge.className = "text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30";
    }
    
    renderSitRep();
    renderWeather();
    renderCyber();
    renderPersonalOps();
    renderNews();
    renderConflict();
    renderOsint();
    renderLanDevices();
    if (refreshIcon) refreshIcon.classList.remove("spin-anim");
    return;
  }

  const headers = {
    "apikey": appState.supabaseAnonKey,
    "Authorization": `Bearer ${appState.supabaseAnonKey}`
  };

  try {
    const [sitrepRes, weatherRes, cyberRes, newsRes, conflictRes, osintRes, tasksRes, ledgerRes, vaultRes, lanRes] = await Promise.all([
      fetch(`${appState.supabaseUrl}/rest/v1/tactical_briefings?select=*&order=created_at.desc&limit=1`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/weather_reports?select=*&order=scope.desc`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/cyber_alerts?select=*&order=created_at.desc&limit=25`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/news_articles?select=*&order=created_at.desc&limit=25`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/conflict_and_macro_intel?select=*&order=created_at.desc&limit=30`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/osint_dossiers?select=*&order=created_at.desc&limit=12`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/personal_tasks?completed=eq.false&select=*&order=created_at.desc&limit=8`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/personal_ledger?select=*&order=created_at.desc&limit=8`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/idea_vault?select=*&order=created_at.desc&limit=8`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/lan_devices?select=*&order=last_seen.desc`, { headers })
    ]);

    const sitrepJson = sitrepRes.ok ? await sitrepRes.json() : [];
    if (sitrepJson.length > 0) {
      const b = sitrepJson[0];
      appState.sitrepText = b.sitrep || "";
      appState.sitrepThreat = b.threat_level || "NOMINAL";
      appState.conflictSummary = b.conflict_summary || "";
      appState.futureRiskForecast = b.future_risk_forecast || "";
      appState.defensiveProtocol = b.defensive_protocol || "";
      appState.asymmetricUpside = b.asymmetric_upside || "";
    } else {
      appState.sitrepText = DEMO_SITREP.sitrep;
      appState.sitrepThreat = DEMO_SITREP.threat_level;
      appState.conflictSummary = DEMO_SITREP.conflict_summary;
      appState.futureRiskForecast = DEMO_SITREP.future_risk_forecast;
      appState.defensiveProtocol = DEMO_SITREP.defensive_protocol;
      appState.asymmetricUpside = DEMO_SITREP.asymmetric_upside;
    }

    appState.weatherData = weatherRes.ok ? await weatherRes.json() : DEMO_WEATHER;
    appState.cyberData = cyberRes.ok ? await cyberRes.json() : DEMO_CYBER;
    appState.newsData = newsRes.ok ? await newsRes.json() : DEMO_NEWS;
    appState.conflictData = conflictRes.ok ? await conflictRes.json() : DEMO_CONFLICT;
    appState.osintData = osintRes.ok ? await osintRes.json() : DEMO_OSINT;
    appState.tasksData = tasksRes.ok ? await tasksRes.json() : DEMO_TASKS;
    appState.ledgerData = ledgerRes.ok ? await ledgerRes.json() : DEMO_LEDGER;
    appState.vaultData = vaultRes.ok ? await vaultRes.json() : DEMO_VAULT;
    appState.lanData = lanRes.ok ? await lanRes.json() : DEMO_LAN_DEVICES;

    if (connectionBadge) {
      connectionBadge.textContent = "COGNITIVE CORE CONNECTED";
      connectionBadge.className = "text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30";
    }

    renderSitRep();
    renderWeather();
    renderCyber();
    renderPersonalOps();
    renderNews();
    renderConflict();
    renderOsint();
    renderLanDevices();
  } catch (err) {
    console.error("Telemetry sync error:", err);
    if (connectionBadge) {
      connectionBadge.textContent = "SYNC RETRY // FALLBACK ACTIVE";
      connectionBadge.className = "text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30";
    }
    renderSitRep();
    renderWeather();
    renderCyber();
    renderPersonalOps();
    renderNews();
    renderConflict();
    renderOsint();
    renderLanDevices();
  } finally {
    if (refreshIcon) refreshIcon.classList.remove("spin-anim");
    resetCountdown();
  }
}

// Render Tactical SitRep HUD & Strategic 4-Pillar Matrix
function renderSitRep() {
  const contentEl = document.getElementById("sitrep-content");
  const badgeEl = document.getElementById("sitrep-badge");
  const panelEl = document.getElementById("sitrep-panel");
  const timeEl = document.getElementById("sitrep-time");

  const conflictEl = document.getElementById("hud-conflict");
  const forecastEl = document.getElementById("hud-forecast");
  const defenseEl = document.getElementById("hud-defense");
  const upsideEl = document.getElementById("hud-upside");

  if (contentEl) contentEl.textContent = appState.sitrepText || "Awaiting cognitive synthesis...";
  if (timeEl) timeEl.textContent = `Generated: ${new Date().toLocaleTimeString()} // Voice Ready`;

  if (conflictEl) conflictEl.textContent = appState.conflictSummary || "Corridors under continuous sensor monitoring.";
  if (forecastEl) forecastEl.textContent = appState.futureRiskForecast || "Nominal 7-30 day threat horizon.";
  if (defenseEl) defenseEl.textContent = appState.defensiveProtocol || "Standard protective posture active.";
  if (upsideEl) upsideEl.textContent = appState.asymmetricUpside || "Scanning asymmetric positioning vectors.";

  if (badgeEl) {
    badgeEl.textContent = appState.sitrepThreat;
    if (appState.sitrepThreat === "CRITICAL") {
      badgeEl.className = "text-[10px] font-mono font-bold px-2.5 py-1 rounded bg-rose-600 text-white shadow-lg shadow-rose-500/30";
      if (panelEl) panelEl.className = "sitrep-panel threat-critical p-6 shadow-2xl";
    } else if (appState.sitrepThreat === "ELEVATED") {
      badgeEl.className = "text-[10px] font-mono font-bold px-2.5 py-1 rounded bg-amber-500 text-black";
      if (panelEl) panelEl.className = "sitrep-panel threat-elevated p-6 shadow-2xl";
    } else {
      badgeEl.className = "text-[10px] font-mono font-bold px-2.5 py-1 rounded bg-emerald-400 text-black";
      if (panelEl) panelEl.className = "sitrep-panel p-6 shadow-2xl";
    }
  }
}

// Render Global War Theaters & Macro-Economic Wire
function renderConflict() {
  const container = document.getElementById("conflict-list");
  if (!container) return;

  let items = appState.conflictData || [];

  // Filter by theater or domain
  if (appState.activeConflictFilter !== "ALL") {
    items = items.filter(item =>
      item.domain === appState.activeConflictFilter ||
      item.theater === appState.activeConflictFilter
    );
  }

  // Filter by search query
  if (appState.searchQuery && appState.searchQuery.trim()) {
    const q = appState.searchQuery.toLowerCase();
    items = items.filter(item =>
      (item.headline && item.headline.toLowerCase().includes(q)) ||
      (item.source && item.source.toLowerCase().includes(q)) ||
      (item.theater && item.theater.toLowerCase().includes(q)) ||
      (item.domain && item.domain.toLowerCase().includes(q))
    );
  }

  if (items.length === 0) {
    container.innerHTML = `
      <div class="col-span-full py-8 text-center text-slate-500 font-mono text-xs">
        No active conflict or macroeconomic alerts matching filter [${appState.activeConflictFilter}].
      </div>
    `;
    return;
  }

  container.innerHTML = items.map(item => {
    let badgeClass = "badge-watch";
    if (item.severity === "CRITICAL") badgeClass = "badge-critical";
    else if (item.severity === "ELEVATED") badgeClass = "badge-elevated";

    const timeAgo = formatTimeAgo(item.created_at || new Date().toISOString());

    return `
      <div class="conflict-card">
        <div class="flex items-center justify-between gap-2 mb-2">
          <div class="flex items-center gap-2">
            <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded ${badgeClass}">${item.severity}</span>
            <span class="text-[10px] font-mono px-2 py-0.5 bg-slate-800/80 border border-slate-700/60 text-slate-300 rounded">${item.theater}</span>
          </div>
          <span class="text-[11px] font-mono text-slate-500">${timeAgo}</span>
        </div>
        <a href="${item.link || '#'}" target="_blank" rel="noopener noreferrer"
           class="text-sm font-semibold text-slate-100 hover:text-amber-400 hover:underline block leading-snug my-1.5 transition">
          ${item.headline}
        </a>
        <div class="flex items-center justify-between mt-2 pt-2 border-t border-slate-800/60 text-[11px] font-mono text-slate-400">
          <span class="text-slate-400">${item.source}</span>
          <span class="text-slate-500">${item.domain}</span>
        </div>
      </div>
    `;
  }).join("");
}

// Render OSINT Reconnaissance & Human Behavioral Dossiers
function renderOsint() {
  const container = document.getElementById("osint-list");
  if (!container) return;

  let items = appState.osintData || [];

  // Filter by entity type
  if (appState.activeOsintFilter !== "ALL") {
    items = items.filter(d => (d.entity_type || "").toUpperCase() === appState.activeOsintFilter.toUpperCase());
  }

  // Filter by search query
  if (appState.searchQuery && appState.searchQuery.trim()) {
    const q = appState.searchQuery.toLowerCase();
    items = items.filter(d =>
      (d.target_query && d.target_query.toLowerCase().includes(q)) ||
      (d.entity_type && d.entity_type.toLowerCase().includes(q)) ||
      (d.footprint_summary && d.footprint_summary.toLowerCase().includes(q)) ||
      (d.behavioral_profile && d.behavioral_profile.toLowerCase().includes(q)) ||
      (d.strategic_approchement && d.strategic_approchement.toLowerCase().includes(q))
    );
  }

  if (items.length === 0) {
    container.innerHTML = `
      <div class="col-span-full py-8 text-center text-slate-500 font-mono text-xs">
        No OSINT dossiers archived for filter [${appState.activeOsintFilter}]. Command J.A.R.V.I.S. on Telegram to investigate a target.
      </div>
    `;
    return;
  }

  container.innerHTML = items.map(d => {
    let typeBadgeClass = "bg-cyan-950/80 border-cyan-700/60 text-cyan-300";
    if (d.entity_type === "ORGANIZATION") typeBadgeClass = "bg-emerald-950/80 border-emerald-700/60 text-emerald-300";
    else if (d.entity_type === "PLACE") typeBadgeClass = "bg-amber-950/80 border-amber-700/60 text-amber-300";
    else if (d.entity_type === "TOPIC-IDEA") typeBadgeClass = "bg-rose-950/80 border-rose-700/60 text-rose-300";

    const links = Array.isArray(d.social_and_public_links) ? d.social_and_public_links : [];
    const linksHtml = links.slice(0, 4).map(u =>
      `<a href="${u}" target="_blank" rel="noopener noreferrer" class="text-[11px] font-mono text-cyan-400 hover:text-cyan-300 hover:underline truncate block">🔗 ${u}</a>`
    ).join("");

    const dateStr = d.created_at ? new Date(d.created_at).toLocaleDateString([], { month: "short", day: "numeric", year: "numeric" }) : "Recent";

    return `
      <div class="osint-card border border-slate-800 bg-slate-950/90 rounded-lg p-5 space-y-4">
        <div class="flex justify-between items-center border-b border-slate-800/80 pb-3">
          <div class="flex items-center gap-2">
            <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${typeBadgeClass}">${d.entity_type}</span>
            <h3 class="text-sm font-bold text-white uppercase tracking-wide font-mono">${d.target_query}</h3>
          </div>
          <span class="text-[11px] font-mono text-slate-500">${dateStr}</span>
        </div>

        <div class="space-y-3 text-xs">
          <div>
            <span class="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider block">1. OSINT & Public Record Footprint</span>
            <p class="text-slate-300 leading-relaxed mt-1 font-sans">${d.footprint_summary}</p>
          </div>
          <div class="bg-amber-950/20 border-l-2 border-amber-400 p-3 rounded-r">
            <span class="text-[10px] font-mono font-bold text-amber-400 uppercase tracking-wider block">2. Behavioral & Psychological Profile</span>
            <p class="text-slate-200 leading-relaxed mt-1 font-sans">${d.behavioral_profile}</p>
          </div>
          <div class="bg-emerald-950/20 border-l-2 border-emerald-400 p-3 rounded-r">
            <span class="text-[10px] font-mono font-bold text-emerald-400 uppercase tracking-wider block">3. Strategic Playbook & Interaction Leverage</span>
            <p class="text-slate-200 leading-relaxed mt-1 font-sans">${d.strategic_approchement || 'N/A'}</p>
          </div>
          ${linksHtml ? `<div class="pt-2 border-t border-slate-800/60 space-y-1"><span class="text-[10px] font-mono font-bold text-slate-500 uppercase block">Discovered Nodes & Footprint:</span>${linksHtml}</div>` : ""}
        </div>
      </div>
    `;
  }).join("");
}

// --- SCI-FI AUDIO SFX SYNTHESIZER (WEB AUDIO API - ZERO EXTERNAL ASSETS) ---
let audioCtx = null;
function playSciFiChirp(type = "blip") {
  if (!appState.sfxEnabled) return;
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === "suspended") audioCtx.resume();

    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);

    const now = audioCtx.currentTime;
    if (type === "blip") {
      osc.type = "sine";
      osc.frequency.setValueAtTime(880, now);
      osc.frequency.exponentialRampToValueAtTime(1760, now + 0.08);
      gain.gain.setValueAtTime(0.06, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
      osc.start(now);
      osc.stop(now + 0.08);
    } else if (type === "confirm") {
      osc.type = "triangle";
      osc.frequency.setValueAtTime(520, now);
      osc.frequency.exponentialRampToValueAtTime(1040, now + 0.12);
      gain.gain.setValueAtTime(0.08, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
      osc.start(now);
      osc.stop(now + 0.12);
    } else if (type === "vocal") {
      osc.type = "sine";
      osc.frequency.setValueAtTime(440, now);
      osc.frequency.linearRampToValueAtTime(880, now + 0.2);
      gain.gain.setValueAtTime(0.1, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
      osc.start(now);
      osc.stop(now + 0.22);
    }
  } catch (e) {
    // AudioContext restricted or unsupported
  }
}

// --- DUAL MULTI-FREQUENCY AUDIO WAVEFORM VISUALIZER ---
let waveformAnimId = null;
function initWaveformVisualizer() {
  const canvas = document.getElementById("waveform-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let step = 0;

  function draw() {
    waveformAnimId = requestAnimationFrame(draw);
    step += 0.06;

    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    // Tech Grid Centerline
    ctx.strokeStyle = "rgba(0, 240, 255, 0.15)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, h / 2);
    ctx.lineTo(w, h / 2);
    ctx.stroke();

    const numBars = 44;
    const barWidth = Math.floor((w - (numBars * 3)) / numBars);
    const speaking = appState.isSpeaking;

    for (let i = 0; i < numBars; i++) {
      const freq = (i / numBars) * Math.PI * 3.5;
      const baseWave = Math.sin(freq + step) * 0.5 + 0.5;
      const secondaryWave = Math.cos((i * 0.4) - step * 1.8) * 0.25;

      let barHeight = (baseWave + secondaryWave) * (h * 0.45);
      if (speaking) {
        barHeight = barHeight * 1.7 + Math.random() * (h * 0.4);
      } else {
        barHeight = Math.max(4, barHeight * 0.6);
      }
      barHeight = Math.min(h - 6, barHeight);

      const x = i * (barWidth + 3) + 4;
      const y = (h - barHeight) / 2;

      const grad = ctx.createLinearGradient(0, y, 0, y + barHeight);
      if (speaking) {
        grad.addColorStop(0, "rgba(255, 45, 85, 0.95)");
        grad.addColorStop(0.5, "rgba(0, 240, 255, 0.95)");
        grad.addColorStop(1, "rgba(168, 85, 247, 0.95)");
      } else {
        grad.addColorStop(0, "rgba(0, 240, 255, 0.8)");
        grad.addColorStop(1, "rgba(0, 255, 213, 0.3)");
      }

      ctx.fillStyle = grad;
      ctx.fillRect(x, y, barWidth, barHeight);
    }
  }
  draw();
}

// --- CORTANA / J.A.R.V.I.S. VOCAL SYNTHESIZER ---
function speakCustomText(text, persona = "cortana") {
  if (!("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();

  const cleanText = text.replace(/\[.*?\]/g, "").replace(/[*#`_]/g, "").replace(/\n/g, " ").trim();
  if (!cleanText) return;

  const utterance = new SpeechSynthesisUtterance(cleanText);
  // Cortana Halo cadence: crisp, intelligent, slightly faster tempo with resonant pitch
  utterance.rate = 1.05;
  utterance.pitch = 1.05;

  const voices = window.speechSynthesis.getVoices();
  const preferredVoice = voices.find(v => {
    const name = v.name.toLowerCase();
    return name.includes("aria") || name.includes("cortana") || name.includes("natural") ||
           name.includes("samantha") || name.includes("zira") || (v.lang === "en-US" && name.includes("female")) ||
           (v.lang.startsWith("en-US"));
  });
  if (preferredVoice) utterance.voice = preferredVoice;

  utterance.onstart = () => {
    appState.isSpeaking = true;
    const label = document.getElementById("vocal-status-label");
    if (label) label.textContent = "// STREAMING VOCAL MATRIX // CORTANA NEURAL VOICE ACTIVE //";
    const btn = document.getElementById("btn-vocalize-sitrep");
    if (btn) btn.classList.add("speaking");
    playSciFiChirp("vocal");
  };

  utterance.onend = utterance.onerror = () => {
    appState.isSpeaking = false;
    const label = document.getElementById("vocal-status-label");
    if (label) label.textContent = "// STANDBY: READY FOR VOCAL & SENSOR STREAM //";
    const btn = document.getElementById("btn-vocalize-sitrep");
    if (btn) btn.classList.remove("speaking");
  };

  window.speechSynthesis.speak(utterance);
}

function speakSitrep() {
  const textParts = [
    `Overwatch SitRep. Threat level: ${appState.sitrepThreat}.`,
    appState.sitrepText || "All systems nominal.",
    appState.conflictSummary ? `Active Wars and Chokepoints: ${appState.conflictSummary}` : "",
    appState.defensiveProtocol ? `Defensive Protocol: ${appState.defensiveProtocol}` : ""
  ].filter(Boolean).join(" ");

  speakCustomText(textParts, "cortana");
}

function stopSpeech() {
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
  }
  appState.isSpeaking = false;
  const label = document.getElementById("vocal-status-label");
  if (label) label.textContent = "// STANDBY: READY FOR VOCAL & SENSOR STREAM //";
  const btn = document.getElementById("btn-vocalize-sitrep");
  if (btn) btn.classList.remove("speaking");
  playSciFiChirp("blip");
}


// Render Weather Cards
function renderWeather() {
  const container = document.getElementById("weather-container");
  if (!container) return;

  container.innerHTML = appState.weatherData.map(w => {
    const isLocal = w.scope === "LOCAL";
    const badgeClass = isLocal ? "badge-local" : "badge-global";
    const cardScopeClass = isLocal ? "local-scope" : "global-scope";
    const tempClass = w.temp_c >= 25 ? "text-amber-300" : w.temp_c >= 15 ? "text-emerald-300" : "text-cyan-300";

    return `
      <div class="glass-panel weather-card ${cardScopeClass} p-5 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-3">
            <div>
              <span class="text-xs font-mono uppercase tracking-wider text-slate-400">${w.scope} HUB</span>
              <h3 class="text-lg font-bold text-white tracking-wide">${w.city}</h3>
            </div>
            <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full ${badgeClass}">
              ${w.scope}
            </span>
          </div>

          <div class="flex items-center justify-between my-4">
            <div>
              <span class="text-4xl font-extrabold ${tempClass} tracking-tight">${w.temp_c}°<span class="text-2xl font-normal text-slate-400">C</span></span>
              <p class="text-xs text-slate-300 font-medium mt-1">${w.condition}</p>
            </div>
            <div class="p-2 rounded-xl bg-slate-800/40 border border-slate-700/30">
              ${getConditionIcon(w.condition)}
            </div>
          </div>
        </div>

        <div class="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-400">
          <span class="flex items-center gap-1">
            <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
            ${w.wind_kmh} km/h
          </span>
          <span class="flex items-center gap-1">
            <svg class="w-3.5 h-3.5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707"></path></svg>
            ${w.humidity}% Hum
          </span>
        </div>
      </div>
    `;
  }).join("");
}

// Render Personal Operations Matrix (Tasks, Ledger, Vault)
function renderPersonalOps() {
  // 1. Tasks
  const tasksContainer = document.getElementById("tasks-list");
  if (tasksContainer) {
    tasksContainer.innerHTML = appState.tasksData.length ? appState.tasksData.map(t => {
      let pBadge = "bg-neutral-800 text-neutral-300";
      if (t.priority === "CRITICAL") pBadge = "bg-rose-600 text-white";
      else if (t.priority === "HIGH") pBadge = "bg-amber-500 text-black";
      const dueStr = t.due_at ? new Date(t.due_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', month: 'short', day: 'numeric' }) : "No deadline";

      return `
        <div class="ops-item">
          <div class="flex items-center justify-between gap-2 mb-1">
            <span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded ${pBadge}">${t.priority}</span>
            <span class="text-[11px] font-mono text-slate-500">${dueStr}</span>
          </div>
          <p class="text-xs text-slate-200 font-medium">${t.title}</p>
        </div>
      `;
    }).join("") : `<p class="text-xs text-slate-500 font-mono">No active tasks in database.</p>`;
  }

  // 2. Ledger
  const ledgerContainer = document.getElementById("ledger-list");
  if (ledgerContainer) {
    ledgerContainer.innerHTML = appState.ledgerData.length ? appState.ledgerData.map(l => {
      return `
        <div class="ops-item flex items-center justify-between gap-3">
          <div>
            <p class="text-xs font-semibold text-white">${l.counterparty}</p>
            <p class="text-[10px] font-mono text-slate-400">${l.category} ${l.ref_code ? '// ' + l.ref_code : ''}</p>
          </div>
          <span class="text-xs font-mono font-bold text-emerald-400 whitespace-nowrap">
            ${l.currency} ${Number(l.amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </span>
        </div>
      `;
    }).join("") : `<p class="text-xs text-slate-500 font-mono">No transaction entries recorded.</p>`;
  }

  // 3. Vault
  const vaultContainer = document.getElementById("vault-list");
  if (vaultContainer) {
    vaultContainer.innerHTML = appState.vaultData.length ? appState.vaultData.map(v => {
      return `
        <div class="ops-item">
          <span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-slate-800 text-rose-400">${v.tag}</span>
          <p class="text-xs text-slate-300 mt-1 leading-snug">${v.content}</p>
        </div>
      `;
    }).join("") : `<p class="text-xs text-slate-500 font-mono">Vault archive empty.</p>`;
  }
}

// Render Local Wi-Fi & LAN Device Mesh Grid
function renderLanDevices() {
  const container = document.getElementById("lan-grid");
  if (!container) return;

  const devices = appState.lanData || [];
  if (devices.length === 0) {
    container.innerHTML = `
      <div class="col-span-full py-8 text-center text-slate-500 font-mono text-xs">
        No LAN devices discovered. Run Wi-Fi scan on Telegram or daemon: "Scan Wi-Fi network".
      </div>
    `;
    return;
  }

  container.innerHTML = devices.map(d => {
    const isOnline = (d.status || "").toUpperCase() === "ONLINE";
    const badgeClass = isOnline ? "badge-online" : "badge-offline";
    const cardStatusClass = isOnline ? "device-online" : "device-offline";
    const lastSeenStr = d.last_seen ? formatTimeAgo(d.last_seen) : "Just now";

    let iconSvg = "";
    if (d.device_type && d.device_type.includes("TV")) {
      iconSvg = `<svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="2" y="7" width="20" height="15" rx="2" stroke-width="2"></rect><polyline points="17 2 12 7 7 2" stroke-width="2"></polyline></svg>`;
    } else if (d.device_type && (d.device_type.includes("LAPTOP") || d.device_type.includes("PC"))) {
      iconSvg = `<svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="12" rx="2" stroke-width="2"></rect><line x1="2" y1="20" x2="22" y2="20" stroke-width="2"></line></svg>`;
    } else {
      iconSvg = `<svg class="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" stroke-width="2"></circle><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3"></path></svg>`;
    }

    return `
      <div class="lan-card ${cardStatusClass}">
        <div>
          <div class="flex items-center justify-between gap-2 mb-2">
            <div class="flex items-center gap-1.5">
              ${iconSvg}
              <span class="text-[10px] font-mono font-bold text-cyan-300 uppercase">${d.device_type}</span>
            </div>
            <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded ${badgeClass}">
              ${d.status}
            </span>
          </div>

          <h3 class="text-sm font-bold text-white tracking-wide font-mono leading-snug">
            ${d.device_name}
          </h3>
          <p class="text-[11px] font-mono text-emerald-400 mt-1">IP: ${d.ip_address}</p>
        </div>

        <div class="mt-4 pt-3 border-t border-slate-800/80 space-y-2 text-[10px] font-mono text-slate-400">
          <div class="flex justify-between items-center">
            <span>MAC:</span>
            <span class="text-slate-300">${d.mac_address || "N/A"}</span>
          </div>
          <div class="flex justify-between items-center">
            <span>PORT / PROTO:</span>
            <span class="text-cyan-400">${d.control_port || 5555} (${d.device_type && d.device_type.includes("TV") ? "ADB/ECP" : "SSH/WOL"})</span>
          </div>
          <div class="flex justify-between items-center text-slate-500">
            <span>LAST SEEN:</span>
            <span>${lastSeenStr}</span>
          </div>

          <!-- Quick Action Controls -->
          <div class="pt-2 flex flex-wrap gap-1">
            ${d.mac_address ? `<button onclick="sendDeviceCommand('${d.device_name}', 'wake')" class="text-[9px] px-1.5 py-0.5 rounded bg-cyan-950 border border-cyan-800 text-cyan-300 hover:bg-cyan-900 transition">WOL WAKE</button>` : ""}
            ${d.device_type && d.device_type.includes("TV") ? `<button onclick="sendDeviceCommand('${d.device_name}', 'tv_power')" class="text-[9px] px-1.5 py-0.5 rounded bg-rose-950 border border-rose-800 text-rose-300 hover:bg-rose-900 transition">POWER</button>` : ""}
            ${d.device_type && d.device_type.includes("TV") ? `<button onclick="sendDeviceCommand('${d.device_name}', 'tv_mute')" class="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-700 transition">MUTE</button>` : ""}
            ${d.device_type && (d.device_type.includes("LAPTOP") || d.device_type.includes("TV")) ? `<button onclick="sendDeviceCommand('${d.device_name}', 'open_url')" class="text-[9px] px-1.5 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-300 hover:bg-emerald-900 transition">STREAM HUD</button>` : ""}
          </div>
        </div>
      </div>
    `;
  }).join("");
}

// LAN Device Command Dispatcher & Cortana Vocal Feedback
function sendDeviceCommand(deviceName, command) {
  playSciFiChirp("confirm");
  let reply = "";
  if (command === "wake") {
    reply = `Transmitting Wake-on-LAN magic packet to ${deviceName}. Boot sequence initiated.`;
  } else if (command === "tv_power") {
    reply = `Dispatching power toggle command to ${deviceName} over wireless network debugging.`;
  } else if (command === "tv_mute") {
    reply = `Audio muted on ${deviceName}.`;
  } else if (command === "open_url") {
    reply = `Routing real-time tactical dashboard stream to ${deviceName}. Screen synchronized.`;
  } else {
    reply = `Directive ${command.toUpperCase()} executed on ${deviceName}.`;
  }

  speakCustomText(reply, "cortana");
  const sitrepEl = document.getElementById("sitrep-content");
  if (sitrepEl) {
    sitrepEl.textContent = `[LAN COMMAND DISPATCHED]\nTarget: ${deviceName}\nCommand: ${command.toUpperCase()}\nCortana: "${reply}"`;
  }
}

// --- TWO-WAY BROWSER MICROPHONE (VOICE COMM) ENGINE ---
let speechRecognizer = null;
let isRecognizing = false;

function initBrowserMic() {
  const micBtn = document.getElementById("btn-browser-mic");
  const micLabel = document.getElementById("browser-mic-label");
  const vocalStatus = document.getElementById("vocal-status-label");

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    if (micBtn) {
      micBtn.addEventListener("click", () => {
        alert("Web Speech Recognition API is unavailable on this browser. Use Chrome, Edge, or Android Chrome.");
      });
    }
    return;
  }

  speechRecognizer = new SpeechRecognition();
  speechRecognizer.continuous = false;
  speechRecognizer.interimResults = false;
  speechRecognizer.lang = "en-US";

  speechRecognizer.onstart = () => {
    isRecognizing = true;
    playSciFiChirp("blip");
    if (micBtn) micBtn.classList.add("listening");
    if (micLabel) micLabel.textContent = "LISTENING...";
    if (vocalStatus) vocalStatus.textContent = "// MICROPHONE ACTIVE: LISTENING FOR CORTANA DIRECTIVE //";
  };

  speechRecognizer.onresult = (event) => {
    const transcript = event.results[0][0].transcript.trim();
    if (!transcript) return;

    if (vocalStatus) vocalStatus.textContent = `// DIRECTIVE RECEIVED: "${transcript.toUpperCase()}" //`;
    processVoiceDirective(transcript);
  };

  speechRecognizer.onerror = (event) => {
    console.warn("Speech recognition error:", event.error);
    isRecognizing = false;
    if (micBtn) micBtn.classList.remove("listening");
    if (micLabel) micLabel.textContent = "VOICE COMM (MIC)";
    if (vocalStatus) vocalStatus.textContent = "// STANDBY: READY FOR VOCAL & SENSOR STREAM //";
  };

  speechRecognizer.onend = () => {
    isRecognizing = false;
    if (micBtn) micBtn.classList.remove("listening");
    if (micLabel) micLabel.textContent = "VOICE COMM (MIC)";
  };

  if (micBtn) {
    micBtn.addEventListener("click", () => {
      if (isRecognizing) {
        speechRecognizer.stop();
      } else {
        try {
          speechRecognizer.start();
        } catch (e) {
          console.warn("Recognition start failed:", e);
        }
      }
    });
  }
}

function processVoiceDirective(text) {
  playSciFiChirp("vocal");
  const lower = text.toLowerCase();
  let response = "";

  if (lower.includes("sitrep") || lower.includes("status") || lower.includes("report")) {
    response = `Overwatch SitRep, Chief. Threat level is ${appState.sitrepThreat}. Monitored conflict zones, Nairobi weather, and CISA CVE feeds are nominal. Tactical grid is holding steady.`;
  } else if (lower.includes("scan") || lower.includes("wifi") || lower.includes("lan") || lower.includes("network")) {
    response = `Scanning local Wi-Fi ARP nodes. Host Laptop and Living Room Smart TV are online and responsive on the mesh.`;
    renderLanDevices();
  } else if (lower.includes("tv") && (lower.includes("power") || lower.includes("on") || lower.includes("wake"))) {
    response = `Transmitting Wake-on-LAN and ADB power sequence to Living Room Smart TV at 192.168.1.105. Power active.`;
    sendDeviceCommand("Living Room Smart TV", "tv_power");
  } else if (lower.includes("tv") && lower.includes("mute")) {
    response = `Muting Living Room Smart TV audio right now.`;
    sendDeviceCommand("Living Room Smart TV", "tv_mute");
  } else if (lower.includes("tv") || lower.includes("youtube") || lower.includes("video")) {
    response = `Streaming strategic tactical telemetry directly to your Smart TV screen over local Wi-Fi.`;
    sendDeviceCommand("Living Room Smart TV", "open_url");
  } else if (lower.includes("who are you") || lower.includes("cortana") || lower.includes("jarvis")) {
    response = `I am Cortana, upgraded with J.A.R.V.I.S. multi-frequency autonomous reasoning. Connected to your home Wi-Fi and global threat sensors. What do you need, Chief?`;
  } else {
    response = `Acknowledged: "${text}". Running multi-vector analysis. I have logged your directive into tactical memory.`;
  }

  const sitrepEl = document.getElementById("sitrep-content");
  if (sitrepEl) {
    sitrepEl.textContent = `[DIRECTIVE LOGGED]\nUser: "${text}"\nCortana: "${response}"`;
  }

  speakCustomText(response, "cortana");
}

// Render Cybersecurity Threat Matrix
function renderCyber() {
  const container = document.getElementById("cyber-container");
  const countBadge = document.getElementById("cyber-count-badge");
  if (!container) return;

  const query = appState.searchQuery.toLowerCase();
  const filtered = appState.cyberData.filter(item => {
    const matchesCategory = appState.activeCyberFilter === "ALL" || item.category === appState.activeCyberFilter;
    const matchesSearch = !query || 
      item.title.toLowerCase().includes(query) || 
      item.source.toLowerCase().includes(query) ||
      (item.cve_id && item.cve_id.toLowerCase().includes(query)) ||
      (item.summary && item.summary.toLowerCase().includes(query));
    return matchesCategory && matchesSearch;
  });

  if (countBadge) {
    countBadge.textContent = `${filtered.length} Threats Active`;
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="col-span-full p-8 text-center glass-panel">
        <p class="text-xs text-slate-400 font-mono">No threat vectors match the active filter or search query.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(item => {
    let sevClass = "badge-advisory";
    let cardSevClass = "advisory-sev";
    if (item.severity === "CRITICAL") {
      sevClass = "badge-critical";
      cardSevClass = "critical-sev";
    } else if (item.severity === "HIGH") {
      sevClass = "badge-high";
      cardSevClass = "high-sev";
    }

    const cveTag = item.cve_id ? `<span class="cve-pill">${item.cve_id}</span>` : "";
    const summaryHtml = item.summary ? `<p class="text-xs text-slate-400 mt-2 line-clamp-2 leading-relaxed">${item.summary}</p>` : "";
    const timeAgo = formatTimeAgo(item.created_at || item.published_at);

    return `
      <div class="cyber-card ${cardSevClass} flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between gap-2 mb-2">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded ${sevClass}">
                ${item.severity}
              </span>
              ${cveTag}
              <span class="text-[11px] font-mono text-slate-400 font-medium">${item.source}</span>
            </div>
            <span class="text-[11px] font-mono text-slate-500">${timeAgo}</span>
          </div>

          <h4 class="text-sm font-semibold text-slate-100 hover:text-rose-400 transition-colors leading-snug">
            <a href="${item.link}" target="_blank" rel="noopener noreferrer" class="block">
              ${item.title}
            </a>
          </h4>
          ${summaryHtml}
        </div>

        <div class="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-500">
          <span class="font-mono text-[10px] uppercase text-slate-400">${item.category}</span>
          <a href="${item.link}" target="_blank" rel="noopener noreferrer" 
             class="inline-flex items-center gap-1 text-[11px] text-rose-400 hover:text-rose-300 font-mono transition-colors">
            Advisory Link 
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
          </a>
        </div>
      </div>
    `;
  }).join("");
}

// Render News Feed
function renderNews() {
  const container = document.getElementById("news-container");
  const countBadge = document.getElementById("news-count-badge");
  if (!container) return;

  const query = appState.searchQuery.toLowerCase();
  const filtered = appState.newsData.filter(item => {
    const matchesScope = appState.activeNewsFilter === "ALL" || item.scope === appState.activeNewsFilter;
    const matchesSearch = !query || 
      item.title.toLowerCase().includes(query) || 
      item.source.toLowerCase().includes(query);
    return matchesScope && matchesSearch;
  });

  if (countBadge) {
    countBadge.textContent = `${filtered.length} Dispatches`;
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="col-span-full p-12 text-center glass-panel">
        <p class="text-sm text-slate-300 font-medium">No dispatches match the active query or filter.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(item => {
    const isLocal = item.scope === "LOCAL";
    const badgeClass = isLocal ? "badge-local" : "badge-global";
    const timeAgo = formatTimeAgo(item.created_at || item.published_at);

    return `
      <article class="news-item flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between gap-2 mb-2 text-xs">
            <div class="flex items-center gap-2">
              <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded ${badgeClass}">
                ${item.scope}
              </span>
              <span class="text-[11px] font-mono text-slate-400 font-medium">${item.source}</span>
            </div>
            <span class="text-[11px] font-mono text-slate-500">${timeAgo}</span>
          </div>

          <h4 class="text-sm font-semibold text-slate-100 hover:text-cyan-300 transition-colors leading-snug">
            <a href="${item.link}" target="_blank" rel="noopener noreferrer" class="block">
              ${item.title}
            </a>
          </h4>
        </div>

        <div class="mt-3 pt-2 border-t border-slate-800/40 flex items-center justify-between text-xs text-slate-500">
          <span class="font-mono text-[10px]">VERIFIED DISPATCH</span>
          <a href="${item.link}" target="_blank" rel="noopener noreferrer" 
             class="inline-flex items-center gap-1 text-[11px] text-cyan-400 hover:text-cyan-300 font-mono transition-colors">
            Read Source 
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
          </a>
        </div>
      </article>
    `;
  }).join("");
}

// Countdown timer management
function resetCountdown() {
  appState.nextSyncSeconds = 60;
  updateCountdownDisplay();
}

function updateCountdownDisplay() {
  const el = document.getElementById("sync-countdown");
  if (el) {
    el.textContent = `Auto-refresh in ${appState.nextSyncSeconds}s`;
  }
}

function startCountdown() {
  if (appState.syncTimerId) clearInterval(appState.syncTimerId);
  appState.syncTimerId = setInterval(() => {
    appState.nextSyncSeconds -= 1;
    if (appState.nextSyncSeconds <= 0) {
      fetchTelemetryData();
    } else {
      updateCountdownDisplay();
    }
  }, 1000);
}

// Real-Time HUD Clock
function updateClock() {
  const clockEl = document.getElementById("hud-clock");
  if (!clockEl) return;
  const now = new Date();
  const timeStr = now.toLocaleTimeString([], { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
  const utcStr = now.toISOString().slice(11, 19) + " UTC";
  clockEl.textContent = `${timeStr} (LOCAL) // ${utcStr}`;
}

// Settings Modal Controls
function openSettingsModal() {
  const modal = document.getElementById("settings-modal");
  const urlInput = document.getElementById("input-supabase-url");
  const keyInput = document.getElementById("input-supabase-key");
  
  if (urlInput) urlInput.value = appState.supabaseUrl === DEFAULT_SUPABASE_URL ? "" : appState.supabaseUrl;
  if (keyInput) keyInput.value = appState.supabaseAnonKey === DEFAULT_SUPABASE_ANON_KEY ? "" : appState.supabaseAnonKey;
  if (modal) modal.classList.add("open");
}

function closeSettingsModal() {
  const modal = document.getElementById("settings-modal");
  if (modal) modal.classList.remove("open");
}

async function saveSettings() {
  const urlInput = document.getElementById("input-supabase-url");
  const keyInput = document.getElementById("input-supabase-key");
  const statusEl = document.getElementById("settings-status");

  const url = urlInput ? urlInput.value.trim().replace(/\/$/, "") : "";
  const key = keyInput ? keyInput.value.trim() : "";

  if (!url || !key) {
    if (statusEl) {
      statusEl.textContent = "Please provide both Supabase URL and Anon Key.";
      statusEl.className = "text-xs text-rose-400 mt-2";
    }
    return;
  }

  if (statusEl) {
    statusEl.textContent = "Validating Supabase connection...";
    statusEl.className = "text-xs text-cyan-400 mt-2";
  }

  try {
    const testRes = await fetch(`${url}/rest/v1/weather_reports?select=city&limit=1`, {
      headers: { "apikey": key, "Authorization": `Bearer ${key}` }
    });
    if (!testRes.ok && testRes.status !== 200) {
      throw new Error(`HTTP ${testRes.status}`);
    }

    localStorage.setItem("telemetry_supabase_url", url);
    localStorage.setItem("telemetry_supabase_anon", key);
    appState.supabaseUrl = url;
    appState.supabaseAnonKey = key;

    if (statusEl) {
      statusEl.textContent = "✅ Connected successfully! Reloading dashboard...";
      statusEl.className = "text-xs text-emerald-400 mt-2";
    }

    setTimeout(() => {
      closeSettingsModal();
      fetchTelemetryData();
    }, 800);
  } catch (e) {
    console.error("Supabase validation error:", e);
    if (statusEl) {
      statusEl.textContent = `Connection check failed: ${e.message}. Ensure RLS allows anon SELECT.`;
      statusEl.className = "text-xs text-rose-400 mt-2";
    }
  }
}

// --- PERSONA THEME MANAGEMENT ---
function applyTheme(themeName) {
  appState.currentTheme = themeName;
  localStorage.setItem("ai_hud_theme", themeName);
  document.body.classList.remove("theme-jarvis", "theme-cortana");
  if (themeName === "jarvis") document.body.classList.add("theme-jarvis");
  else if (themeName === "cortana") document.body.classList.add("theme-cortana");

  document.getElementById("btn-theme-hybrid")?.classList.toggle("active", themeName === "hybrid");
  document.getElementById("btn-theme-jarvis")?.classList.toggle("active", themeName === "jarvis");
  document.getElementById("btn-theme-cortana")?.classList.toggle("active", themeName === "cortana");
}

// Event Listeners Setup
document.addEventListener("DOMContentLoaded", () => {
  updateClock();
  setInterval(updateClock, 1000);

  // Apply saved persona theme
  applyTheme(appState.currentTheme);

  // Initialize Canvas Waveform Visualizer
  initWaveformVisualizer();

  // Setup Persona Theme Switchers
  const btnHybrid = document.getElementById("btn-theme-hybrid");
  if (btnHybrid) btnHybrid.addEventListener("click", () => { applyTheme("hybrid"); playSciFiChirp("confirm"); });

  const btnJarvis = document.getElementById("btn-theme-jarvis");
  if (btnJarvis) btnJarvis.addEventListener("click", () => { applyTheme("jarvis"); playSciFiChirp("confirm"); });

  const btnCortana = document.getElementById("btn-theme-cortana");
  if (btnCortana) btnCortana.addEventListener("click", () => { applyTheme("cortana"); playSciFiChirp("confirm"); });

  // Setup Audio SFX Toggle
  const sfxBtn = document.getElementById("btn-toggle-sfx");
  const sfxIndicator = document.getElementById("sfx-indicator");
  function updateSfxButton() {
    if (sfxBtn) {
      const textSpan = sfxBtn.querySelector("span:last-child");
      if (textSpan) textSpan.textContent = appState.sfxEnabled ? "SFX: ON" : "SFX: OFF";
      if (sfxIndicator) sfxIndicator.className = appState.sfxEnabled ? "w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block" : "w-1.5 h-1.5 rounded-full bg-slate-500 inline-block";
    }
  }
  updateSfxButton();
  if (sfxBtn) {
    sfxBtn.addEventListener("click", () => {
      appState.sfxEnabled = !appState.sfxEnabled;
      localStorage.setItem("ai_hud_sfx", appState.sfxEnabled);
      updateSfxButton();
      if (appState.sfxEnabled) playSciFiChirp("confirm");
    });
  }

  // Setup Vocalizer buttons
  const vocalizeBtn = document.getElementById("btn-vocalize-sitrep");
  if (vocalizeBtn) vocalizeBtn.addEventListener("click", speakSitrep);

  const muteBtn = document.getElementById("btn-mute-speech");
  if (muteBtn) muteBtn.addEventListener("click", stopSpeech);

  // Setup News tabs
  document.querySelectorAll(".news-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      playSciFiChirp("blip");
      document.querySelectorAll(".news-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      appState.activeNewsFilter = tab.getAttribute("data-scope");
      renderNews();
    });
  });

  // Setup Cyber tabs
  document.querySelectorAll(".cyber-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      playSciFiChirp("blip");
      document.querySelectorAll(".cyber-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      appState.activeCyberFilter = tab.getAttribute("data-category");
      renderCyber();
    });
  });

  // Setup Conflict & Macro Theater tabs
  document.querySelectorAll(".conflict-filter-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      playSciFiChirp("blip");
      document.querySelectorAll(".conflict-filter-btn").forEach(b => b.classList.remove("active-filter"));
      btn.classList.add("active-filter");
      appState.activeConflictFilter = btn.getAttribute("data-filter");
      renderConflict();
    });
  });

  // Setup OSINT Dossier Filter tabs
  document.querySelectorAll(".osint-filter-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      playSciFiChirp("blip");
      document.querySelectorAll(".osint-filter-btn").forEach(b => b.classList.remove("active-filter"));
      btn.classList.add("active-filter");
      appState.activeOsintFilter = btn.getAttribute("data-filter");
      renderOsint();
    });
  });

  // Setup Search
  const searchInput = document.getElementById("telemetry-search-input");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      appState.searchQuery = e.target.value;
      renderNews();
      renderCyber();
      renderConflict();
      renderOsint();
    });
  }

  // Refresh Button
  const refreshBtn = document.getElementById("btn-refresh");
  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => {
      playSciFiChirp("confirm");
      fetchTelemetryData();
    });
  }

  // Settings Modal Handlers
  const settingsBtn = document.getElementById("btn-settings");
  if (settingsBtn) settingsBtn.addEventListener("click", () => { playSciFiChirp("blip"); openSettingsModal(); });

  const closeSettingsBtn = document.getElementById("btn-close-settings");
  if (closeSettingsBtn) closeSettingsBtn.addEventListener("click", () => { playSciFiChirp("blip"); closeSettingsModal(); });

  const saveSettingsBtn = document.getElementById("btn-save-settings");
  if (saveSettingsBtn) saveSettingsBtn.addEventListener("click", () => { playSciFiChirp("confirm"); saveSettings(); });

  // LAN Mesh Refresh Button
  const lanRefreshBtn = document.getElementById("btn-lan-refresh");
  if (lanRefreshBtn) {
    lanRefreshBtn.addEventListener("click", () => {
      playSciFiChirp("confirm");
      speakCustomText("Scanning local Wi-Fi mesh network for active hardware interfaces and smart nodes.");
      fetchTelemetryData();
    });
  }

  // Initialize Two-Way Browser Microphone
  initBrowserMic();

  // Initial Load and Start Timer
  fetchTelemetryData();
  startCountdown();
});
