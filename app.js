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

const LIVE_WEATHER_STATIONS = [
  { city: "Kitengela", scope: "LOCAL", lat: -1.4746, lon: 36.9614 },
  { city: "Nairobi", scope: "LOCAL", lat: -1.2921, lon: 36.8219 },
  { city: "London", scope: "GLOBAL", lat: 51.5074, lon: -0.1278 },
  { city: "New York", scope: "GLOBAL", lat: 40.7128, lon: -74.0060 },
  { city: "Tokyo", scope: "GLOBAL", lat: 35.6762, lon: 139.6503 }
];

const WMO_CODE_MAP = {
  0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
  45: "Fog", 51: "Light Drizzle", 61: "Light Rain", 63: "Moderate Rain",
  65: "Heavy Rain", 80: "Rain Showers", 95: "Thunderstorm"
};

async function fetchLiveWeatherDirect() {
  const reports = [];
  for (const loc of LIVE_WEATHER_STATIONS) {
    try {
      const url = `https://api.open-meteo.com/v1/forecast?latitude=${loc.lat}&longitude=${loc.lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        const cur = data.current || {};
        const cond = WMO_CODE_MAP[cur.weather_code] || "Clear Sky";
        reports.push({
          city: loc.city,
          scope: loc.scope,
          temp_c: Math.round(cur.temperature_2m * 10) / 10,
          condition: cond,
          humidity: cur.relative_humidity_2m,
          wind_kmh: Math.round(cur.wind_speed_10m * 10) / 10,
          updated_at: new Date().toISOString()
        });
      }
    } catch (e) {
      // station error ignored
    }
  }
  if (reports.length > 0) {
    appState.weatherData = reports;
  }
}

async function fetchLiveTelemetryFile() {
  try {
    const res = await fetch("telemetry_live.json?t=" + Date.now());
    if (res.ok) {
      const data = await res.json();
      if (data.sitrep) {
        appState.sitrepText = data.sitrep.sitrep || "";
        appState.sitrepThreat = data.sitrep.threat_level || "NOMINAL";
        appState.conflictSummary = data.sitrep.conflict_summary || "";
        appState.futureRiskForecast = data.sitrep.future_risk_forecast || "";
        appState.defensiveProtocol = data.sitrep.defensive_protocol || "";
        appState.asymmetricUpside = data.sitrep.asymmetric_upside || "";
      }
      if (Array.isArray(data.weather) && data.weather.length > 0) appState.weatherData = data.weather;
      if (Array.isArray(data.cyber) && data.cyber.length > 0) appState.cyberData = data.cyber;
      if (Array.isArray(data.news) && data.news.length > 0) appState.newsData = data.news;
      if (Array.isArray(data.conflicts) && data.conflicts.length > 0) appState.conflictData = data.conflicts;
      if (Array.isArray(data.lan_devices) && data.lan_devices.length > 0) appState.lanData = data.lan_devices;
      if (Array.isArray(data.tasks) && data.tasks.length > 0) appState.tasksData = data.tasks;
      if (Array.isArray(data.ledger) && data.ledger.length > 0) appState.ledgerData = data.ledger;
      if (Array.isArray(data.vault) && data.vault.length > 0) appState.vaultData = data.vault;
    }
  } catch (err) {
    console.warn("Live telemetry file error:", err);
  }
}

// Fetch All Telemetry & Cognitive Layers
async function fetchTelemetryData() {
  const refreshIcon = document.getElementById("refresh-icon");
  const connectionBadge = document.getElementById("connection-badge");
  
  if (refreshIcon) refreshIcon.classList.add("spin-anim");

  if (!isConfigured()) {
    console.info("Ingesting 100% real live planetary, cyber, and network telemetry...");
    await fetchLiveTelemetryFile();
    await fetchLiveWeatherDirect();
    appState.lastSyncTime = new Date();
    
    if (connectionBadge) {
      connectionBadge.textContent = "COGNITIVE CORE ACTIVE (LIVE SENSORS)";
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
    }

    if (weatherRes.ok) {
      const wData = await weatherRes.json();
      if (wData && wData.length > 0) appState.weatherData = wData;
      else await fetchLiveWeatherDirect();
    } else {
      await fetchLiveWeatherDirect();
    }

    if (cyberRes.ok) {
      const cData = await cyberRes.json();
      if (cData && cData.length > 0) appState.cyberData = cData;
    }
    if (newsRes.ok) {
      const nData = await newsRes.json();
      if (nData && nData.length > 0) appState.newsData = nData;
    }
    if (conflictRes.ok) {
      const cfData = await conflictRes.json();
      if (cfData && cfData.length > 0) appState.conflictData = cfData;
    }
    if (osintRes.ok) {
      const oData = await osintRes.json();
      if (oData && oData.length > 0) appState.osintData = oData;
    }
    if (tasksRes.ok) {
      const tData = await tasksRes.json();
      if (tData && tData.length > 0) appState.tasksData = tData;
    }
    if (ledgerRes.ok) {
      const lData = await ledgerRes.json();
      if (lData && lData.length > 0) appState.ledgerData = lData;
    }
    if (vaultRes.ok) {
      const vData = await vaultRes.json();
      if (vData && vData.length > 0) appState.vaultData = vData;
    }
    if (lanRes.ok) {
      const ldData = await lanRes.json();
      if (ldData && ldData.length > 0) appState.lanData = ldData;
    }

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
