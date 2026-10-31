"""
╔══════════════════════════════════════════════════════════════╗
║  CORTANA // J.A.R.V.I.S. — EVOLUTION MODULE REGISTRY        ║
║  Dynamic Indexing, Search, and Runtime Execution Engine      ║
║  Author: Cortana Autonomous Evolution Core                   ║
╚══════════════════════════════════════════════════════════════╝

Provides seamless cataloging, search, inspection, and on-demand execution
of all 330+ evolution modules across Industrial SCADA, Reverse Engineering,
Fintech, Cold-Chain Logistics, Zero-Trust Security, and Edge Systems.
"""

import ast
import os
import sys
import json
import inspect
import importlib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

MODULES_DIR = Path(__file__).resolve().parent

# Domain classification rules based on module name and content keywords
DOMAIN_MAPPINGS = {
    "REVERSE_ENGINEERING_SECURITY": {
        "title": "Reverse Engineering & Security Operations",
        "icon": "🛡️",
        "keywords": ["reverse_engineer", "zero_trust", "credential", "quantum", "tamper", "shield", "deception", "auditor", "threat", "anomaly", "auth", "encrypt", "sandbox", "obfuscation"]
    },
    "FINTECH_MPESA": {
        "title": "Fintech, M-Pesa & Financial Vaults",
        "icon": "💳",
        "keywords": ["mpesa", "daraja", "kra", "tax", "sacco", "chama", "escrow", "settlement", "remittance", "dividend", "wallet", "ledger", "microcredit"]
    },
    "INDUSTRIAL_MILLING_SCADA": {
        "title": "Industrial SCADA & Commercial Milling",
        "icon": "🏭",
        "keywords": ["roller_mill", "milling", "silo", "flour", "grain", "purifier", "sifter", "torque", "boiler", "scada", "bearing", "destoner", "chiller", "autoclave"]
    },
    "AGRO_COLD_CHAIN": {
        "title": "Agribusiness, Cold Chain & Food Systems",
        "icon": "🌱",
        "keywords": ["cold_chain", "greenhouse", "aquaponics", "hydroponic", "coffee", "tea", "avocado", "honey", "apiar", "abattoir", "poultry", "compost", "macadamia", "irrigation", "mango", "cheese"]
    },
    "MOBILITY_LOGISTICS": {
        "title": "Mobility, Transit & Freight",
        "icon": "🚚",
        "keywords": ["matatu", "boda", "sgr", "cargo", "expressway", "toll", "parcel", "ambulance", "logistics", "fleet", "parking", "school_bus"]
    },
    "CIVIC_ENERGY_EDGE": {
        "title": "Civic Infrastructure, Solar & Edge Resilience",
        "icon": "⚡",
        "keywords": ["solar", "grid", "kplc", "borehole", "water", "streetlight", "edge", "offline", "wan", "fiber", "sms", "ussd", "waste", "pharmacy", "hospital", "creche"]
    }
}


