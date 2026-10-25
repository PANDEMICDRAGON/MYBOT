const fs = require('fs');
const path = require('path');

const appJsPath = path.join(__dirname, '..', 'app.js');
let content = fs.readFileSync(appJsPath, 'utf8');

const startMarker = 'function switchHolodeckSimulation(simName, triggerAudio = true) {';
const endMarker = 'function sortByCriticality(items, type = "generic") {';

const startIndex = content.indexOf(startMarker);
const endIndex = content.indexOf(endMarker);

if (startIndex === -1 || endIndex === -1) {
  console.error("Markers not found!", { startIndex, endIndex });
  process.exit(1);
}

const replacementCode = `// ==========================================================================
// SIMULTANEOUS MULTI-FRANCHISE CANVASES ENGINE
// (Prometheus LIDAR, Terminator T-800, God's Eye Satellite, Total Recall Rekall)
// ==========================================================================

// 1. Prometheus Weyland-Yutani 3D LIDAR Contour Scan
let weylandLidarStep = 0;
function initPrometheusLidar() {
  const canvas = document.getElementById("weyland-lidar-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  
  if (!holodeckState.particles || holodeckState.particles.length === 0) {
    initHolodeckParticles();
  }

  function draw() {
    if (!document.getElementById("weyland-lidar-canvas")) return;
    const w = canvas.width;
    const h = canvas.height;
    const cx = w / 2;
    const cy = h / 2;

    weylandLidarStep += 0.02;

    ctx.fillStyle = "rgba(4, 12, 18, 0.35)";
    ctx.fillRect(0, 0, w, h);

    // Grid lines
    ctx.strokeStyle = "rgba(56, 189, 248, 0.08)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let x = 0; x < w; x += 30) { ctx.moveTo(x, 0); ctx.lineTo(x, h); }
    for (let y = 0; y < h; y += 25) { ctx.moveTo(0, y); ctx.lineTo(w, y); }
    ctx.stroke();

    // 3D Particles
    const rotY = weylandLidarStep * 0.4;
    holodeckState.particles.slice(0, 140).forEach(p => {
      let x1 = p.x * Math.cos(rotY) - p.z * Math.sin(rotY);
      let z1 = p.x * Math.sin(rotY) + p.z * Math.cos(rotY);
      const fov = 300;
      const scale = fov / (fov + z1 + 120);
      const px = cx + x1 * scale * 1.3;
      const py = cy + p.y * scale * 0.7;

      ctx.fillStyle = p.baseColor || "#38bdf8";
      ctx.globalAlpha = Math.max(0.2, Math.min(1, (z1 + 150) / 300));
      ctx.beginPath();
      ctx.arc(px, py, (p.size || 1.5) * scale, 0, 2 * Math.PI);
      ctx.fill();
    });
    ctx.globalAlpha = 1;

    // Orbiting LIDAR Pup Drone
    const droneAngle = weylandLidarStep * 1.4;
    const dx = cx + Math.cos(droneAngle) * (w * 0.38);
    const dy = cy + Math.sin(droneAngle * 1.5) * 45;

    ctx.strokeStyle = "rgba(239, 68, 68, 0.45)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(dx, dy);
    ctx.lineTo(cx, cy + 15);
    ctx.stroke();

    ctx.fillStyle = "#ef4444";
    ctx.beginPath();
    ctx.arc(dx, dy, 4, 0, 2 * Math.PI);
    ctx.fill();

    ctx.fillStyle = "#38bdf8";
    ctx.font = "8px 'JetBrains Mono', monospace";
    ctx.fillText("PUP-01 // SCANNING", dx + 6, dy - 4);

    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
}

// 2. Terminator Genisys Cyberdyne Systems T-800 Optical HUD
let t800Step = 0;
function initTerminatorOptical() {
  const canvas = document.getElementById("t800-optical-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  function draw() {
    if (!document.getElementById("t800-optical-canvas")) return;
    const w = canvas.width;
    const h = canvas.height;
    const cx = w / 2;
    const cy = h / 2;

    t800Step += 0.03;

    ctx.fillStyle = "rgba(18, 4, 6, 0.4)";
    ctx.fillRect(0, 0, w, h);

    // Crimson Scanline Grid
    ctx.strokeStyle = "rgba(239, 68, 68, 0.15)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let y = 0; y < h; y += 12) {
      ctx.moveTo(0, y); ctx.lineTo(w, y);
    }
    ctx.stroke();

    // Moving Scan Bar
    const scanY = (t800Step * 80) % h;
    ctx.strokeStyle = "rgba(255, 0, 50, 0.6)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, scanY); ctx.lineTo(w, scanY);
    ctx.stroke();

    // Reticle Target Box
    const tx = cx + Math.sin(t800Step * 0.8) * 30;
    const ty = cy + Math.cos(t800Step * 0.6) * 15;
    ctx.strokeStyle = "#ff0033";
    ctx.lineWidth = 2;
    ctx.strokeRect(tx - 35, ty - 30, 70, 60);

    // Crosshair ticks
    ctx.beginPath();
    ctx.moveTo(tx - 45, ty); ctx.lineTo(tx - 35, ty);
    ctx.moveTo(tx + 35, ty); ctx.lineTo(tx + 45, ty);
    ctx.moveTo(tx, ty - 40); ctx.lineTo(tx, ty - 30);
    ctx.moveTo(tx, ty + 30); ctx.lineTo(tx, ty + 40);
    ctx.stroke();

    ctx.fillStyle = "#ff0033";
    ctx.font = "bold 9px 'JetBrains Mono', monospace";
    ctx.textAlign = "center";
    ctx.fillText("TARGET: ZERO-DAY // THREAT: 99.1%", tx, ty - 36);
    ctx.fillText("DEFCON LEVEL 3 // ARMED", tx, ty + 45);

    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
}

// 3. Furious 7 Ramsey God's Eye Satellite Triangulation
let godsEyeStep = 0;
function initGodsEyeTriangulation() {
  const canvas = document.getElementById("godseye-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const satellites = [
    { name: "SAT-ALPHA", speed: 0.008, rad: 0.85, phase: 0 },
    { name: "SAT-BRAVO", speed: 0.012, rad: 0.72, phase: 1.2 },
    { name: "SAT-CHARLIE", speed: 0.009, rad: 0.60, phase: 2.8 },
    { name: "SAT-DELTA", speed: 0.015, rad: 0.90, phase: 4.1 },
    { name: "SAT-ECHO", speed: 0.011, rad: 0.78, phase: 5.3 }
  ];

  function draw() {
    if (!document.getElementById("godseye-canvas")) return;
    const w = canvas.width;
    const h = canvas.height;
    const cx = w / 2;
    const cy = h / 2 + 10;

    godsEyeStep += 0.03;

    ctx.fillStyle = "rgba(4, 14, 8, 0.35)";
    ctx.fillRect(0, 0, w, h);

    // Earth Curve Arc
    ctx.strokeStyle = "rgba(0, 255, 136, 0.25)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(cx, cy + 180, 220, Math.PI * 1.15, Math.PI * 1.85);
    ctx.stroke();

    // Target Location on Ground
    const targetX = cx + Math.sin(godsEyeStep * 0.4) * 40;
    const targetY = cy - 20;

    // Satellites orbiting & triangulation beams
    satellites.forEach(sat => {
      const angle = (godsEyeStep * sat.speed * 20 + sat.phase) % (2 * Math.PI);
      const rx = (w * 0.42) * sat.rad;
      const ry = 45 * sat.rad;
      const sx = cx + Math.cos(angle) * rx;
      const sy = cy - 50 + Math.sin(angle) * ry;

      // Triangulation vector beam
      ctx.strokeStyle = "rgba(0, 255, 136, 0.25)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(sx, sy);
      ctx.lineTo(targetX, targetY);
      ctx.stroke();

      // Satellite blip
      ctx.fillStyle = "#00ff88";
      ctx.beginPath();
      ctx.arc(sx, sy, 3, 0, 2 * Math.PI);
      ctx.fill();

      ctx.fillStyle = "rgba(0, 255, 136, 0.8)";
      ctx.font = "7px 'JetBrains Mono', monospace";
      ctx.fillText(sat.name, sx + 5, sy - 3);
    });

    // Biometric Target Box
    ctx.strokeStyle = "#00ff88";
    ctx.lineWidth = 1.5;
    ctx.strokeRect(targetX - 18, targetY - 18, 36, 36);

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 8px 'JetBrains Mono', monospace";
    ctx.textAlign = "center";
    ctx.fillText("FACIAL RECON: 99.4%", targetX, targetY - 22);
    ctx.fillText("LOC: KITENGELA", targetX, targetY + 28);

    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
}

// 4. Total Recall Rekall Neural Synapse Matrix
let rekallStep = 0;
function initRekallSynapse() {
  const canvas = document.getElementById("rekall-synapse-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const nodes = [
    { x: 0.12, y: 0.5, label: "M-PESA", color: "#10b981" },
    { x: 0.32, y: 0.3, label: "TASK-01", color: "#f59e0b" },
    { x: 0.50, y: 0.65, label: "CORE REKALL", color: "#a855f7" },
    { x: 0.70, y: 0.35, label: "VOICE VAULT", color: "#06b6d4" },
    { x: 0.88, y: 0.55, label: "USD LEDGER", color: "#3b82f6" }
  ];

  function draw() {
    if (!document.getElementById("rekall-synapse-canvas")) return;
    const w = canvas.width;
    const h = canvas.height;

    rekallStep += 0.03;

    ctx.fillStyle = "rgba(12, 6, 20, 0.35)";
    ctx.fillRect(0, 0, w, h);

    // Draw Synaptic Connections
    ctx.lineWidth = 1.5;
    for (let i = 0; i < nodes.length - 1; i++) {
      const n1 = nodes[i];
      const n2 = nodes[i + 1];
      const x1 = n1.x * w;
      const y1 = n1.y * h + Math.sin(rekallStep + i) * 6;
      const x2 = n2.x * w;
      const y2 = n2.y * h + Math.cos(rekallStep + i) * 6;

      ctx.strokeStyle = "rgba(168, 85, 247, 0.35)";
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();

      // Pulse traveling along synapse
      const pulseT = (rekallStep * 1.5 + i * 0.4) % 1;
      const px = x1 + (x2 - x1) * pulseT;
      const py = y1 + (y2 - y1) * pulseT;
      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.arc(px, py, 2, 0, 2 * Math.PI);
      ctx.fill();
    }

    // Draw Synapse Nodes
    nodes.forEach((n, idx) => {
      const nx = n.x * w;
      const ny = n.y * h + Math.sin(rekallStep + idx) * 6;

      ctx.fillStyle = n.color;
      ctx.beginPath();
      ctx.arc(nx, ny, 5, 0, 2 * Math.PI);
      ctx.fill();

      ctx.strokeStyle = "rgba(255, 255, 255, 0.4)";
      ctx.beginPath();
      ctx.arc(nx, ny, 8, 0, 2 * Math.PI);
      ctx.stroke();

      ctx.fillStyle = "#ffffff";
      ctx.font = "8px 'JetBrains Mono', monospace";
      ctx.textAlign = "center";
      ctx.fillText(n.label, nx, ny - 10);
    });

    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
}

function initSimultaneousSciFiCanvases() {
  initPrometheusLidar();
  initTerminatorOptical();
  initGodsEyeTriangulation();
  initRekallSynapse();
}

function initHolodeckEngine() {
  initSimultaneousSciFiCanvases();
}

// ==========================================================================
// CRITICALITY SORTING ENGINE (PRIORITIZES HIGHEST THREAT / IMPACT TELEMETRY)
// ==========================================================================
`;

const newContent = content.slice(0, startIndex) + replacementCode + content.slice(endIndex + endMarker.length);
fs.writeFileSync(appJsPath, newContent, 'utf8');
console.log("Successfully replaced holodeck engine with simultaneous sci-fi multi-canvas engines!");
