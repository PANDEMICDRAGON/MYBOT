"""
╔══════════════════════════════════════════════════════════════╗
║  CORTANA // J.A.R.V.I.S. — REVERSE ENGINEERING SUITE        ║
║  Industrial-Grade Binary & Protocol Analysis Engine          ║
║  Author: Cortana Autonomous Evolution Core                   ║
║  Domain: OSINT / SECURITY / REVERSE_ENGINEERING             ║
╚══════════════════════════════════════════════════════════════╝

Capabilities:
- Binary / ELF / PE / Mach-O file analysis
- APK / JAR inspection (Android apps)
- String extraction (ASCII, Unicode, Base64, URLs, IPs, keys)
- API endpoint harvesting from binaries / JS / APKs
- Entropy analysis (packed / encrypted detection)
- Obfuscation detection
- File format identification (magic bytes)
- Network protocol signature matching
- Disassembly overview (requires objdump)
- Hash generation (MD5, SHA1, SHA256, SHA512)
- Metadata extraction (ELF headers, PE headers)
- JavaScript deobfuscation hints
- Credential / secret pattern scanning
"""

import os
import re
import math
import json
import struct
import hashlib
import string
import subprocess
import tempfile
import zipfile
import base64
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone


# ─── Magic Byte Signatures ────────────────────────────────────────────────────
MAGIC_SIGNATURES = {
    b"\x7fELF": "ELF Binary (Linux/Android native)",
    b"MZ": "PE Binary (Windows .exe/.dll)",
    b"\xfe\xed\xfa\xce": "Mach-O Binary (macOS/iOS 32-bit)",
    b"\xfe\xed\xfa\xcf": "Mach-O Binary (macOS/iOS 64-bit)",
    b"PK\x03\x04": "ZIP Archive (may be APK/JAR/DOCX)",
    b"\x50\x4b\x05\x06": "ZIP (empty archive)",
    b"dex\n": "Android DEX Bytecode",
    b"ODEX": "Android Optimized DEX",
    b"\x89PNG": "PNG Image",
    b"\xff\xd8\xff": "JPEG Image",
    b"GIF8": "GIF Image",
    b"%PDF": "PDF Document",
    b"OggS": "OGG Audio",
    b"fLaC": "FLAC Audio",
    b"\x1f\x8b": "GZIP Compressed",
    b"BZh": "BZIP2 Compressed",
    b"\xfd7zXZ": "XZ Compressed",
    b"Rar!": "RAR Archive",
    b"7z\xbc\xaf": "7-Zip Archive",
    b"\x25\x21": "Script (shebang)",
    b"CAFEBABE": "Java Class File",
    b"\x00\x00\x01\x00": "Windows ICO",
    b"RIFF": "RIFF Container (WAV/AVI)",
    b"\x00\x00\x00 ftyp": "MP4 / ISO Base Media",
}

# ─── Credential / Secret Patterns ─────────────────────────────────────────────
SECRET_PATTERNS = {
    "AWS Access Key":        r"AKIA[0-9A-Z]{16}",
    "AWS Secret Key":        r"(?i)aws.{0,20}secret.{0,20}['\"][0-9a-zA-Z/+]{40}['\"]",
    "GitHub Token":          r"ghp_[A-Za-z0-9]{36}|ghs_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}",
    "Google API Key":        r"AIza[0-9A-Za-z\-_]{35}",
    "Telegram Bot Token":    r"\d{8,10}:AA[A-Za-z0-9_-]{33}",
    "Supabase Anon Key":     r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}",
    "Generic API Key":       r"(?i)(api[_-]?key|apikey|access[_-]?token|secret[_-]?key).{0,10}['\"][A-Za-z0-9_\-]{20,}['\"]",
    "Private Key PEM":       r"-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----",
    "Bearer Token":          r"Bearer\s+[A-Za-z0-9\-._~+/]+=*",
    "Basic Auth":            r"Basic\s+[A-Za-z0-9+/]+=*",
    "Stripe Key":            r"sk_live_[A-Za-z0-9]{24}",
    "M-Pesa Consumer Key":   r"(?i)consumer[_-]?key.{0,10}['\"][A-Za-z0-9]{20,}['\"]",
    "HuggingFace Token":     r"hf_[A-Za-z0-9]{30,}",
    "Groq API Key":          r"gsk_[A-Za-z0-9]{48,}",
    "Password Hash":         r"\$2[ayb]\$[0-9]{2}\$[A-Za-z0-9./]{53}",
}

