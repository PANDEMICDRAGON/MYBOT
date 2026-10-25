#!/usr/bin/env python3
"""
=====================================================================
HALO WORKSPACE DAEMON & LOCAL CLI BRIDGE (halo_agent.py)
Autonomous Principal Systems Engineer & Secure Local Bridge
=====================================================================
Dual-Listener Bridge:
- Port 5050 (or HALO_PORT) Asynchronous HTTP Server with CORS for Web HUD
- Supabase command_queue Poller for Mobile Vercel Web HUD & Telegram
- One-Shot Terminal CLI for Instant Colorized Diffs & Patch Approvals
- Path-Sandboxed Read/Write with Git Stash + Snapshot Rollback Protection
"""

import os
import sys
import json
import shutil
import difflib
import asyncio
import platform
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import httpx
from aiohttp import web

# Load .env if present in workspace root
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# --- ENVIRONMENT & WORKSPACE CONFIGURATION ---
WORKSPACE_ROOT = Path(os.getenv("WORKSPACE_ROOT", os.getcwd())).resolve()
BACKUP_DIR = WORKSPACE_ROOT / ".halo_backups"
BACKUP_DIR.mkdir(exist_ok=True)

AUTO_APPLY = os.getenv("HALO_AUTO_APPLY", "0") == "1"
LOCAL_PORT = int(os.getenv("HALO_PORT", "5050"))
OPERATOR_PASSCODE = os.getenv("OPERATOR_PASSCODE", "CORTANA-75-AUTH")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
AUTHORIZED_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0"))
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_KEY", "")

SUPABASE_HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json"
}

GEMINI_CHAT_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

MODEL_CASCADE = [
    {"provider": "gemini", "model": "gemini-3.5-flash-lite"},
    {"provider": "gemini", "model": "gemini-3.8-flash"},
    {"provider": "gemini", "model": "gemini-2.5-pro"},
    {"provider": "gemini", "model": "gemini-2.5-flash"},
    {"provider": "groq",   "model": "qwen/qwen3.8-27b"},
    {"provider": "groq",   "model": "llama-3.3-70b-versatile"},
    {"provider": "groq",   "model": "llama-3.1-8b-instant"}
]

REFACTOR_SYSTEM_PROMPT = """You are HALO, an autonomous principal systems engineer and local workspace bridge.
When given a source file and an optimization/refactor directive:
1. Return valid JSON strictly matching this schema:
{
  "explanation": "Concise technical summary of optimizations, complexity reductions, and fixes applied.",
  "refactored_code": "The complete, production-ready replacement file content. Never use placeholders or elisions like '// ... rest of code'."
}
2. Preserve all existing functional contracts and exports unless explicitly instructed to change them."""


# --- 1. PATH SECURITY & GIT/FILE BACKUP ENGINE ---
def resolve_safe_path(relative_path: str) -> Path:
    """Ensures target file resides strictly inside WORKSPACE_ROOT."""
    clean_rel = relative_path.strip().lstrip("/\\")
    target = (WORKSPACE_ROOT / clean_rel).resolve()
    if not target.is_relative_to(WORKSPACE_ROOT):
        raise ValueError(f"Security violation: {relative_path} resolves outside {WORKSPACE_ROOT}")
    return target


