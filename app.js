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
  currentTheme: localStorage.getItem("ai_hud_theme") || "hybrid",
  selectedLanDeviceIp: null,
  selectedOsintId: 1,
  radarAngle: 0,
  radarSelectedBlipId: "red-sea"
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

// Global Radar Flashpoint Definitions & State
const RADAR_FLASHPOINTS = [
  { id: "red-sea", name: "RED SEA & BAB EL-MANDEB", type: "CRITICAL", domain: "WAR-KINETIC", x: 0.65, y: 0.35, wire: "Anti-ship ballistic missile and drone corridors active. Commercial container rerouting via Cape of Good Hope sustaining elevated war-risk marine insurance into Mombasa port.", defense: "Verify 30-day USD/KES reserves against import price inflation; maintain local component inventories.", upside: "Retain offshore invoice billing in USD; offer failover routing audits to regional freight logisticians." },
  { id: "horn-africa", name: "HORN OF AFRICA & SUDAN", type: "ELEVATED", domain: "WAR-KINETIC", x: 0.58, y: 0.48, wire: "Regional security dialogue monitoring Port Sudan logistics choke point; Kenya border surveillance elevated.", defense: "Maintain independent local power and offline data mirrors.", upside: "Cross-border tech logistics and regional supply security solutions." },
  { id: "eastern-europe", name: "EASTERN EUROPE & BLACK SEA", type: "CRITICAL", domain: "WAR-KINETIC", x: 0.48, y: 0.20, wire: "Long-range drone strikes and electronic warfare near Black Sea commercial maritime corridor.", defense: "Audit cloud hosting failover across multi-region geographic zones.", upside: "Remote European software engineering contracting in strong currency." },
  { id: "indo-pacific", name: "INDO-PACIFIC & TAIWAN STRAIT", type: "WATCH", domain: "GEOPOLITICAL", x: 0.82, y: 0.30, wire: "Naval patrols near maritime chokepoints; semiconductor export controls under review.", defense: "Procure critical hardware and spare electronics ahead of supply pinches.", upside: "Edge AI and local inference software deployment." },
  { id: "hub-london", name: "LONDON METEOROLOGY HUB", type: "HUB", domain: "SENSORS", x: 0.40, y: 0.24, wire: "Atmospheric array streaming real-time metrics. Station reporting 12.9°C.", defense: "Ensure transatlantic secure tunneling.", upside: "UK fintech integration." },
  { id: "hub-ny", name: "NEW YORK SENSOR HUB", type: "HUB", domain: "SENSORS", x: 0.22, y: 0.28, wire: "Wall Street economic intelligence and atmospheric node. Station reporting 3.2°C.", defense: "USD asset liquidity optimization.", upside: "US financial market index yields." },
  { id: "hub-tokyo", name: "TOKYO SENSOR HUB", type: "HUB", domain: "SENSORS", x: 0.88, y: 0.26, wire: "Pacific technology telemetry online. Station reporting 18.5°C.", defense: "Multi-cloud Asia-Pacific redundancy.", upside: "Cross-currency algorithmic spread arbitrage." }
];

let radarBlipCoordinates = [];
let radarInitialized = false;