# ─── URL / IP / Domain Patterns ───────────────────────────────────────────────
URL_PATTERN     = re.compile(r"https?://[^\s\"'<>\x00-\x1f]{6,}")
IP_PATTERN      = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
DOMAIN_PATTERN  = re.compile(r"\b(?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.)+(?:com|net|org|io|co|ke|tz|ug|rw|gov|edu|app|dev|api)\b", re.I)
B64_PATTERN     = re.compile(r"(?:[A-Za-z0-9+/]{4}){4,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?")
API_PATH_PATTERN= re.compile(r"/(?:api|v\d+|rest|graphql|oauth|auth|token|endpoint|webhook|callback)[/\w\-\?=%&.]*", re.I)


class ReverseEngineeringEngine:
    """Industrial-grade reverse engineering and binary analysis engine."""

    def __init__(self):
        self.name = "Cortana Reverse Engineering Suite"
        self.version = "1.0.0"

    # ──────────────────────────────────────────────────────────────────────────
    def identify_file(self, path: str) -> dict:
        """Identify file type via magic bytes and extension."""
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}

        result = {
            "file": str(p),
            "size_bytes": p.stat().st_size,
            "size_human": self._human_size(p.stat().st_size),
            "extension": p.suffix.lower(),
            "magic_type": "Unknown",
            "is_text": False,
        }

        try:
            with open(path, "rb") as f:
                header = f.read(16)
            for magic, label in MAGIC_SIGNATURES.items():
                if header[:len(magic)] == magic:
                    result["magic_type"] = label
                    break
            # Text check
            try:
                with open(path, "r", encoding="utf-8", errors="strict") as f:
                    f.read(1024)
                result["is_text"] = True
            except Exception:
                pass
        except Exception as e:
            result["error"] = str(e)

        return result

    # ──────────────────────────────────────────────────────────────────────────
    def hash_file(self, path: str) -> dict:
        """Compute MD5, SHA1, SHA256, SHA512 hashes of a file."""
        hashes = {alg: hashlib.new(alg) for alg in ["md5", "sha1", "sha256", "sha512"]}
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    for h in hashes.values():
                        h.update(chunk)
            return {k: v.hexdigest() for k, v in hashes.items()}
        except Exception as e:
            return {"error": str(e)}

    # ──────────────────────────────────────────────────────────────────────────
    def entropy_analysis(self, path: str, block_size: int = 4096) -> dict:
        """Measure Shannon entropy to detect packing/encryption."""
        try:
            data = Path(path).read_bytes()
        except Exception as e:
            return {"error": str(e)}

        total_entropy = self._shannon_entropy(data)
        verdict = (
            "⚡ LIKELY PACKED/ENCRYPTED (entropy > 7.5)" if total_entropy > 7.5
            else "🟡 POSSIBLY COMPRESSED (entropy 6.5-7.5)" if total_entropy > 6.5
            else "✅ NORMAL (entropy < 6.5 — readable/plain)"
        )

        # Block-level entropy for heatmap
        blocks = []
        for i in range(0, min(len(data), block_size * 20), block_size):
            blk = data[i:i + block_size]
            blocks.append(round(self._shannon_entropy(blk), 3))

        return {
            "total_entropy": round(total_entropy, 4),
            "verdict": verdict,
            "block_size": block_size,
            "block_entropies": blocks[:20],
            "max_block_entropy": max(blocks) if blocks else 0,
            "min_block_entropy": min(blocks) if blocks else 0,
        }

    # ──────────────────────────────────────────────────────────────────────────
    def extract_strings(self, path: str, min_len: int = 5) -> dict:
        """Extract printable ASCII and Unicode strings from any binary."""
        try:
            data = Path(path).read_bytes()
        except Exception as e:
            return {"error": str(e)}

        ascii_strings = []
        unicode_strings = []
        current = []

        # ASCII
        for byte in data:
            c = chr(byte)
            if c in string.printable and c not in "\r\n\t\x0b\x0c":
                current.append(c)
            else:
                s = "".join(current)
                if len(s) >= min_len:
                    ascii_strings.append(s)
                current = []
        if len(current) >= min_len:
            ascii_strings.append("".join(current))

        # Unicode (UTF-16 LE)
        try:
            text = data.decode("utf-16-le", errors="ignore")
            for line in text.split("\x00"):
                clean = "".join(c for c in line if c in string.printable)
                if len(clean) >= min_len:
                    unicode_strings.append(clean)
        except Exception:
            pass

        total = len(ascii_strings) + len(unicode_strings)
        return {
            "total_strings": total,
            "ascii_count": len(ascii_strings),
            "unicode_count": len(unicode_strings),
            "ascii_strings": ascii_strings[:200],
            "unicode_strings": unicode_strings[:100],
        }

    # ──────────────────────────────────────────────────────────────────────────
    def scan_secrets(self, path: str) -> dict:
        """Scan file for embedded secrets, credentials, and API keys."""
        try:
            try:
                content = Path(path).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                data = Path(path).read_bytes()
                content = data.decode("ascii", errors="ignore")
        except Exception as e:
            return {"error": str(e)}

        found = {}
        for label, pattern in SECRET_PATTERNS.items():
            matches = re.findall(pattern, content)
            if matches:
                # Redact middle of found values for safety in output
                safe = [m[:8] + "***" + m[-4:] if len(m) > 16 else m for m in matches[:5]]
                found[label] = safe

        return {
            "secrets_found": len(found),
            "findings": found,
            "verdict": "🚨 CREDENTIALS DETECTED" if found else "✅ No obvious credentials found",
        }

    # ──────────────────────────────────────────────────────────────────────────
    def extract_network_indicators(self, path: str) -> dict:
        """Extract URLs, IPs, domains, API paths, and Base64 blobs."""
        try:
            try:
                content = Path(path).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                content = Path(path).read_bytes().decode("ascii", errors="ignore")
        except Exception as e:
            return {"error": str(e)}

        urls    = list(set(URL_PATTERN.findall(content)))[:100]
        ips     = list(set(IP_PATTERN.findall(content)))[:50]
        domains = list(set(DOMAIN_PATTERN.findall(content)))[:100]
        api_paths = list(set(API_PATH_PATTERN.findall(content)))[:50]

        # Base64 blobs that decode to something interesting
        b64_decoded = []
        for m in B64_PATTERN.findall(content):
            if len(m) > 20:
                try:
                    dec = base64.b64decode(m + "==").decode("utf-8", errors="ignore")
                    if any(c in dec for c in ["http", "key", "token", "pass", "secret"]):
                        b64_decoded.append({"encoded": m[:30] + "...", "decoded_preview": dec[:60]})
                except Exception:
                    pass
        b64_decoded = b64_decoded[:10]

        return {
            "urls": urls,
            "ips": ips,
            "domains": domains,
            "api_paths": api_paths,
            "interesting_b64_blobs": b64_decoded,
            "summary": {
                "urls": len(urls),
                "ips": len(ips),
                "domains": len(domains),
                "api_paths": len(api_paths),
            }
        }

    # ──────────────────────────────────────────────────────────────────────────
    def inspect_apk(self, apk_path: str, output_dir: Optional[str] = None) -> dict:
        """Inspect Android APK: manifest, permissions, DEX files, assets."""
        p = Path(apk_path)
        if not p.exists():
            return {"error": f"APK not found: {apk_path}"}

        result = {"file": str(p), "permissions": [], "activities": [], "services": [],
                  "receivers": [], "providers": [], "dex_files": [], "assets": [], "native_libs": []}

        try:
            with zipfile.ZipFile(apk_path, "r") as z:
                namelist = z.namelist()
                result["total_files"] = len(namelist)
                result["dex_files"] = [n for n in namelist if n.endswith(".dex")]
                result["native_libs"] = [n for n in namelist if n.endswith(".so")]
                result["assets"] = [n for n in namelist if n.startswith("assets/")][:50]

                # Parse AndroidManifest.xml (binary XML — extract strings only)
                if "AndroidManifest.xml" in namelist:
                    raw = z.read("AndroidManifest.xml")
                    # Extract readable strings from binary XML
                    readable = re.findall(rb"[a-zA-Z0-9_\.\-/]{5,}", raw)
                    strings = [s.decode("ascii", errors="ignore") for s in readable]
                    result["manifest_strings"] = strings[:200]

                    # Extract permission names
                    result["permissions"] = [
                        s for s in strings if "permission" in s.lower() or s.startswith("android.") or "RECEIVE" in s or "READ" in s or "WRITE" in s or "INTERNET" in s
                    ][:50]

        except zipfile.BadZipFile:
            result["error"] = "Not a valid ZIP/APK file"
        except Exception as e:
            result["error"] = str(e)

        return result

    # ──────────────────────────────────────────────────────────────────────────
    def disassemble_overview(self, path: str, arch: str = "auto") -> dict:
        """Run objdump disassembly overview (requires objdump on system)."""
        try:
            cmd = ["objdump", "-f", path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            overview = result.stdout or result.stderr

            # Also get section headers
            cmd2 = ["objdump", "-h", path]
            result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=15)
            sections = result2.stdout or ""

            return {
                "file_headers": overview[:2000],
                "section_headers": sections[:2000],
                "objdump_available": True,
            }
        except FileNotFoundError:
            return {
                "objdump_available": False,
                "note": "objdump not found. Install binutils for disassembly.",
            }
        except Exception as e:
            return {"error": str(e)}

    # ──────────────────────────────────────────────────────────────────────────
    def analyze_javascript(self, js_path: str) -> dict:
        """Analyze JavaScript file for obfuscation, endpoints, and secrets."""
        try:
            content = Path(js_path).read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            return {"error": str(e)}

        lines = content.split("\n")
        line_count = len(lines)
        avg_line_len = sum(len(l) for l in lines) / max(line_count, 1)

        obfuscation_signals = []
        if avg_line_len > 500:
            obfuscation_signals.append("Long average line length (minified/obfuscated)")
        if re.search(r"eval\s*\(", content):
            obfuscation_signals.append("eval() usage detected — possible code injection point")
        if re.search(r"\\x[0-9a-f]{2}", content):
            obfuscation_signals.append("Hex-encoded character sequences found")
        if re.search(r"String\.fromCharCode", content):
            obfuscation_signals.append("String.fromCharCode — char-code obfuscation pattern")
        if re.search(r"atob\s*\(|btoa\s*\(", content):
            obfuscation_signals.append("Base64 encode/decode (atob/btoa) usage")
        if re.search(r"\b_0x[a-f0-9]{4,}\b", content):
            obfuscation_signals.append("Hex-named variables (_0x...) — obfuscator fingerprint")

        endpoints = list(set(API_PATH_PATTERN.findall(content)))[:50]
        urls = list(set(URL_PATTERN.findall(content)))[:50]

        fetch_calls = re.findall(r"fetch\s*\(['\"]([^'\"]+)['\"]", content)
        axios_calls = re.findall(r"axios\.\w+\s*\(['\"]([^'\"]+)['\"]", content)
        xhr_calls   = re.findall(r"open\s*\(['\"](?:GET|POST|PUT|DELETE)['\"],\s*['\"]([^'\"]+)['\"]", content, re.I)

        return {
            "line_count": line_count,
            "avg_line_length": round(avg_line_len, 1),
            "obfuscation_score": len(obfuscation_signals),
            "obfuscation_signals": obfuscation_signals,
            "api_endpoints": endpoints,
            "hardcoded_urls": urls,
            "fetch_calls": fetch_calls[:20],
            "axios_calls": axios_calls[:20],
            "xhr_calls": xhr_calls[:20],
        }

    # ──────────────────────────────────────────────────────────────────────────
    def full_analysis(self, path: str) -> dict:
        """Run complete analysis pipeline on any file."""
        report = {
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "engine": self.name,
            "version": self.version,
        }

        report["identification"] = self.identify_file(path)
        report["hashes"] = self.hash_file(path)
        report["entropy"] = self.entropy_analysis(path)
        report["network_indicators"] = self.extract_network_indicators(path)
        report["secrets_scan"] = self.scan_secrets(path)

        ext = Path(path).suffix.lower()
        if ext in (".apk", ".aar", ".jar"):
            report["apk_inspection"] = self.inspect_apk(path)
        if ext in (".js", ".ts", ".mjs", ".jsx"):
            report["javascript_analysis"] = self.analyze_javascript(path)
        if ext in (".elf", "", ".so", ".exe", ".dll", ".bin", ".out"):
            report["strings"] = self.extract_strings(path)
            report["disassembly"] = self.disassemble_overview(path)

        return report

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _shannon_entropy(data: bytes) -> float:
        if not data:
            return 0.0
        freq = [0] * 256
        for b in data:
            freq[b] += 1
        n = len(data)
        return -sum((c / n) * math.log2(c / n) for c in freq if c > 0)

    @staticmethod
    def _human_size(n: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} TB"


