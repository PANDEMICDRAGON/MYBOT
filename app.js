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
  activeNewsFilter: "ALL",   // ALL | LOCAL | GLOBAL
  activeCyberFilter: "ALL",  // ALL | CVE-KEV | THREAT-INTEL | LOCAL-CYBER
  activeConflictFilter: "ALL", // ALL | WAR-KINETIC | MACRO-ECONOMIC | EAST-AFRICA | RED-SEA-MIDEAST
  activeOsintFilter: "ALL",    // ALL | PERSON | ORGANIZATION | PLACE | TOPIC-IDEA
  searchQuery: "",
  lastSyncTime: null,
  nextSyncSeconds: 60,
  syncTimerId: null
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
    if (refreshIcon) refreshIcon.classList.remove("spin-anim");
    return;
  }

  const headers = {
    "apikey": appState.supabaseAnonKey,
    "Authorization": `Bearer ${appState.supabaseAnonKey}`
  };

  try {
    const [sitrepRes, weatherRes, cyberRes, newsRes, conflictRes, osintRes, tasksRes, ledgerRes, vaultRes] = await Promise.all([
      fetch(`${appState.supabaseUrl}/rest/v1/tactical_briefings?select=*&order=created_at.desc&limit=1`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/weather_reports?select=*&order=scope.desc`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/cyber_alerts?select=*&order=created_at.desc&limit=25`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/news_articles?select=*&order=created_at.desc&limit=25`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/conflict_and_macro_intel?select=*&order=created_at.desc&limit=30`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/osint_dossiers?select=*&order=created_at.desc&limit=12`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/personal_tasks?completed=eq.false&select=*&order=created_at.desc&limit=8`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/personal_ledger?select=*&order=created_at.desc&limit=8`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/idea_vault?select=*&order=created_at.desc&limit=8`, { headers })
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

// Web Speech API Vocalization (Cortana / J.A.R.V.I.S. Audio Synthesizer)
function speakSitrep() {
  if (!("speechSynthesis" in window)) {
    alert("Speech synthesis is not supported on this browser.");
    return;
  }
  window.speechSynthesis.cancel();
  
  const textParts = [
    `Overwatch SitRep. Threat level: ${appState.sitrepThreat}.`,
    appState.sitrepText || "All systems nominal.",
    appState.conflictSummary ? `Active Wars and Chokepoints: ${appState.conflictSummary}` : "",
    appState.defensiveProtocol ? `Defensive Protocol: ${appState.defensiveProtocol}` : ""
  ].filter(Boolean).join(" ");

  const cleanText = textParts.replace(/\[.*?\]/g, "").replace(/\n/g, " ").trim();
  const utterance = new SpeechSynthesisUtterance(cleanText);
  utterance.rate = 1.05;
  utterance.pitch = 0.95;

  // Prefer a crisp English voice
  const voices = window.speechSynthesis.getVoices();
  const preferredVoice = voices.find(v => v.lang.includes("en-US") || v.lang.includes("en-GB") || v.name.includes("Google") || v.name.includes("Samantha"));
  if (preferredVoice) utterance.voice = preferredVoice;

  window.speechSynthesis.speak(utterance);
}

function stopSpeech() {
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
  }
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

// Event Listeners Setup
document.addEventListener("DOMContentLoaded", () => {
  updateClock();
  setInterval(updateClock, 1000);

  // Setup Vocalizer buttons
  const vocalizeBtn = document.getElementById("btn-vocalize-sitrep");
  if (vocalizeBtn) vocalizeBtn.addEventListener("click", speakSitrep);

  const muteBtn = document.getElementById("btn-mute-speech");
  if (muteBtn) muteBtn.addEventListener("click", stopSpeech);

  // Setup News tabs
  document.querySelectorAll(".news-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".news-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      appState.activeNewsFilter = tab.getAttribute("data-scope");
      renderNews();
    });
  });

  // Setup Cyber tabs
  document.querySelectorAll(".cyber-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".cyber-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      appState.activeCyberFilter = tab.getAttribute("data-category");
      renderCyber();
    });
  });

  // Setup Conflict & Macro Theater tabs
  document.querySelectorAll(".conflict-filter-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".conflict-filter-btn").forEach(b => b.classList.remove("active-filter"));
      btn.classList.add("active-filter");
      appState.activeConflictFilter = btn.getAttribute("data-filter");
      renderConflict();
    });
  });

  // Setup OSINT Dossier Filter tabs
  document.querySelectorAll(".osint-filter-btn").forEach(btn => {
    btn.addEventListener("click", () => {
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
      fetchTelemetryData();
    });
  }

  // Settings Modal Handlers
  const settingsBtn = document.getElementById("btn-settings");
  if (settingsBtn) settingsBtn.addEventListener("click", openSettingsModal);

  const closeSettingsBtn = document.getElementById("btn-close-settings");
  if (closeSettingsBtn) closeSettingsBtn.addEventListener("click", closeSettingsModal);

  const saveSettingsBtn = document.getElementById("btn-save-settings");
  if (saveSettingsBtn) saveSettingsBtn.addEventListener("click", saveSettings);

  // Initial Load and Start Timer
  fetchTelemetryData();
  startCountdown();
});