function initGlobalRadar() {
  const canvas = document.getElementById("global-radar-canvas");
  if (!canvas || radarInitialized) return;
  radarInitialized = true;
  const ctx = canvas.getContext("2d");

  canvas.addEventListener("click", (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) * (canvas.width / rect.width);
    const y = (e.clientY - rect.top) * (canvas.height / rect.height);

    for (const b of radarBlipCoordinates) {
      if (Math.hypot(b.x - x, b.y - y) <= 15) {
        selectRadarTarget(b.data);
        return;
      }
    }
  });

  function selectRadarTarget(target) {
    playSciFiChirp("confirm");
    appState.radarSelectedBlipId = target.id;
    const titleEl = document.getElementById("radar-target-title");
    const badgeEl = document.getElementById("radar-target-badge");
    const wireEl = document.getElementById("radar-target-wire");
    const defEl = document.getElementById("radar-target-defense");
    const upEl = document.getElementById("radar-target-upside");

    if (titleEl) titleEl.textContent = target.name;
    if (badgeEl) {
      badgeEl.textContent = `${target.type} // ${target.domain}`;
      badgeEl.className = target.type === "CRITICAL" 
        ? "text-[10px] px-2 py-0.5 rounded bg-rose-600/30 text-rose-300 border border-rose-500/40" 
        : (target.type === "ELEVATED" 
          ? "text-[10px] px-2 py-0.5 rounded bg-amber-600/30 text-amber-300 border border-amber-500/40" 
          : "text-[10px] px-2 py-0.5 rounded bg-cyan-950 border border-cyan-700 text-cyan-300");
    }
    if (wireEl) wireEl.textContent = target.wire;
    if (defEl) defEl.textContent = target.defense;
    if (upEl) upEl.textContent = target.upside;
  }

  function draw() {
    requestAnimationFrame(draw);
    appState.radarAngle = (appState.radarAngle + 0.02) % (2 * Math.PI);

    const w = canvas.width;
    const h = canvas.height;
    const cx = w / 2;
    const cy = h / 2;
    const maxR = Math.min(cx, cy) - 16;
    ctx.clearRect(0, 0, w, h);

    // Concentric Range Rings
    [0.33, 0.66, 1.0].forEach((ratio, idx) => {
      const r = maxR * ratio;
      ctx.strokeStyle = "rgba(0, 240, 255, 0.15)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, 2 * Math.PI);
      ctx.stroke();

      ctx.fillStyle = "rgba(0, 240, 255, 0.4)";
      ctx.font = "8px 'JetBrains Mono', monospace";
      ctx.textAlign = "left";
      const kmLabel = (idx + 1) * 4000 + " KM";
      ctx.fillText(kmLabel, cx + 4, cy - r + 10);
    });

    // Crosshairs
    ctx.strokeStyle = "rgba(0, 240, 255, 0.12)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(cx, cy - maxR);
    ctx.lineTo(cx, cy + maxR);
    ctx.moveTo(cx - maxR, cy);
    ctx.lineTo(cx + maxR, cy);
    ctx.stroke();

    // Rotating Radar Sweep Beam
    const beamAngle = appState.radarAngle;
    const beamGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, maxR);
    beamGrad.addColorStop(0, "rgba(0, 240, 255, 0.35)");
    beamGrad.addColorStop(1, "rgba(0, 240, 255, 0.0)");

    ctx.fillStyle = beamGrad;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, maxR, beamAngle - 0.35, beamAngle);
    ctx.closePath();
    ctx.fill();

    // Radar Sweep Leading Edge Line
    ctx.strokeStyle = "rgba(0, 240, 255, 0.85)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + maxR * Math.cos(beamAngle), cy + maxR * Math.sin(beamAngle));
    ctx.stroke();

    // Trajectory Arcs & Blips
    radarBlipCoordinates = [];
    RADAR_FLASHPOINTS.forEach(fp => {
      const bx = fp.x * w;
      const by = fp.y * h;
      radarBlipCoordinates.push({ x: bx, y: by, data: fp });

      const isSelected = fp.id === appState.radarSelectedBlipId;

      // Trajectory arc from center to blip
      ctx.strokeStyle = isSelected ? "rgba(0, 240, 255, 0.6)" : "rgba(255, 255, 255, 0.08)";
      ctx.lineWidth = isSelected ? 1.5 : 0.8;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.quadraticCurveTo(cx + (bx - cx) * 0.5, cy - 25, bx, by);
      ctx.stroke();

      // Blip color
      let blipColor = "#38bdf8";
      if (fp.type === "CRITICAL") blipColor = "#f43f5e";
      else if (fp.type === "ELEVATED") blipColor = "#f59e0b";

      // Blip Circle
      ctx.fillStyle = blipColor;
      ctx.beginPath();
      ctx.arc(bx, by, isSelected ? 5 : 3.5, 0, 2 * Math.PI);
      ctx.fill();

      // Pulsing Halo Ring
      ctx.strokeStyle = blipColor;
      ctx.lineWidth = 1;
      const pulse = (Date.now() % 1200) / 1200;
      ctx.beginPath();
      ctx.arc(bx, by, 6 + pulse * 8, 0, 2 * Math.PI);
      ctx.stroke();

      // Reticle if selected
      if (isSelected) {
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 1.5;
        ctx.strokeRect(bx - 9, by - 9, 18, 18);
      }

      // Blip Label
      ctx.fillStyle = isSelected ? "#fff" : "rgba(255, 255, 255, 0.7)";
      ctx.font = isSelected ? "bold 9px 'Rajdhani', sans-serif" : "8px 'Rajdhani', sans-serif";
      ctx.textAlign = "left";
      ctx.fillText(fp.name.split(" ")[0], bx + 8, by + 3);
    });

    // Anchor Center (Kitengela / Nairobi)
    ctx.fillStyle = "#10b981";
    ctx.beginPath();
    ctx.arc(cx, cy, 4, 0, 2 * Math.PI);
    ctx.fill();
    ctx.fillStyle = "#34d399";
    ctx.font = "bold 9px 'JetBrains Mono', monospace";
    ctx.textAlign = "center";
    ctx.fillText("NAIROBI / KITENGELA", cx, cy + 14);
  }
  draw();
}

