import re

def update_app_js():
    with open("app.js", "r", encoding="utf-8") as f:
        content = f.read()

    # Normalize CRLF to LF for consistent matching and editing
    content = content.replace("\r\n", "\n")

    # 1. Update appState
    old_state = '  newsData: [],\n  cyberData: [],'
    new_state = '  newsData: [],\n  topicDeepDives: [],\n  cyberData: [],'
    if old_state in content:
        content = content.replace(old_state, new_state, 1)
        print("Updated appState.")
    else:
        print("Warning: old_state not found.")

    # 2. Update fetchLiveTelemetryFile
    old_telemetry = '      if (Array.isArray(data.news) && data.news.length > 0) appState.newsData = data.news;'
    new_telemetry = ('      if (Array.isArray(data.news) && data.news.length > 0) appState.newsData = data.news;\n'
                     '      if (Array.isArray(data.topic_deep_dives) && data.topic_deep_dives.length > 0) appState.topicDeepDives = data.topic_deep_dives;')
    if old_telemetry in content:
        content = content.replace(old_telemetry, new_telemetry, 1)
        print("Updated fetchLiveTelemetryFile.")
    else:
        print("Warning: old_telemetry not found.")

    # 3. Add renderTopicDeepDives in render sequences
    content = content.replace("    renderPersonalOps();\n    renderNews();",
                              "    renderPersonalOps();\n    renderTopicDeepDives();\n    renderNews();")
    print("Added renderTopicDeepDives() to sync blocks.")

    # 4. Add renderTopicDeepDives() to news-tab click and search input
    content = content.replace('      appState.activeNewsFilter = tab.getAttribute("data-scope");\n      renderNews();',
                              '      appState.activeNewsFilter = tab.getAttribute("data-scope");\n      renderTopicDeepDives();\n      renderNews();')
    
    content = content.replace('      appState.searchQuery = e.target.value;\n      renderNews();',
                              '      appState.searchQuery = e.target.value;\n      renderTopicDeepDives();\n      renderNews();')
    print("Added renderTopicDeepDives() to events.")

    # 5. Define renderTopicDeepDives and upgraded renderNews
    new_render_blocks = '''// Render Active Theater Topic Deep Dives
function renderTopicDeepDives() {
  const container = document.getElementById("topic-deep-dives-container");
  if (!container) return;

  const dives = appState.topicDeepDives || [];
  if (!dives || dives.length === 0) {
    container.innerHTML = "";
    return;
  }

  const query = (appState.searchQuery || "").toLowerCase();
  const filtered = dives.filter(d => {
    if (!query) return true;
    return (d.subject || "").toLowerCase().includes(query) ||
           (d.in_depth_context || "").toLowerCase().includes(query) ||
           (d.latest_developments || "").toLowerCase().includes(query);
  });

  if (filtered.length === 0) {
    container.innerHTML = "";
    return;
  }

  container.innerHTML = `
    <div class="p-4 rounded-lg bg-slate-950/80 border border-cyan-500/40 shadow-xl mb-4">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-cyan-500/20 mb-3 gap-2">
        <div class="flex items-center gap-2">
          <span class="inline-block w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse"></span>
          <h3 class="text-xs font-mono font-bold tracking-widest text-cyan-300 uppercase">
            ACTIVE THEATER TOPIC DEEP-DIVES // POST-SWEEP COGNITIVE INTELLIGENCE
          </h3>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/30">
            ${filtered.length} ACTIVE SUBJECTS
          </span>
          <span class="text-[10px] font-mono text-slate-400">NON-REPETITIVE ADAPTIVE SWEEPS</span>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-3.5">
        ${filtered.map(d => {
          const theater = d.theater || "GLOBAL";
          let theaterBadge = "border-cyan-500/30 text-cyan-300 bg-cyan-950/50";
          if (theater === "CYBER") theaterBadge = "border-violet-500/30 text-violet-300 bg-violet-950/50";
          if (theater === "RED-SEA-MIDEAST") theaterBadge = "border-amber-500/30 text-amber-300 bg-amber-950/50";
          if (theater === "EAST-AFRICA") theaterBadge = "border-emerald-500/30 text-emerald-300 bg-emerald-950/50";

          const subjectEsc = escapeHtml(d.subject || "Tactical Subject");
          const subjectAttr = (d.subject || "").replace(/"/g, '&quot;').replace(/'/g, "\\\\'");

          return `
            <div class="rounded-md border border-slate-800 bg-slate-900/60 p-3.5 hover:border-cyan-500/40 transition-all flex flex-col justify-between">
              <div>
                <div class="flex items-center justify-between gap-2 mb-2">
                  <div class="flex items-center gap-2">
                    <span class="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border ${theaterBadge}">
                      ${theater}
                    </span>
                    <h4 class="text-xs font-bold text-white font-display">${subjectEsc}</h4>
                  </div>
                  <button onclick="window.triggerSubjectDeepDive('${subjectAttr}', '${theater}')"
                          title="Transmit instant research directive to neural construct"
                          class="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 hover:bg-cyan-900 text-cyan-300 border border-cyan-500/40 transition-colors flex items-center gap-1 shrink-0">
                    ⚡ DEEP DIVE
                  </button>
                </div>

                ${d.latest_developments ? `
                  <div class="mb-2">
                    <span class="text-[9px] font-mono text-cyan-400 font-bold uppercase tracking-wider block mb-0.5">LATEST DEVELOPMENTS:</span>
                    <p class="text-[11px] text-slate-300 leading-snug font-sans">${escapeHtml(d.latest_developments)}</p>
                  </div>
                ` : ""}

                ${d.in_depth_context ? `
                  <div class="mb-2">
                    <span class="text-[9px] font-mono text-purple-400 font-bold uppercase tracking-wider block mb-0.5">IN-DEPTH CONTEXT & SECOND-ORDER RIPPLES:</span>
                    <p class="text-[11px] text-slate-400 leading-snug font-sans">${escapeHtml(d.in_depth_context)}</p>
                  </div>
                ` : ""}
              </div>

              ${d.why_it_matters ? `
                <div class="mt-2 pt-2 border-t border-cyan-500/20 bg-cyan-950/30 rounded p-2 text-[10px] font-mono text-cyan-200">
                  <span class="font-bold text-cyan-400">OPERATOR RELEVANCE (KENYA/NAIROBI):</span>
                  <p class="text-slate-300 mt-0.5 font-sans leading-tight">${escapeHtml(d.why_it_matters)}</p>
                </div>
              ` : ""}
            </div>
          `;
        }).join("")}
      </div>
    </div>
  `;
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

    // Extract tactical intel if present in title
    let mainTitle = item.title || "";
    let tacticalIntel = "";
    if (mainTitle.includes(" // [TACTICAL INTEL]: ")) {
      const parts = mainTitle.split(" // [TACTICAL INTEL]: ");
      mainTitle = parts[0];
      tacticalIntel = parts.slice(1).join(" // [TACTICAL INTEL]: ").trim();
    } else if (mainTitle.includes("\\n\\n[IN-DEPTH ANALYSIS]:")) {
      const parts = mainTitle.split("\\n\\n[IN-DEPTH ANALYSIS]:");
      mainTitle = parts[0];
      tacticalIntel = parts.slice(1).join("\\n\\n[IN-DEPTH ANALYSIS]:").trim();
    }

    const titleAttr = mainTitle.replace(/"/g, '&quot;').replace(/'/g, "\\\\'");
    const sourceAttr = (item.source || "").replace(/"/g, '&quot;').replace(/'/g, "\\\\'");

    return `
      <article class="news-item flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between gap-2 mb-2 text-xs">
            <div class="flex items-center gap-2">
              <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded ${badgeClass}">
                ${item.scope}
              </span>
              <span class="text-[11px] font-mono text-slate-400 font-medium">${escapeHtml(item.source)}</span>
            </div>
            <span class="text-[11px] font-mono text-slate-500">${timeAgo}</span>
          </div>

          <h4 class="text-sm font-semibold text-slate-100 hover:text-cyan-300 transition-colors leading-snug">
            <a href="${item.link}" target="_blank" rel="noopener noreferrer" class="block">
              ${escapeHtml(mainTitle)}
            </a>
          </h4>

          ${tacticalIntel ? `
            <div class="mt-2.5 p-2.5 rounded bg-cyan-950/40 border border-cyan-500/30 text-xs">
              <div class="flex items-center justify-between gap-1 mb-1">
                <span class="text-[10px] font-mono font-bold text-cyan-400 flex items-center gap-1">
                  <span class="inline-block w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
                  TACTICAL DEPTH & IMPLICATIONS
                </span>
                <span class="text-[9px] font-mono text-slate-400">COGNITIVE SIFT</span>
              </div>
              <p class="text-[11px] text-slate-300 font-sans leading-relaxed">${escapeHtml(tacticalIntel)}</p>
            </div>
          ` : ""}
        </div>

        <div class="mt-3 pt-2 border-t border-slate-800/40 flex items-center justify-between text-xs text-slate-500">
          <button onclick="window.triggerSubjectDeepDive('${titleAttr}', '${sourceAttr}')"
                  class="inline-flex items-center gap-1 text-[10px] text-cyan-400 hover:text-cyan-300 font-mono px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-500/20 hover:border-cyan-500/50 transition-colors">
            ⚡ DEEP DIVE SUBJECT
          </button>
          <a href="${item.link}" target="_blank" rel="noopener noreferrer" 
             class="inline-flex items-center gap-1 text-[11px] text-cyan-400 hover:text-cyan-300 font-mono transition-colors">
            Read Source 
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
          </a>
        </div>
      </article>
    `;
  }).join("");
}'''

    # Replace old renderNews function
    render_news_pattern = re.compile(r'// Render News Feed\s*function renderNews\(\) \{[\s\S]*?\n\}\n\n// Countdown timer management', re.MULTILINE)
    match = render_news_pattern.search(content)
    if match:
        content = content[:match.start()] + new_render_blocks + '\n\n// Countdown timer management' + content[match.end():]
        print("Replaced renderNews with renderTopicDeepDives + upgraded renderNews.")
    else:
        print("Warning: renderNews pattern not matched.")

    # 6. Add window.triggerSubjectDeepDive at bottom
    if "window.triggerSubjectDeepDive =" not in content:
        content += '''

// ==========================================================================
// TACTICAL SUBJECT DEEP DIVE TRIGGER
// ==========================================================================
window.triggerSubjectDeepDive = async function(subject, source) {
  const inputEl = document.getElementById("cmd-input");
  const modeEl = document.getElementById("cmd-mode");
  const section = document.getElementById("interactive-command-section") || document.getElementById("command-center-section");

  if (section) {
    section.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  if (inputEl && modeEl) {
    modeEl.value = "DEEP-DIVE";
    inputEl.value = `Investigate in-depth developments, structural ripples, and operator impact regarding "${subject}" (Source: ${source || "Global Wire"}). What new data is emerging?`;
    inputEl.focus();

    if (typeof submitCommandDirective === "function") {
      submitCommandDirective();
    }
  }
};
'''
        print("Appended window.triggerSubjectDeepDive.")

    with open("app.js", "w", encoding="utf-8") as f:
        f.write(content)
    print("app.js successfully written.")

if __name__ == "__main__":
    update_app_js()