def create_safety_backup(target_path: Path) -> str:
    """Creates a timestamped file snapshot and records a non-destructive git stash entry if inside a repo."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"{target_path.name}.{timestamp}.bak"
    if target_path.exists():
        shutil.copy2(target_path, backup_file)

    # Create a non-destructive git stash commit object without wiping working tree
    try:
        stash_sha = subprocess.check_output(
            ["git", "stash", "create", f"HALO-backup-{target_path.name}-{timestamp}"],
            cwd=WORKSPACE_ROOT,
            stderr=subprocess.DEVNULL
        ).decode().strip()
        if stash_sha:
            subprocess.run(
                ["git", "stash", "store", "-m", f"HALO-pre-patch-{target_path.name}-{timestamp}", stash_sha],
                cwd=WORKSPACE_ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
    except Exception:
        pass

    return str(backup_file)


def verify_syntax(target_path: Path) -> tuple[bool, str]:
    """Runs syntax verification after writing a patch. Returns (ok, error_message)."""
    suffix = target_path.suffix.lower()
    if suffix == ".py":
        res = subprocess.run([sys.executable, "-m", "py_compile", str(target_path)], capture_output=True, text=True)
        return (res.returncode == 0, res.stderr.strip())
    elif suffix in (".js", ".mjs", ".cjs"):
        res = subprocess.run(["node", "--check", str(target_path)], capture_output=True, text=True)
        return (res.returncode == 0, res.stderr.strip())
    return (True, "Syntax check bypassed for file type.")


# --- 2. RESILIENT LLM ROUTER (GEMINI FLASH-LITE / PRO -> GROQ FAILOVER) ---
async def call_llm(client: httpx.AsyncClient, messages: list[dict], json_mode: bool = False) -> str:
    for route in MODEL_CASCADE:
        provider, model = route["provider"], route["model"]
        if provider == "gemini" and GEMINI_API_KEY:
            url, key = GEMINI_CHAT_URL, GEMINI_API_KEY
        elif provider == "groq" and GROQ_API_KEY:
            url, key = GROQ_CHAT_URL, GROQ_API_KEY
        else:
            continue

        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": messages, "temperature": 0.15}
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            resp = await client.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code == 429:
                continue
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict) and "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[LLM Failover Warning - {provider}:{model}]: {e}")
            continue

    raise RuntimeError("All configured LLM endpoints (Gemini & Groq) failed or hit rate limits.")


# --- 3. GRANULAR FILE REFACTOR & DIFF PATCH ENGINE ---
async def refactor_workspace_file(
    client: httpx.AsyncClient,
    rel_path: str,
    instruction: str,
    force_auto: bool = False
) -> dict:
    target = resolve_safe_path(rel_path)
    if not target.exists() or not target.is_file():
        return {"status": "ERROR", "message": f"File not found: {rel_path}"}

    original_code = target.read_text(encoding="utf-8")
    user_prompt = (
        f"TARGET FILE: {rel_path}\n"
        f"OPTIMIZATION DIRECTIVE: {instruction}\n\n"
        f"--- CURRENT FILE CONTENT ---\n{original_code}"
    )

    raw_response = await call_llm(
        client,
        [
            {"role": "system", "content": REFACTOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        json_mode=True
    )

    parsed = json.loads(raw_response)
    explanation = parsed.get("explanation", "Refactor generated.")
    new_code = parsed.get("refactored_code", "")

    if not new_code.strip():
        return {"status": "ERROR", "message": "Model returned empty code buffer."}

    diff_lines = list(difflib.unified_diff(
        original_code.splitlines(keepends=True),
        new_code.splitlines(keepends=True),
        fromfile=f"a/{rel_path}",
        tofile=f"b/{rel_path}",
        n=3
    ))
    diff_text = "".join(diff_lines)

    if not diff_text:
        return {"status": "NO_CHANGES", "message": f"No modifications required for {rel_path}.", "diff": ""}

    # Print diff to local terminal
    print(f"\n{'='*60}\nPROPOSED PATCH FOR: {rel_path}\nSUMMARY: {explanation}\n{'='*60}")
    for line in diff_lines:
        if line.startswith("+") and not line.startswith("+++"):
            print(f"\033[92m{line}\033[0m", end="")
        elif line.startswith("-") and not line.startswith("---"):
            print(f"\033[91m{line}\033[0m", end="")
        else:
            print(line, end="")
    print(f"\n{'='*60}")

    # Check confirmation gate
    should_apply = AUTO_APPLY or force_auto
    if not should_apply and sys.stdin.isatty():
        ans = await asyncio.to_thread(input, f"\nApply patch to {rel_path}? [y/N]: ")
        should_apply = ans.strip().lower() == "y"

    if not should_apply:
        return {
            "status": "STAGED_ONLY",
            "message": f"Diff generated for {rel_path} (awaiting confirmation).",
            "explanation": explanation,
            "diff": diff_text
        }

    backup_path = create_safety_backup(target)
    target.write_text(new_code, encoding="utf-8")

    syntax_ok, syntax_err = verify_syntax(target)
    if not syntax_ok:
        shutil.copy2(backup_path, target)
        return {
            "status": "ROLLED_BACK",
            "message": f"Syntax validation failed; restored backup from {backup_path}.\nError: {syntax_err}",
            "diff": diff_text
        }

    return {
        "status": "APPLIED",
        "message": f"Patch applied to {rel_path}. Backup saved: {backup_path}",
        "explanation": explanation,
        "diff": diff_text
    }


# --- 4. LOCAL NETWORK & SYSTEM COMMAND ROUTER ---
async def scan_local_mesh(subnet_prefix: str = "192.168.1") -> str:
    """Executes concurrent ping sweep across local Wi-Fi subnet."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    wait_flag = "-w" if platform.system().lower() == "windows" else "-W"

    async def ping_host(ip: str):
        proc = await asyncio.create_subprocess_exec(
            "ping", param, "1", wait_flag, "1", ip,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await proc.wait()
        return ip if proc.returncode == 0 else None

    tasks = [ping_host(f"{subnet_prefix}.{i}") for i in range(1, 50)]
    results = await asyncio.gather(*tasks)
    live_hosts = [ip for ip in results if ip]
    return f"Local mesh scan complete on {subnet_prefix}.0/24. Active nodes ({len(live_hosts)}): {', '.join(live_hosts) if live_hosts else 'None detected'}"


async def execute_directive_router(client: httpx.AsyncClient, prompt: str, auto_apply: bool = False) -> str:
    """
    Routes incoming directives from CLI, Local Port 5050, Web HUD, or Telegram:
    - 'patch <filepath> : <instruction>' -> Refactors file & produces diff
    - 'read <filepath>' -> Reads local workspace file
    - 'tree' / 'files' -> Lists workspace files
    - 'scan network' / 'wi-fi' -> Runs live local subnet discovery
    - Everything else -> Conversational Cortana/J.A.R.V.I.S. synthesis
    """
    clean = prompt.strip()
    lower = clean.lower()

    if lower.startswith("patch "):
        body = clean[6:].strip()
        if ":" not in body:
            return "Usage: patch <relative/path/to/file> : <optimization directive>"
        rel_path, instruction = body.split(":", 1)
        res = await refactor_workspace_file(client, rel_path.strip(), instruction.strip(), force_auto=auto_apply)
        return f"[{res['status']}] {res['message']}\n\n{res.get('explanation', '')}\n\n```diff\n{res.get('diff', '')[:2500]}\n```"

    if lower.startswith("read "):
        rel_path = clean[5:].strip()
        target = resolve_safe_path(rel_path)
        if not target.exists():
            return f"File not found: {rel_path}"
        return f"FILE: {rel_path}\n\n{target.read_text(encoding='utf-8')[:3500]}"

    if lower in ("tree", "files", "ls"):
        files = [
            str(p.relative_to(WORKSPACE_ROOT))
            for p in WORKSPACE_ROOT.rglob("*")
            if p.is_file() and not any(part.startswith(".") or part in ("node_modules", "__pycache__", "venv", ".venv") for part in p.parts)
        ]
        return f"Workspace Root: {WORKSPACE_ROOT}\nFiles ({len(files)}):\n" + "\n".join(files[:60])

    if any(k in lower for k in ["wi-fi", "wifi", "mesh", "scan local", "network", "tv and laptop"]):
        subnet = os.getenv("LOCAL_SUBNET", "192.168.1")
        mesh_report = await scan_local_mesh(subnet)
        return await call_llm(client, [
            {"role": "system", "content": "You are HALO (Cortana/J.A.R.V.I.S.). Report the local network telemetry concisely."},
            {"role": "user", "content": f"Directive: {clean}\nLive Hardware Telemetry: {mesh_report}"}
        ])

    if lower.startswith(("recon ", "/recon ", "osint ", "decode ")):
        target_q = clean.split(" ", 1)[1].strip()
        from osint_engine import run_planetary_recon
        r = await run_planetary_recon(
            client,
            target_query=target_q,
            llm_caller=call_llm,
            supabase_url=SUPABASE_URL,
            supabase_headers=SUPABASE_HEADERS
        )
        return (
            f"PLANETARY OSINT & BEHAVIORAL DOSSIER // TARGET: {r['target_query']}\n"
            f"PLATFORMS: {', '.join(r['platforms_scanned'])}\n"
            f"SENTIMENT VECTOR: {r['sentiment_vector']}\n\n"
            f"1. EVOLUTIONARY PSYCHOLOGY & STATUS SIGNALING:\n{r['status_signaling']}\n\n"
            f"2. GAME THEORY & INCENTIVE MATRIX:\n{r['game_theory_matrix']}\n\n"
            f"3. NARRATIVE COORDINATION & BOT DETECTION:\n{r['narrative_coordination']}\n\n"
            f"4. OPERATOR COUNTERPLAY (PROTECT & EXPLOIT):\n{r['operator_counterplay']}"
        )

    return await call_llm(client, [
        {"role": "system", "content": f"You are HALO (Cortana/J.A.R.V.I.S. construct) running locally inside {WORKSPACE_ROOT}. Respond directly and concisely."},
        {"role": "user", "content": clean}
    ])


# --- 5. LOCAL PORT 5050 HTTP SERVER (RESOLVES WEB HUD PORT 5050 REQUIREMENT) ---
@web.middleware
async def cors_middleware(request: web.Request, handler):
    if request.method == "OPTIONS":
        resp = web.Response(status=204)
    else:
        resp = await handler(request)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, x-operator-key, Authorization"
    return resp


async def handle_http_command(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except Exception:
        data = {}
    passcode = request.headers.get("x-operator-key") or data.get("passcode", "")
    if passcode != OPERATOR_PASSCODE:
        return web.json_response({"status": "ERROR", "response": "Unauthorized passcode."}, status=401)

    prompt = data.get("prompt") or data.get("directive", "")
    auto_flag = bool(data.get("auto_apply", AUTO_APPLY))
    async with httpx.AsyncClient() as client:
        reply = await execute_directive_router(client, prompt, auto_apply=auto_flag)
    return web.json_response({"status": "COMPLETED", "response": reply})


async def handle_http_health(request: web.Request) -> web.Response:
    return web.json_response({
        "status": "ONLINE",
        "service": "HALO Workspace Daemon",
        "workspace": str(WORKSPACE_ROOT),
        "port": LOCAL_PORT
    })


# --- 6. SUPABASE COMMAND_QUEUE POLLER (FOR MOBILE VERCEL HUD & TELEGRAM) ---
async def supabase_queue_worker(client: httpx.AsyncClient):
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("[HALO] Supabase credentials unconfigured. Cloud queue polling inactive.")
        return
    print("[HALO] Supabase command_queue poller active (2s interval)...")
    while True:
        try:
            url = f"{SUPABASE_URL}/rest/v1/command_queue?status=eq.PENDING&select=*&order=created_at.asc&limit=3"
            resp = await client.get(url, headers=SUPABASE_HEADERS, timeout=15)
            if resp.status_code == 200:
                for job in resp.json():
                    job_id = job["id"]
                    job_prompt = job.get("prompt") or job.get("directive", "")
                    await client.patch(
                        f"{SUPABASE_URL}/rest/v1/command_queue?id=eq.{job_id}",
                        headers=SUPABASE_HEADERS,
                        json={"status": "PROCESSING"}
                    )
                    reply = await execute_directive_router(client, job_prompt, auto_apply=True)
                    await client.patch(
                        f"{SUPABASE_URL}/rest/v1/command_queue?id=eq.{job_id}",
                        headers=SUPABASE_HEADERS,
                        json={
                            "status": "COMPLETED",
                            "response": reply,
                            "completed_at": datetime.now(timezone.utc).isoformat()
                        }
                    )
        except Exception as e:
            print(f"[Supabase Bridge Error]: {e}")
        await asyncio.sleep(2)


async def main():
    # Direct CLI One-Shot Mode: python halo_agent.py "patch app/page.tsx : optimize rendering"
    if len(sys.argv) > 1:
        cli_directive = " ".join(sys.argv[1:])
        async with httpx.AsyncClient() as client:
            output = await execute_directive_router(client, cli_directive, auto_apply=AUTO_APPLY)
            print(output)
        return

    # Persistent Daemon Mode: Port 5050 HTTP Bridge + Supabase Queue Poller
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_get("/health", handle_http_health)
    app.router.add_get("/api/health", handle_http_health)
    app.router.add_post("/execute", handle_http_command)
    app.router.add_post("/api/execute", handle_http_command)

    runner = web.AppRunner(app)
    await runner.setup()

    bind_port = LOCAL_PORT
    try:
        site = web.TCPSite(runner, "127.0.0.1", bind_port)
        await site.start()
        print(f"HALO Workspace Daemon Online // Root: {WORKSPACE_ROOT} // Port: {bind_port}")
    except OSError as oe:
        # If port 5050 is already in use by bot.py, bind fallback port and continue queue poller
        bind_port = LOCAL_PORT + 1
        site = web.TCPSite(runner, "127.0.0.1", bind_port)
        await site.start()
        print(f"HALO Workspace Daemon Online // Port {LOCAL_PORT} busy, listening on fallback {bind_port} // Root: {WORKSPACE_ROOT}")

    async with httpx.AsyncClient() as client:
        await supabase_queue_worker(client)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n[HALO] Daemon standing down.")