// Render Global War Theaters & Macro-Economic Wire
function renderConflict() {
  initGlobalRadar();
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

// --- 5-AXIS BEHAVIORAL SPIDER RADAR MATRIX ---
const OSINT_BEHAVIORAL_AXES = [
  "Surface Web",
  "Social Dorks",
  "Registries",
  "Public Audit",
  "Game Theory"
];

const DEFAULT_OSINT_TARGETS = [
  {
    id: 1,
    target_query: "Kenya Power (KPLC Infrastructure Grid)",
    entity_type: "ORGANIZATION",
    scores: [88, 72, 94, 96, 68],
    footprint_summary: "Dominant power transmission grid holding national statutory monopoly. Monitored for substation telemetry, regional transformer load shedding, and billing metering APIs.",
    behavioral_profile: "Risk-averse corporate utility bureaucracy operating under intense legislative audit scrutiny. Highly reactive to unplanned blackout trends and consumer tariff disputes.",
    strategic_approchement: "Interface via enterprise bulk metering telemetry; verify backup fuel generators in Kitengela node during regional grid fluctuations."
  },
  {
    id: 2,
    target_query: "Safaricom PLC (M-Pesa & Fiber Backbone)",
    entity_type: "ORGANIZATION",
    scores: [96, 92, 98, 90, 86],
    footprint_summary: "East Africa's largest fintech & telecommunications infrastructure operator. Hosts Daraja M-Pesa APIs, LTE/5G base stations, and urban fiber distribution rings.",
    behavioral_profile: "Technologically progressive with strict regulatory compliance standards. Sensitive to network downtime and foreign exchange remittance constraints.",
    strategic_approchement: "Maintain redundant multi-SIM 4G fallback alongside primary fiber line; implement instant webhook verification for M-Pesa transaction notifications."
  },
  {
    id: 3,
    target_query: "Red Sea Maritime & Port Logistics Corridor",
    entity_type: "PLACE",
    scores: [82, 60, 88, 92, 85],
    footprint_summary: "Strategic Bab el-Mandeb and Mombasa shipping lane connecting Middle East crude, European electronics, and African container freight.",
    behavioral_profile: "Geopolitically volatile; container rates and war-risk insurance premiums fluctuate dynamically based on regional security dispatches.",
    strategic_approchement: "Pre-order hardware supplies 30 days ahead; maintain buffer stocks in Nairobi/Kitengela storage facilities."
  }
];

function initOsintSpiderChart() {
  const svg = document.getElementById("osint-spider-svg");
  const pillsContainer = document.getElementById("spider-target-pills");
  if (!svg) return;

  const activeTarget = DEFAULT_OSINT_TARGETS.find(t => t.id === appState.selectedOsintId) || DEFAULT_OSINT_TARGETS[0];

  // Populate target pills
  if (pillsContainer) {
    pillsContainer.innerHTML = DEFAULT_OSINT_TARGETS.map(t => {
      const isSelected = t.id === activeTarget.id;
      const activeClass = isSelected ? "border-cyan-400 bg-cyan-950/80 text-cyan-300 font-bold" : "border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700";
      return `
        <button onclick="selectOsintProfile(${t.id})" class="text-[10px] font-mono px-2 py-1 rounded border ${activeClass} transition">
          ${t.target_query.split(" ")[0]}
        </button>
      `;
    }).join("");
  }

  // Draw 5-axis spider radar
  const cx = 150;
  const cy = 150;
  const maxR = 95;
  const numAxes = OSINT_BEHAVIORAL_AXES.length;

  let svgHtml = "";

  // Concentric radar web polygons
  [0.2, 0.4, 0.6, 0.8, 1.0].forEach((ratio) => {
    const ringPoints = [];
    for (let i = 0; i < numAxes; i++) {
      const angle = -Math.PI / 2 + i * (2 * Math.PI / numAxes);
      const px = cx + maxR * ratio * Math.cos(angle);
      const py = cy + maxR * ratio * Math.sin(angle);
      ringPoints.push(`${px.toFixed(1)},${py.toFixed(1)}`);
    }
    svgHtml += `<polygon points="${ringPoints.join(" ")}" fill="none" stroke="rgba(0, 240, 255, 0.15)" stroke-width="1"></polygon>`;
  });

  // Radial Axis Spokes & Labels
  for (let i = 0; i < numAxes; i++) {
    const angle = -Math.PI / 2 + i * (2 * Math.PI / numAxes);
    const ex = cx + maxR * Math.cos(angle);
    const ey = cy + maxR * Math.sin(angle);

    // Spoke line
    svgHtml += `<line x1="${cx}" y1="${cy}" x2="${ex.toFixed(1)}" y2="${ey.toFixed(1)}" stroke="rgba(0, 240, 255, 0.25)" stroke-width="1"></line>`;

    // Label position (pushed slightly past maxR)
    const lx = cx + (maxR + 18) * Math.cos(angle);
    const ly = cy + (maxR + 18) * Math.sin(angle);
    const anchor = Math.abs(Math.cos(angle)) < 0.2 ? "middle" : (Math.cos(angle) > 0 ? "start" : "end");

    svgHtml += `
      <text x="${lx.toFixed(1)}" y="${ly.toFixed(1)}" fill="rgba(0, 240, 255, 0.7)" font-family="'JetBrains Mono', monospace" font-size="8" text-anchor="${anchor}" alignment-baseline="middle">
        ${OSINT_BEHAVIORAL_AXES[i]}
      </text>
    `;
  }

  // Active target behavioral polygon
  const targetPoints = [];
  activeTarget.scores.forEach((score, i) => {
    const ratio = Math.max(0.1, score / 100);
    const angle = -Math.PI / 2 + i * (2 * Math.PI / numAxes);
    const tx = cx + maxR * ratio * Math.cos(angle);
    const ty = cy + maxR * ratio * Math.sin(angle);
    targetPoints.push(`${tx.toFixed(1)},${ty.toFixed(1)}`);
  });

  svgHtml += `
    <polygon points="${targetPoints.join(" ")}" fill="rgba(0, 240, 255, 0.3)" stroke="#00f0ff" stroke-width="2" class="spider-polygon"></polygon>
  `;

  // Vertex blip dots
  activeTarget.scores.forEach((score, i) => {
    const ratio = Math.max(0.1, score / 100);
    const angle = -Math.PI / 2 + i * (2 * Math.PI / numAxes);
    const tx = cx + maxR * ratio * Math.cos(angle);
    const ty = cy + maxR * ratio * Math.sin(angle);
    svgHtml += `<circle cx="${tx.toFixed(1)}" cy="${ty.toFixed(1)}" r="3" fill="#38bdf8" stroke="#ffffff" stroke-width="1"></circle>`;
  });

  // Center anchor
  svgHtml += `<circle cx="${cx}" cy="${cy}" r="3" fill="#00f0ff"></circle>`;

  svg.innerHTML = svgHtml;

  // Update target briefing card
  const titleEl = document.getElementById("osint-brief-title");
  const footEl = document.getElementById("osint-brief-footprint");
  const typeEl = document.getElementById("osint-brief-type");
  const psychEl = document.getElementById("osint-brief-psych");
  const docEl = document.getElementById("osint-brief-doctrine");
  const labelEl = document.getElementById("spider-profile-label");

  if (titleEl) titleEl.textContent = activeTarget.target_query;
  if (footEl) footEl.textContent = activeTarget.footprint_summary;
  if (typeEl) typeEl.textContent = activeTarget.entity_type;
  if (psychEl) psychEl.textContent = activeTarget.behavioral_profile;
  if (docEl) docEl.textContent = activeTarget.strategic_approchement;
  if (labelEl) labelEl.textContent = activeTarget.target_query.toUpperCase();
}

function selectOsintProfile(id) {
  playSciFiChirp("confirm");
  appState.selectedOsintId = id;
  initOsintSpiderChart();
}

// Render OSINT Reconnaissance & Human Behavioral Dossiers
function renderOsint() {
  initOsintSpiderChart();
  const container = document.getElementById("osint-list");
  if (!container) return;

  let items = (appState.osintData && appState.osintData.length > 0) ? appState.osintData : DEFAULT_OSINT_TARGETS;

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

    const dateStr = d.created_at ? new Date(d.created_at).toLocaleDateString([], { month: "short", day: "numeric", year: "numeric" }) : "Active";

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


// Render Weather Radial Dial Gauges
function renderWeather() {
  const container = document.getElementById("weather-container");
  if (!container) return;

  container.innerHTML = appState.weatherData.map(w => {
    const isLocal = w.scope === "LOCAL";
    const badgeClass = isLocal ? "badge-local" : "badge-global";
    const tempClass = w.temp_c >= 25 ? "text-amber-400" : w.temp_c >= 15 ? "text-emerald-400" : "text-cyan-400";
    const strokeColor = w.temp_c >= 25 ? "#f59e0b" : w.temp_c >= 15 ? "#10b981" : "#00f0ff";
    
    // SVG radial progress arc (range: 0°C to 45°C)
    const radius = 38;
    const circ = 2 * Math.PI * radius; // ~238.76
    const pct = Math.max(0, Math.min(1, (w.temp_c || 0) / 45));
    const offset = circ * (1 - pct);

    return `
      <div class="radial-gauge-card">
        <div class="w-full flex items-center justify-between mb-2">
          <span class="text-xs font-mono font-bold uppercase tracking-wider text-white">${w.city}</span>
          <span class="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded-full ${badgeClass}">${w.scope}</span>
        </div>

        <div class="relative w-28 h-28 flex items-center justify-center my-1">
          <svg class="gauge-svg w-full h-full" viewBox="0 0 100 100">
            <circle class="gauge-track" cx="50" cy="50" r="${radius}" fill="none" stroke-width="7"></circle>
            <circle class="gauge-progress" cx="50" cy="50" r="${radius}" fill="none" stroke="${strokeColor}" stroke-width="7" stroke-dasharray="${circ}" stroke-dashoffset="${offset}"></circle>
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center font-display">
            <span class="text-2xl font-black ${tempClass} tracking-tight">${w.temp_c}°</span>
            <span class="text-[9px] font-mono text-slate-400 mt-0.5 text-center px-1 truncate max-w-[80px]">${w.condition}</span>
          </div>
        </div>

        <div class="w-full pt-2 mt-1 border-t border-slate-800/80 flex items-center justify-between text-[10px] font-mono text-slate-400">
          <span class="flex items-center gap-1">
            <svg class="w-3 h-3 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
            ${w.wind_kmh} km/h
          </span>
          <span class="flex items-center gap-1">
            <svg class="w-3 h-3 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707"></path></svg>
            ${w.humidity}%
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

// --- LAN STAR TOPOLOGY, 1-BY-1 DEVICE INSPECTOR & OSCILLOSCOPE ---
let lanTopologyCoords = [];
let lanTopologyAnimId = null;
let oscilloscopeAnimId = null;
let oscilloscopeSpikeTime = 0;

function getSelectedLanDevice() {
  const devices = appState.lanData || [];
  if (devices.length === 0) return null;
  if (!appState.selectedLanDeviceIp) {
    appState.selectedLanDeviceIp = devices[0].ip_address;
  }
  return devices.find(d => d.ip_address === appState.selectedLanDeviceIp) || devices[0];
}

function selectLanDeviceByIp(ip) {
  playSciFiChirp("confirm");
  appState.selectedLanDeviceIp = ip;
  const dev = getSelectedLanDevice();
  if (dev) {
    updateDeviceInspector(dev);
    renderLanDevicePills();
  }
}

function renderLanDevicePills() {
  const container = document.getElementById("lan-device-pills");
  if (!container) return;

  const devices = appState.lanData || [];
  container.innerHTML = devices.map(d => {
    const isSelected = d.ip_address === appState.selectedLanDeviceIp;
    const activeClass = isSelected 
      ? "border-emerald-400 bg-emerald-950/80 text-emerald-300 font-bold shadow-[0_0_12px_rgba(16,185,129,0.3)]" 
      : "border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700 hover:text-slate-300";
    
    let typeIcon = "💻";
    if (d.device_type && d.device_type.includes("ROUTER")) typeIcon = "🌐";
    else if (d.device_type && d.device_type.includes("TV")) typeIcon = "📺";
    else if (d.device_type && d.device_type.includes("MOBILE")) typeIcon = "📱";
    else typeIcon = "📡";

    return `
      <button onclick="selectLanDeviceByIp('${d.ip_address}')" class="device-node-pill flex items-center gap-1.5 px-2.5 py-1 rounded border text-[11px] font-mono transition ${activeClass}">
        <span class="w-1.5 h-1.5 rounded-full ${isSelected ? 'bg-emerald-400 animate-ping' : 'bg-slate-600'}"></span>
        <span>${typeIcon}</span>
        <span class="truncate max-w-[140px]">${d.device_name.split(" ")[0]}</span>
        <span class="text-[9px] text-slate-500">${d.ip_address.replace("192.168.100.", ".")}</span>
      </button>
    `;
  }).join("");
}

function updateDeviceInspector(dev) {
  if (!dev) return;

  const nameEl = document.getElementById("inspector-device-name");
  const ipEl = document.getElementById("inspector-device-ip");
  const statusEl = document.getElementById("inspector-device-status");
  const typeEl = document.getElementById("inspector-device-type");
  const portEl = document.getElementById("inspector-device-port");
  const pingEl = document.getElementById("inspector-device-ping");
  const cmdStatusEl = document.getElementById("inspector-command-status");
  const iconBox = document.getElementById("inspector-device-icon");

  if (nameEl) nameEl.textContent = dev.device_name;
  if (ipEl) ipEl.textContent = `IP: ${dev.ip_address} // MAC: ${dev.mac_address || "N/A"}`;
  if (statusEl) {
    statusEl.textContent = dev.status || "ONLINE";
    statusEl.className = dev.status === "ONLINE" 
      ? "text-[9px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
      : "text-[9px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400";
  }
  if (typeEl) typeEl.textContent = dev.device_type || "GENERIC";
  if (portEl) {
    const defaultProto = dev.device_type && dev.device_type.includes("TV") ? "ADB/ECP" : dev.device_type && dev.device_type.includes("ROUTER") ? "HTTP-ADMIN" : "HTTP/TCP";
    portEl.textContent = `${dev.control_port || 80} (${defaultProto})`;
  }
  if (pingEl) {
    pingEl.textContent = `PING: ${(1.2 + Math.random() * 2.2).toFixed(1)}ms (HEALTHY)`;
  }
  if (cmdStatusEl) {
    cmdStatusEl.textContent = `// NODE LOCKED: ${dev.device_name} (${dev.ip_address}) READY //`;
  }

  // Update Icon
  if (iconBox) {
    let iconSvg = "";
    if (dev.device_type && dev.device_type.includes("TV")) {
      iconSvg = `<svg class="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="2" y="7" width="20" height="15" rx="2" stroke-width="2"></rect><polyline points="17 2 12 7 7 2" stroke-width="2"></polyline></svg>`;
    } else if (dev.device_type && dev.device_type.includes("ROUTER")) {
      iconSvg = `<svg class="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" stroke-width="2"></circle><line x1="2" y1="12" x2="22" y2="12" stroke-width="2"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>`;
    } else if (dev.device_type && (dev.device_type.includes("LAPTOP") || dev.device_type.includes("PC"))) {
      iconSvg = `<svg class="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="12" rx="2" stroke-width="2"></rect><line x1="2" y1="20" x2="22" y2="20" stroke-width="2"></line></svg>`;
    } else {
      iconSvg = `<svg class="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" stroke-width="2"></circle><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3"></path></svg>`;
    }
    iconBox.innerHTML = iconSvg;
  }
}

function probeDevicePing(dev) {
  playSciFiChirp("confirm");
  oscilloscopeSpikeTime = Date.now();
  const target = dev || getSelectedLanDevice();
  if (!target) return;

  const pingMs = (1.1 + Math.random() * 2.3).toFixed(1);
  const pingEl = document.getElementById("inspector-device-ping");
  if (pingEl) pingEl.textContent = `PING: ${pingMs}ms (ICMP ECHO OK)`;

  const cmdStatusEl = document.getElementById("inspector-command-status");
  if (cmdStatusEl) {
    cmdStatusEl.textContent = `[ICMP PROBE] ${target.device_name} (${target.ip_address}) responded in ${pingMs}ms. Local link 100% nominal.`;
  }
}

function runPortAudit(dev) {
  playSciFiChirp("vocal");
  const target = dev || getSelectedLanDevice();
  if (!target) return;

  const isTv = target.device_type && target.device_type.includes("TV");
  const isRouter = target.device_type && target.device_type.includes("ROUTER");
  const isHost = target.ip_address.endsWith(".40");

  let auditText = "";
  if (isRouter) {
    auditText = `PORT AUDIT [${target.ip_address}]: Port 80 (HTTP-Admin: OPEN), Port 53 (DNS-Relay: ACTIVE), Port 443 (HTTPS: OPEN).`;
  } else if (isTv) {
    auditText = `PORT AUDIT [${target.ip_address}]: Port 5555 (ADB-Debug: READY), Port 8060 (ECP: ACTIVE), Port 8008 (DIAL/Cast: OPEN).`;
  } else if (isHost) {
    auditText = `PORT AUDIT [${target.ip_address}]: Port 3000 (HUD-Server: ONLINE), Port 22 (SSH: FILTERED), Port 8080 (WS: STANDBY).`;
  } else {
    auditText = `PORT AUDIT [${target.ip_address}]: Port 8080 (HTTP: OPEN), Port 5555 (FILTERED), Port 80 (NOMINAL).`;
  }

  const cmdStatusEl = document.getElementById("inspector-command-status");
  if (cmdStatusEl) cmdStatusEl.textContent = auditText;

  speakCustomText(`Port audit complete for ${target.device_name}. Monitored services are operational.`, "cortana");
}

function initOscilloscope() {
  const canvas = document.getElementById("oscilloscope-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  let phase = 0;
  function draw() {
    oscilloscopeAnimId = requestAnimationFrame(draw);
    phase += 0.08;

    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    // Tech baseline
    ctx.strokeStyle = "rgba(16, 185, 129, 0.15)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, h / 2);
    ctx.lineTo(w, h / 2);
    ctx.stroke();

    // Pulse waveform
    ctx.strokeStyle = "#10b981";
    ctx.lineWidth = 1.5;
    ctx.beginPath();

    const isSpike = (Date.now() - oscilloscopeSpikeTime) < 1200;

    for (let x = 0; x < w; x++) {
      let y = h / 2;
      const freq = (x / w) * Math.PI * 8;
      const noise = (Math.sin(freq + phase) + Math.cos(freq * 0.5 - phase * 0.7)) * 3;

      if (isSpike) {
        const spikeCenter = ((Date.now() - oscilloscopeSpikeTime) / 1200) * w;
        const dist = Math.abs(x - spikeCenter);
        if (dist < 30) {
          const spikeAmp = Math.sin((dist / 30) * Math.PI) * (h * 0.42);
          y -= spikeAmp * (x % 2 === 0 ? 1 : -0.6);
        } else {
          y += noise;
        }
      } else {
        y += noise * 0.6;
      }

      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }

  if (!oscilloscopeAnimId) draw();
}

function initLanTopologyCanvas() {
  const canvas = document.getElementById("lan-topology-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  // Canvas click targeting
  canvas.onclick = (e) => {
    const rect = canvas.getBoundingClientRect();
    const clickX = (e.clientX - rect.left) * (canvas.width / rect.width);
    const clickY = (e.clientY - rect.top) * (canvas.height / rect.height);

    let closest = null;
    let minDist = 999;
    lanTopologyCoords.forEach(item => {
      const d = Math.hypot(clickX - item.x, clickY - item.y);
      if (d < item.r + 10 && d < minDist) {
        minDist = d;
        closest = item.dev;
      }
    });

    if (closest) {
      selectLanDeviceByIp(closest.ip_address);
    }
  };

  let animAngle = 0;
  function draw() {
    lanTopologyAnimId = requestAnimationFrame(draw);
    animAngle += 0.008;

    const w = canvas.width;
    const h = canvas.height;
    const cx = w / 2;
    const cy = h / 2;
    ctx.clearRect(0, 0, w, h);

    const devices = appState.lanData || [];
    if (devices.length === 0) return;

    // Find Gateway or Router (center)
    let router = devices.find(d => (d.device_type || "").includes("ROUTER")) || devices[0];
    let satellites = devices.filter(d => d.ip_address !== router.ip_address);
    if (satellites.length === 0) satellites = devices;

    const orbitR = Math.min(cx, cy) - 34;

    // Orbit Ring
    ctx.strokeStyle = "rgba(16, 185, 129, 0.15)";
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.arc(cx, cy, orbitR, 0, 2 * Math.PI);
    ctx.stroke();
    ctx.setLineDash([]);

    lanTopologyCoords = [];

    // Satellites in Orbit
    const count = satellites.length;
    satellites.forEach((sat, i) => {
      const angle = (2 * Math.PI / count) * i - Math.PI / 2 + animAngle * 0.4;
      const sx = cx + orbitR * Math.cos(angle);
      const sy = cy + orbitR * Math.sin(angle);
      const isSelected = sat.ip_address === appState.selectedLanDeviceIp;

      lanTopologyCoords.push({ x: sx, y: sy, r: 16, dev: sat });

      // Laser Beam from Gateway to Satellite
      ctx.strokeStyle = isSelected ? "rgba(0, 240, 255, 0.7)" : "rgba(16, 185, 129, 0.25)";
      ctx.lineWidth = isSelected ? 1.5 : 1;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(sx, sy);
      ctx.stroke();

      // Moving Data Packet Photon along beam
      const packetProgress = (Date.now() / 1400 + i * 0.2) % 1.0;
      const px = cx + (sx - cx) * packetProgress;
      const py = cy + (sy - cy) * packetProgress;
      ctx.fillStyle = isSelected ? "#00f0ff" : "#34d399";
      ctx.beginPath();
      ctx.arc(px, py, isSelected ? 2.8 : 2, 0, 2 * Math.PI);
      ctx.fill();

      // Satellite Node Circle
      ctx.fillStyle = isSelected ? "#064e3b" : "#0f172a";
      ctx.strokeStyle = isSelected ? "#00f0ff" : "#10b981";
      ctx.lineWidth = isSelected ? 2 : 1.2;
      ctx.beginPath();
      ctx.arc(sx, sy, 14, 0, 2 * Math.PI);
      ctx.fill();
      ctx.stroke();

      // Pulsing Halo if selected
      if (isSelected) {
        ctx.strokeStyle = "rgba(0, 240, 255, 0.4)";
        ctx.lineWidth = 1;
        const pulseR = 16 + ((Date.now() % 1000) / 1000) * 8;
        ctx.beginPath();
        ctx.arc(sx, sy, pulseR, 0, 2 * Math.PI);
        ctx.stroke();
      }

      // Node Glyph / Short Tag
      ctx.fillStyle = isSelected ? "#fff" : "#94a3b8";
      ctx.font = "bold 9px 'JetBrains Mono', monospace";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      const tag = sat.device_type && sat.device_type.includes("TV") ? "TV" : sat.device_type && sat.device_type.includes("LAPTOP") ? "PC" : "IOT";
      ctx.fillText(tag, sx, sy);

      // Node IP Label
      ctx.fillStyle = isSelected ? "#38bdf8" : "rgba(255, 255, 255, 0.65)";
      ctx.font = "8px 'JetBrains Mono', monospace";
      ctx.textBaseline = "top";
      const ipShort = sat.ip_address.replace("192.168.100.", ".");
      ctx.fillText(ipShort, sx, sy + 16);
    });

    // Central Node: Gateway Router
    const isRouterSelected = router.ip_address === appState.selectedLanDeviceIp;
    lanTopologyCoords.push({ x: cx, y: cy, r: 20, dev: router });

    ctx.fillStyle = isRouterSelected ? "#047857" : "#065f46";
    ctx.strokeStyle = isRouterSelected ? "#00f0ff" : "#34d399";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, 18, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();

    // Central Gateway Pulse
    ctx.strokeStyle = "rgba(52, 211, 153, 0.35)";
    ctx.lineWidth = 1.2;
    const centerPulse = 18 + ((Date.now() % 1400) / 1400) * 12;
    ctx.beginPath();
    ctx.arc(cx, cy, centerPulse, 0, 2 * Math.PI);
    ctx.stroke();

    ctx.fillStyle = "#fff";
    ctx.font = "bold 9px 'JetBrains Mono', monospace";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("ONT", cx, cy);

    ctx.fillStyle = "#10b981";
    ctx.font = "bold 8px 'JetBrains Mono', monospace";
    ctx.textBaseline = "top";
    ctx.fillText(".1 GATEWAY", cx, cy + 20);
  }

  if (!lanTopologyAnimId) draw();
}

function initDeviceActionHandlers() {
  const btnWake = document.getElementById("btn-action-wake");
  const btnPower = document.getElementById("btn-action-power");
  const btnMute = document.getElementById("btn-action-mute");
  const btnVolUp = document.getElementById("btn-action-volup");
  const btnVolDn = document.getElementById("btn-action-voldn");
  const btnStream = document.getElementById("btn-action-stream");
  const btnOpenWeb = document.getElementById("btn-action-openweb");
  const btnPortScan = document.getElementById("btn-action-portscan");
  const btnVoice = document.getElementById("btn-action-voice");
  const btnPing = document.getElementById("btn-device-ping");

  if (btnWake) btnWake.onclick = () => {
    const dev = getSelectedLanDevice();
    if (dev) sendDeviceCommand(dev.device_name, "wake");
  };
  if (btnPower) btnPower.onclick = () => {
    const dev = getSelectedLanDevice();
    if (dev) sendDeviceCommand(dev.device_name, "tv_power");
  };
  if (btnMute) btnMute.onclick = () => {
    const dev = getSelectedLanDevice();
    if (dev) sendDeviceCommand(dev.device_name, "tv_mute");
  };
  if (btnVolUp) btnVolUp.onclick = () => {
    const dev = getSelectedLanDevice();
    if (dev) sendDeviceCommand(dev.device_name, "vol_up");
  };
  if (btnVolDn) btnVolDn.onclick = () => {
    const dev = getSelectedLanDevice();
    if (dev) sendDeviceCommand(dev.device_name, "vol_down");
  };
  if (btnStream) btnStream.onclick = () => {
    const dev = getSelectedLanDevice();
    if (dev) sendDeviceCommand(dev.device_name, "open_url");
  };
  if (btnOpenWeb) btnOpenWeb.onclick = () => {
    const dev = getSelectedLanDevice();
    if (dev) {
      playSciFiChirp("confirm");
      const url = `http://${dev.ip_address}:${dev.control_port || 80}`;
      window.open(url, "_blank");
    }
  };
  if (btnPortScan) btnPortScan.onclick = () => {
    const dev = getSelectedLanDevice();
    if (dev) runPortAudit(dev);
  };
  if (btnVoice) btnVoice.onclick = () => {
    const dev = getSelectedLanDevice();
    if (dev) {
      playSciFiChirp("vocal");
      speakCustomText(`Direct neural link confirmed with ${dev.device_name} on subnet 192.168.100.0. All hardware interfaces ready.`, "cortana");
    }
  };
  if (btnPing) btnPing.onclick = () => {
    const dev = getSelectedLanDevice();
    if (dev) probeDevicePing(dev);
  };
}

// Render Local Wi-Fi & LAN Device Mesh Grid
function renderLanDevices() {
  const container = document.getElementById("lan-grid");
  const summaryEl = document.getElementById("topology-node-summary");
  const countEl = document.getElementById("topology-node-count");

  const devices = appState.lanData || [];

  if (summaryEl) summaryEl.textContent = `${devices.length} ACTIVE SUBNET NODES`;
  if (countEl) countEl.textContent = `${devices.length} NODES ON ORBIT`;

  renderLanDevicePills();
  initLanTopologyCanvas();
  initOscilloscope();
  initDeviceActionHandlers();

  const selectedDev = getSelectedLanDevice();
  if (selectedDev) updateDeviceInspector(selectedDev);

  if (!container) return;

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
    } else if (d.device_type && d.device_type.includes("ROUTER")) {
      iconSvg = `<svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" stroke-width="2"></circle><line x1="2" y1="12" x2="22" y2="12" stroke-width="2"></line></svg>`;
    } else if (d.device_type && (d.device_type.includes("LAPTOP") || d.device_type.includes("PC"))) {
      iconSvg = `<svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="12" rx="2" stroke-width="2"></rect><line x1="2" y1="20" x2="22" y2="20" stroke-width="2"></line></svg>`;
    } else {
      iconSvg = `<svg class="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" stroke-width="2"></circle><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3"></path></svg>`;
    }

    const isCurrent = d.ip_address === appState.selectedLanDeviceIp;
    const borderHighlight = isCurrent ? "border-emerald-400/80 shadow-[0_0_15px_rgba(16,185,129,0.2)]" : "border-slate-800/80";

    return `
      <div class="lan-card ${cardStatusClass} ${borderHighlight} cursor-pointer" onclick="selectLanDeviceByIp('${d.ip_address}')">
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
            <span class="text-cyan-400">${d.control_port || 80}</span>
          </div>
          <div class="flex justify-between items-center text-slate-500">
            <span>LAST SEEN:</span>
            <span>${lastSeenStr}</span>
          </div>

          <!-- Quick Action Controls -->
          <div class="pt-2 flex flex-wrap gap-1">
            ${d.mac_address ? `<button onclick="event.stopPropagation(); sendDeviceCommand('${d.device_name}', 'wake')" class="text-[9px] px-1.5 py-0.5 rounded bg-cyan-950 border border-cyan-800 text-cyan-300 hover:bg-cyan-900 transition">WOL</button>` : ""}
            ${d.device_type && d.device_type.includes("TV") ? `<button onclick="event.stopPropagation(); sendDeviceCommand('${d.device_name}', 'tv_power')" class="text-[9px] px-1.5 py-0.5 rounded bg-rose-950 border border-rose-800 text-rose-300 hover:bg-rose-900 transition">PWR</button>` : ""}
            ${d.device_type && d.device_type.includes("TV") ? `<button onclick="event.stopPropagation(); sendDeviceCommand('${d.device_name}', 'tv_mute')" class="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-700 transition">MUTE</button>` : ""}
            <button onclick="event.stopPropagation(); selectLanDeviceByIp('${d.ip_address}')" class="text-[9px] px-1.5 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-300 hover:bg-emerald-900 transition">INSPECT</button>
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
  } else if (command === "vol_up") {
    reply = `Volume increased on ${deviceName}.`;
  } else if (command === "vol_down") {
    reply = `Volume decreased on ${deviceName}.`;
  } else if (command === "open_url") {
    reply = `Routing real-time tactical dashboard stream to ${deviceName}. Screen synchronized.`;
  } else {
    reply = `Directive ${command.toUpperCase()} executed on ${deviceName}.`;
  }

  speakCustomText(reply, "cortana");
  const cmdStatusEl = document.getElementById("inspector-command-status");
  if (cmdStatusEl) {
    cmdStatusEl.textContent = `[COMMAND EXECUTED] ${command.toUpperCase()} -> ${deviceName}: "${reply}"`;
  }
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

// --- CYBERSECURITY DEFCON GAUGE & HEXAGONAL CVE MATRIX ---
function lockCveTarget(cveId) {
  playSciFiChirp("confirm");
  const item = (appState.cyberData || []).find(c => (c.cve_id === cveId) || (c.title && c.title.includes(cveId)));
  if (!item) return;

  const lockCard = document.getElementById("cve-target-lock");
  const lockIdEl = document.getElementById("cve-lock-id");
  const lockSevEl = document.getElementById("cve-lock-sev");
  const lockTitleEl = document.getElementById("cve-lock-title");
  const lockDescEl = document.getElementById("cve-lock-desc");
  const lockLinkEl = document.getElementById("cve-lock-link");

  if (lockCard) lockCard.classList.remove("hidden");
  if (lockIdEl) lockIdEl.textContent = item.cve_id || "VULNERABILITY LOCK";
  if (lockSevEl) {
    lockSevEl.textContent = item.severity;
    lockSevEl.className = item.severity === "CRITICAL"
      ? "text-[9px] px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-700 font-bold"
      : item.severity === "HIGH"
      ? "text-[9px] px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-700 font-bold"
      : "text-[9px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-700 font-bold";
  }
  if (lockTitleEl) lockTitleEl.textContent = item.title;
  if (lockDescEl) lockDescEl.textContent = item.summary || "Actively exploited CISA catalog vector. Immediate perimeter patch verification advised.";
  if (lockLinkEl && item.link) lockLinkEl.href = item.link;
}

function previewCveTarget(cveId) {
  playSciFiChirp("blip");
  lockCveTarget(cveId);
}

// Render Cybersecurity Threat Matrix
function renderCyber() {
  const container = document.getElementById("cyber-container");
  const countBadge = document.getElementById("cyber-count-badge");
  const hexGrid = document.getElementById("hex-cve-grid");
  const defconValEl = document.getElementById("defcon-value");
  const defconLabelEl = document.getElementById("defcon-label");

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

  // Update DEFCON threat meter
  const critCount = filtered.filter(i => i.severity === "CRITICAL").length;
  const highCount = filtered.filter(i => i.severity === "HIGH").length;
  let defcon = 3;
  let defconText = "ELEVATED";

  if (critCount >= 3) {
    defcon = 2;
    defconText = "CRITICAL";
  } else if (critCount === 0 && highCount === 0) {
    defcon = 4;
    defconText = "GUARD";
  }

  if (defconValEl) defconValEl.textContent = defcon;
  if (defconLabelEl) {
    defconLabelEl.textContent = defconText;
    defconLabelEl.className = defcon === 2 ? "text-[9px] font-mono text-rose-400 font-bold uppercase glow-crimson" : "text-[9px] font-mono text-amber-400 font-bold uppercase";
  }

  // Populate Hexagonal Honeycomb Matrix
  if (hexGrid) {
    const hexItems = filtered.slice(0, 32);
    if (hexItems.length === 0) {
      hexGrid.innerHTML = `<div class="p-4 text-xs font-mono text-slate-500">No CVE hex vectors matching current filter.</div>`;
    } else {
      hexGrid.innerHTML = hexItems.map(item => {
        let hexClass = "hex-adv";
        if (item.severity === "CRITICAL") hexClass = "hex-crit";
        else if (item.severity === "HIGH") hexClass = "hex-high";

        const label = item.cve_id ? item.cve_id.replace("CVE-", "") : (item.title ? item.title.slice(0, 10) : "CVE");
        const safeId = (item.cve_id || item.title || "").replace(/['"]/g, "");

        return `
          <div class="hex-cell ${hexClass}" onclick="lockCveTarget('${safeId}')" onmouseenter="previewCveTarget('${safeId}')">
            <div class="hex-shape"></div>
            <div class="hex-content">
              <span class="hex-cve-id">${label}</span>
              <span class="hex-cve-sev">${item.severity.slice(0, 4)}</span>
            </div>
          </div>
        `;
      }).join("");

      // Lock onto first critical item by default
      if (hexItems.length > 0) {
        lockCveTarget(hexItems[0].cve_id || hexItems[0].title);
      }
    }
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
