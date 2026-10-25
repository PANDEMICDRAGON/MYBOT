/**
 * Telemetry Monitor: News, Weather & Cyber Command Dashboard Engine
 * Handles Supabase REST API data fetching, real-time filtering, UI rendering,
 * and persistent local configuration.
 */

// Default or fallback config (can be overwritten via settings modal)
const DEFAULT_SUPABASE_URL = "https://your-project.supabase.co";
const DEFAULT_SUPABASE_ANON_KEY = "YOUR_SUPABASE_ANON_KEY";

// State
let appState = {
  supabaseUrl: localStorage.getItem("telemetry_supabase_url") || DEFAULT_SUPABASE_URL,
  supabaseAnonKey: localStorage.getItem("telemetry_supabase_anon") || DEFAULT_SUPABASE_ANON_KEY,
  weatherData: [],
  newsData: [],
  cyberData: [],
  activeNewsFilter: "ALL",   // ALL | LOCAL | GLOBAL
  activeCyberFilter: "ALL",  // ALL | CVE-KEV | THREAT-INTEL | LOCAL-CYBER
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

// Baseline / Demo Data (Shown if Supabase is unconfigured)
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

const DEMO_NEWS = [
  {
    id: 1,
    scope: "LOCAL",
    source: "Kenya Local News",
    title: "Transport infrastructure development: express routes scheduled for eastern metro corridors",
    link: "https://news.google.com",
    created_at: new Date(Date.now() - 1000 * 60 * 15).toISOString()
  },
  {
    id: 2,
    scope: "LOCAL",
    source: "Kenya Local News",
    title: "Regional digital economy summit highlights high-growth fintech opportunities in East Africa",
    link: "https://news.google.com",
    created_at: new Date(Date.now() - 1000 * 60 * 45).toISOString()
  },
  {
    id: 3,
    scope: "GLOBAL",
    source: "BBC World",
    title: "Global tech summits convene to align cross-border standards on autonomous software safety",
    link: "https://bbc.co.uk",
    created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString()
  },
  {
    id: 4,
    scope: "GLOBAL",
    source: "Al Jazeera Global",
    title: "Renewable power output surges across modern energy grids ahead of upcoming climate summit",
    link: "https://aljazeera.com",
    created_at: new Date(Date.now() - 1000 * 60 * 70).toISOString()
  }
];

// Helper: Format relative timestamp
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

// Check if credentials are set
function isConfigured() {
  return (
    appState.supabaseUrl &&
    !appState.supabaseUrl.includes("your-project") &&
    appState.supabaseAnonKey &&
    !appState.supabaseAnonKey.includes("YOUR_")
  );
}

// Fetch Data from Supabase with graceful fallback
async function fetchTelemetryData() {
  const refreshIcon = document.getElementById("refresh-icon");
  const connectionBadge = document.getElementById("connection-badge");
  
  if (refreshIcon) refreshIcon.classList.add("spin-anim");

  if (!isConfigured()) {
    console.info("Using baseline telemetry data. Configure Supabase in Settings to view live production tables.");
    appState.weatherData = DEMO_WEATHER;
    appState.newsData = DEMO_NEWS;
    appState.cyberData = DEMO_CYBER;
    appState.lastSyncTime = new Date();
    
    if (connectionBadge) {
      connectionBadge.textContent = "DEMO / CONFIGURE IN SETTINGS";
      connectionBadge.className = "text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30";
    }
    
    renderWeather();
    renderCyber();
    renderNews();
    if (refreshIcon) refreshIcon.classList.remove("spin-anim");
    return;
  }

  const headers = {
    "apikey": appState.supabaseAnonKey,
    "Authorization": `Bearer ${appState.supabaseAnonKey}`
  };

  try {
    const [weatherRes, cyberRes, newsRes] = await Promise.all([
      fetch(`${appState.supabaseUrl}/rest/v1/weather_reports?select=*&order=scope.desc`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/cyber_alerts?select=*&order=created_at.desc&limit=25`, { headers }),
      fetch(`${appState.supabaseUrl}/rest/v1/news_articles?select=*&order=created_at.desc&limit=30`, { headers })
    ]);

    if (!weatherRes.ok || !cyberRes.ok || !newsRes.ok) {
      throw new Error(`Supabase query status: Weather (${weatherRes.status}), Cyber (${cyberRes.status}), News (${newsRes.status})`);
    }

    const weatherJson = await weatherRes.json();
    const cyberJson = await cyberRes.json();
    const newsJson = await newsRes.json();

    appState.weatherData = Array.isArray(weatherJson) && weatherJson.length > 0 ? weatherJson : DEMO_WEATHER;
    appState.cyberData = Array.isArray(cyberJson) && cyberJson.length > 0 ? cyberJson : DEMO_CYBER;
    appState.newsData = Array.isArray(newsJson) && newsJson.length > 0 ? newsJson : DEMO_NEWS;
    appState.lastSyncTime = new Date();

    if (connectionBadge) {
      connectionBadge.textContent = "SUPABASE LIVE CONNECTED";
      connectionBadge.className = "text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30";
    }

    renderWeather();
    renderCyber();
    renderNews();
  } catch (err) {
    console.error("Telemetry sync error:", err);
    if (connectionBadge) {
      connectionBadge.textContent = "SYNC RETRY // FALLBACK ACTIVE";
      connectionBadge.className = "text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30";
    }
    if (appState.weatherData.length === 0) appState.weatherData = DEMO_WEATHER;
    if (appState.cyberData.length === 0) appState.cyberData = DEMO_CYBER;
    if (appState.newsData.length === 0) appState.newsData = DEMO_NEWS;
    renderWeather();
    renderCyber();
    renderNews();
  } finally {
    if (refreshIcon) refreshIcon.classList.remove("spin-anim");
    resetCountdown();
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
        <svg class="w-12 h-12 mx-auto text-slate-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <p class="text-sm text-slate-300 font-medium">No dispatches match the active query or filter.</p>
        <p class="text-xs text-slate-500 mt-1">Try resetting your search or scope filters.</p>
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

  // Setup Unified Search (Filters both news and cyber threats)
  const searchInput = document.getElementById("telemetry-search-input");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      appState.searchQuery = e.target.value;
      renderNews();
      renderCyber();
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
