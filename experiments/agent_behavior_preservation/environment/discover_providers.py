from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OUT_JSON = BASE / "environment" / "provider_discovery.json"
OUT_MD = BASE / "environment" / "provider_discovery.md"

PROVIDERS = {
    "openai": {"env_names": ["OPENAI_API_KEY"], "cli": None},
    "anthropic": {"env_names": ["ANTHROPIC_API_KEY"], "cli": None},
    "google_gemini": {"env_names": ["GOOGLE_API_KEY", "GEMINI_API_KEY"], "cli": None},
    "azure_openai": {"env_names": ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"], "cli": None},
    "github_copilot_cli": {"env_names": [], "cli": "gh"},
}


def gh_copilot_usable() -> tuple[bool, bool]:
    if shutil.which("gh") is None:
        return False, False
    try:
        result = subprocess.run(["gh", "extension", "list"], text=True, capture_output=True, timeout=8)
    except Exception:
        return True, False
    return True, "copilot" in (result.stdout + result.stderr).lower()


def main() -> int:
    rows = []
    for provider, spec in PROVIDERS.items():
        configured = any(name in os.environ and bool(os.environ.get(name)) for name in spec["env_names"])
        auth_usable = configured
        models_discoverable = False
        note = "environment variable presence only; secret value not inspected"
        if provider == "github_copilot_cli":
            cli_present, copilot_present = gh_copilot_usable()
            configured = cli_present and copilot_present
            auth_usable = False
            models_discoverable = False
            note = "gh CLI checked for copilot extension without making model calls"
        rows.append(
            {
                "provider": provider,
                "provider_configured": configured,
                "authentication_usable": auth_usable,
                "models_discoverable": models_discoverable,
                "secret_values_logged": False,
                "note": note,
            }
        )
    payload = {"timestamp": datetime.now(timezone.utc).isoformat(), "providers": rows}
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = ["# Provider Discovery", "", "No API keys or secret values are printed or stored.", "", "| Provider | Configured | Authentication usable | Models discoverable |", "|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['provider']} | {row['provider_configured']} | {row['authentication_usable']} | {row['models_discoverable']} |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