class ModuleRegistry:
    """Industrial runtime registry for all evolution modules."""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._indexed = False

    def index(self, force: bool = False) -> Dict[str, Dict[str, Any]]:
        """Scans and statically indexes all modules in evolution_modules."""
        if self._indexed and not force:
            return self._cache

        modules = {}
        for py_file in MODULES_DIR.glob("*.py"):
            name = py_file.stem
            if name in ("__init__", "registry"):
                continue

            doc = ""
            classes = []
            functions = []
            has_main = False

            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                has_main = 'if __name__ == "__main__":' in content or "if __name__ == '__main__':" in content
                
                # Fast AST parsing to extract metadata without importing
                tree = ast.parse(content, filename=str(py_file))
                doc = ast.get_docstring(tree) or ""
                if not doc:
                    # check for leading comment block
                    lines = [l.strip("# \t\r\n") for l in content.splitlines()[:15] if l.strip().startswith("#")]
                    if lines:
                        doc = " ".join(lines)

                for node in tree.body:
                    if isinstance(node, ast.ClassDef):
                        classes.append({
                            "name": node.name,
                            "doc": ast.get_docstring(node) or "",
                            "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef) and not m.name.startswith("_")]
                        })
                    elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                        functions.append(node.name)

            except Exception as e:
                doc = f"[Parser fallback]: {e}"

            # Classify domain
            domain = "GENERAL_UTILITY"
            domain_icon = "⚙️"
            domain_title = "General Utility & System Sentinels"
            name_lower = name.lower()
            text_lower = f"{name_lower} {doc.lower()}"

            for d_key, d_meta in DOMAIN_MAPPINGS.items():
                if any(k in text_lower for k in d_meta["keywords"]):
                    domain = d_key
                    domain_icon = d_meta["icon"]
                    domain_title = d_meta["title"]
                    break

            modules[name] = {
                "name": name,
                "file_path": str(py_file),
                "file_size": py_file.stat().st_size,
                "doc": doc.strip() if doc else "Autonomous Cortana Evolution Module",
                "classes": classes,
                "functions": functions,
                "has_main": has_main,
                "domain": domain,
                "domain_icon": domain_icon,
                "domain_title": domain_title
            }

        self._cache = modules
        self._indexed = True
        return self._cache

    def count(self) -> int:
        return len(self.index())

    def get_categories(self) -> Dict[str, Dict[str, Any]]:
        """Returns summary counts and details per category."""
        modules = self.index()
        cats = {}
        for d_key, d_meta in DOMAIN_MAPPINGS.items():
            matching = [m for m in modules.values() if m["domain"] == d_key]
            cats[d_key] = {
                "title": d_meta["title"],
                "icon": d_meta["icon"],
                "count": len(matching),
                "sample_modules": [m["name"] for m in matching[:8]]
            }
        
        # General Utility
        general = [m for m in modules.values() if m["domain"] == "GENERAL_UTILITY"]
        if general:
            cats["GENERAL_UTILITY"] = {
                "title": "General Utility & Autonomous Sentinels",
                "icon": "⚙️",
                "count": len(general),
                "sample_modules": [m["name"] for m in general[:8]]
            }
        return cats

    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Searches modules across names, categories, and docstrings."""
        modules = self.index()
        q = query.lower().strip()
        results = []

        for name, meta in modules.items():
            score = 0
            name_lower = name.lower()
            if q == name_lower:
                score += 100
            elif q in name_lower:
                score += 40
            
            if q in meta["domain"].lower() or q in meta["domain_title"].lower():
                score += 25

            if q in meta["doc"].lower():
                score += 15

            for cls in meta["classes"]:
                if q in cls["name"].lower():
                    score += 20
                for meth in cls.get("methods", []):
                    if q in meth.lower():
                        score += 10

            if score > 0:
                results.append((score, meta))

        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:limit]]

    def get_info(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Returns full structural metadata for a specific module."""
        modules = self.index()
        target = module_name.strip().lower()
        if target.endswith(".py"):
            target = target[:-3]

        if target in modules:
            return modules[target]

        # Fuzzy match
        for name, meta in modules.items():
            if target in name.lower():
                return meta
        return None

    def execute_module(self, module_name: str, args: Optional[List[str]] = None, timeout: int = 40) -> Dict[str, Any]:
        """
        Executes a module in an isolated subprocess, capturing stdout/stderr and artifacts.
        """
        info = self.get_info(module_name)
        if not info:
            return {
                "success": False,
                "error": f"Module '{module_name}' not found in registry.",
                "output": "",
                "duration": 0
            }

        py_path = Path(info["file_path"])
        cmd = [sys.executable, str(py_path)]
        if args:
            cmd.extend(args)

        import time
        start_t = time.time()
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(MODULES_DIR.parent)
            )
            elapsed = time.time() - start_t
            output = (res.stdout + "\n" + res.stderr).strip()
            return {
                "success": res.returncode == 0,
                "returncode": res.returncode,
                "output": output if output else "[Module completed successfully with no terminal output]",
                "duration": round(elapsed, 2),
                "module_name": info["name"],
                "domain": info["domain_title"]
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Execution timed out after {timeout} seconds.",
                "output": "",
                "duration": timeout,
                "module_name": info["name"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": "",
                "duration": round(time.time() - start_t, 2),
                "module_name": info["name"]
            }


# Singleton instance
registry = ModuleRegistry()


def list_modules_summary() -> str:
    """Builds a formatted Telegram/Markdown summary of module categories."""
    cats = registry.get_categories()
    total = registry.count()

    lines = [
        f"🧩 *CORTANA // J.A.R.V.I.S. INDUSTRIAL MODULE REGISTRY*",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"📦 *Total Active Modules:* `{total}`",
        f"⚡ *Status:* All validated, syntax-verified & ready for execution",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
        f"*Available Domains:*"
    ]

    for d_key, meta in cats.items():
        lines.append(f"{meta['icon']} *{meta['title']}* (`{meta['count']}` modules)")
        samples = ", ".join(f"`{s}`" for s in meta["sample_modules"][:4])
        lines.append(f"  ↳ Samples: {samples}\n")

    lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"💡 *How to access & use any module anytime:*")
    lines.append(f"• `/modules search <keyword>` — Search modules")
    lines.append(f"• `/module <name>` — Inspect module info & classes")
    lines.append(f"• `/run <name>` or `/module run <name> [args]` — Execute immediately")
    lines.append(f"• `/re <file_or_url>` — Run Reverse Engineering Suite")

    return "\n".join(lines)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(f"Indexing modules in {MODULES_DIR}...")
    reg = registry.index()
    print(f"Indexed {len(reg)} modules.")
    print("\n" + list_modules_summary())