# ─── Standalone API ────────────────────────────────────────────────────────────
_engine = ReverseEngineeringEngine()


def analyze_file(path: str) -> dict:
    """Full analysis of any file — entry point for bot integration."""
    return _engine.full_analysis(path)


def scan_for_secrets(path: str) -> dict:
    """Quick credential scan on a file."""
    return _engine.scan_secrets(path)


def extract_network_iocs(path: str) -> dict:
    """Extract network indicators of compromise (URLs, IPs, domains)."""
    return _engine.extract_network_indicators(path)


def get_file_info(path: str) -> dict:
    """Identify a file and get its hashes."""
    info = _engine.identify_file(path)
    info["hashes"] = _engine.hash_file(path)
    info["entropy"] = _engine.entropy_analysis(path)
    return info


def inspect_apk(apk_path: str) -> dict:
    """Inspect an Android APK file."""
    return _engine.inspect_apk(apk_path)


def analyze_js(js_path: str) -> dict:
    """Analyze a JavaScript file for obfuscation and endpoints."""
    return _engine.analyze_javascript(js_path)


def summarize(report: dict) -> str:
    """Convert analysis report to a readable Telegram-friendly summary."""
    lines = [
        f"🔬 *REVERSE ENGINEERING REPORT*",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    if "identification" in report:
        idf = report["identification"]
        lines += [
            f"📄 *File:* `{Path(idf.get('file', '?')).name}`",
            f"📦 *Type:* `{idf.get('magic_type', '?')}`",
            f"💾 *Size:* `{idf.get('size_human', '?')}`",
        ]

    if "hashes" in report:
        h = report["hashes"]
        lines.append(f"🔑 *SHA256:* `{h.get('sha256', '?')[:32]}...`")

    if "entropy" in report:
        ent = report["entropy"]
        lines.append(f"📊 *Entropy:* `{ent.get('total_entropy', 0)}` — {ent.get('verdict', '')}")

    if "secrets_scan" in report:
        sec = report["secrets_scan"]
        lines.append(f"🚨 *Secrets:* {sec.get('verdict', '')}")
        for k, v in (sec.get("findings") or {}).items():
            lines.append(f"  ↳ `{k}`: {', '.join(v[:2])}")

    if "network_indicators" in report:
        net = report["network_indicators"]
        s = net.get("summary", {})
        lines.append(
            f"🌐 *Network IOCs:* `{s.get('urls', 0)}` URLs · `{s.get('ips', 0)}` IPs · `{s.get('api_paths', 0)}` API paths"
        )
        for url in net.get("urls", [])[:3]:
            lines.append(f"  ↳ `{url}`")

    if "javascript_analysis" in report:
        js = report["javascript_analysis"]
        obs = js.get("obfuscation_score", 0)
        lines.append(f"⚙️ *JS Obfuscation Score:* `{obs}/6`")
        for sig in js.get("obfuscation_signals", [])[:3]:
            lines.append(f"  ↳ ⚠️ {sig}")

    if "apk_inspection" in report:
        apk = report["apk_inspection"]
        lines += [
            f"📱 *APK Files:* `{apk.get('total_files', '?')}`",
            f"📝 *Permissions:* `{len(apk.get('permissions', []))}`",
            f"🔧 *Native Libs:* `{len(apk.get('native_libs', []))}`",
        ]

    lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        target = sys.argv[1]
        print(f"\n[ReverseEngineer] Analyzing: {target}\n")
        report = analyze_file(target)
        print(json.dumps(report, indent=2, default=str))
        print("\n" + "=" * 60)
        print(summarize(report))
    else:
        print("Usage: python reverse_engineer.py <file_path>")
        print("\nFunctions available:")
        print("  analyze_file(path)       — Full analysis pipeline")
        print("  scan_for_secrets(path)   — Credential scan")
        print("  extract_network_iocs(path) — URLs, IPs, domains")
        print("  get_file_info(path)      — ID + hashes + entropy")
        print("  inspect_apk(path)        — Android APK inspection")
        print("  analyze_js(path)         — JavaScript obfuscation analysis")
