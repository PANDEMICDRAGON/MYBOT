const fs = require('fs');

let code = fs.readFileSync('app.js', 'utf8');

// 1. Update renderSitRep to sync modalBody
const oldSitrep = `  if (contentEl) contentEl.textContent = appState.sitrepText || "Awaiting cognitive synthesis...";
  if (timeEl) timeEl.textContent = \`Generated: \${new Date().toLocaleTimeString()} // Voice Ready\`;`;

const newSitrep = `  if (contentEl) contentEl.textContent = appState.sitrepText || "Awaiting cognitive synthesis...";
  if (timeEl) timeEl.textContent = \`Generated: \${new Date().toLocaleTimeString()} // Voice Ready\`;
  const modalBody = document.getElementById("sitrep-modal-body");
  if (modalBody) modalBody.textContent = appState.sitrepText || "No classified SitRep intelligence generated yet. Transmit a directive or voice query to populate.";`;

code = code.replace(oldSitrep, newSitrep);

// 2. Make renderOsint visual and compact with collapsible full details
const oldOsintCard = `        <div class="space-y-3 text-xs">
          <div>
            <span class="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider block">1. OSINT & Public Record Footprint</span>
            <p class="text-slate-300 leading-relaxed mt-1 font-sans">\${escapeHtml(d.footprint_summary || '')}</p>
          </div>
          <div class="bg-amber-950/20 border-l-2 border-amber-400 p-3 rounded-r">
            <span class="text-[10px] font-mono font-bold text-amber-400 uppercase tracking-wider block">2. Behavioral & Psychological Profile</span>
            <p class="text-slate-200 leading-relaxed mt-1 font-sans">\${escapeHtml(d.behavioral_profile || '')}</p>
          </div>
          <div class="bg-emerald-950/20 border-l-2 border-emerald-400 p-3 rounded-r">
            <span class="text-[10px] font-mono font-bold text-emerald-400 uppercase tracking-wider block">3. Strategic Playbook & Interaction Leverage</span>
            <p class="text-slate-200 leading-relaxed mt-1 font-sans">\${escapeHtml(d.strategic_approchement || 'N/A')}</p>
          </div>
          \${linksHtml ? \`<div class="pt-2 border-t border-slate-800/60 space-y-1"><span class="text-[10px] font-mono font-bold text-slate-500 uppercase block">Discovered Nodes & Footprint:</span>\${linksHtml}</div>\` : ""}
        </div>`;

const newOsintCard = `        <!-- Visual Telemetry Gauges -->
        <div class="grid grid-cols-3 gap-2 py-1 font-mono text-[9px]">
          <div class="p-2 rounded bg-slate-900/90 border border-slate-800 text-center">
            <span class="text-slate-500 block">FOOTPRINT</span>
            <span class="text-cyan-400 font-bold">88.4%</span>
            <div class="w-full bg-slate-950 h-1 rounded overflow-hidden mt-1"><div class="bg-cyan-400 h-full w-[88%]"></div></div>
          </div>
          <div class="p-2 rounded bg-slate-900/90 border border-slate-800 text-center">
            <span class="text-slate-500 block">PSYCH LEVERAGE</span>
            <span class="text-amber-400 font-bold">94.1%</span>
            <div class="w-full bg-slate-950 h-1 rounded overflow-hidden mt-1"><div class="bg-amber-400 h-full w-[94%]"></div></div>
          </div>
          <div class="p-2 rounded bg-slate-900/90 border border-slate-800 text-center">
            <span class="text-slate-500 block">VK-PROBABILITY</span>
            <span class="text-emerald-400 font-bold">LOW RISK</span>
            <div class="w-full bg-slate-950 h-1 rounded overflow-hidden mt-1"><div class="bg-emerald-400 h-full w-[25%]"></div></div>
          </div>
        </div>

        <!-- Compact Key Takeaway -->
        <p class="text-xs text-slate-200 font-sans line-clamp-2 leading-relaxed">
          \${escapeHtml(d.footprint_summary || d.behavioral_profile || 'Classified surveillance dossier.')}
        </p>

        <!-- Collapsible Full Dossier (Eliminates Walls of Text) -->
        <details class="group border border-slate-800/80 rounded bg-slate-900/60 p-2.5 transition">
          <summary class="cursor-pointer text-[10px] font-mono font-bold text-amber-400 hover:text-amber-300 flex items-center justify-between select-none">
            <span class="flex items-center gap-1.5">
              <span class="group-open:rotate-90 transition-transform inline-block">▶</span>
              <span>CLASSIFIED DOSSIER &amp; PSYCHOLOGICAL PLAYBOOK</span>
            </span>
            <span class="text-slate-500 text-[9px]">[TOGGLE DOSSIER]</span>
          </summary>
          <div class="space-y-2.5 pt-3 text-xs mt-2 border-t border-slate-800">
            <div>
              <span class="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider block">1. OSINT &amp; Public Record Footprint</span>
              <p class="text-slate-300 leading-relaxed mt-0.5 font-sans">\${escapeHtml(d.footprint_summary || '')}</p>
            </div>
            <div class="bg-amber-950/20 border-l-2 border-amber-400 p-2.5 rounded-r">
              <span class="text-[10px] font-mono font-bold text-amber-400 uppercase tracking-wider block">2. Behavioral &amp; Psychological Profile</span>
              <p class="text-slate-200 leading-relaxed mt-0.5 font-sans">\${escapeHtml(d.behavioral_profile || '')}</p>
            </div>
            <div class="bg-emerald-950/20 border-l-2 border-emerald-400 p-2.5 rounded-r">
              <span class="text-[10px] font-mono font-bold text-emerald-400 uppercase tracking-wider block">3. Strategic Playbook &amp; Interaction Leverage</span>
              <p class="text-slate-200 leading-relaxed mt-0.5 font-sans">\${escapeHtml(d.strategic_approchement || 'N/A')}</p>
            </div>
            \${linksHtml ? \`<div class="pt-2 border-t border-slate-800/60 space-y-1"><span class="text-[10px] font-mono font-bold text-slate-500 uppercase block">Discovered Nodes &amp; Footprint:</span>\${linksHtml}</div>\` : ""}
          </div>
        </details>`;

if (code.includes('1. OSINT & Public Record Footprint')) {
  // Replace the card body inside renderOsint
  code = code.replace(oldOsintCard, newOsintCard);
  console.log("Updated OSINT card to compact visual layout!");
} else {
  console.log("OSINT card marker not found directly, checking variations...");
}

fs.writeFileSync('app.js', code, 'utf8');
console.log("Completed optimize_renderers.js");
