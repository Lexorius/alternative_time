#!/usr/bin/env bash
# Schnell-Check der manifest.json-Konventionen, ohne CI abzuwarten.
# Prüft: JSON valide, Pflichtkeys da, Key-Reihenfolge korrekt.
set -euo pipefail
cd "$(dirname "$0")/.."

MANIFEST="custom_components/haushaltsdoku/manifest.json"

python3 - "$MANIFEST" <<'PY'
import json, sys
path = sys.argv[1]

try:
    raw = open(path, encoding="utf-8").read()
    data = json.loads(raw)
except Exception as e:
    print(f"✗ {path} ist kein gültiges JSON: {e}")
    sys.exit(1)

required = {"domain", "name", "documentation", "codeowners", "version"}
missing = required - data.keys()
if missing:
    print(f"✗ Pflichtkeys fehlen: {sorted(missing)}")
    sys.exit(1)

# Reihenfolge: domain, name, dann alphabetisch
keys = list(data.keys())
expected = ["domain", "name"] + sorted(k for k in data if k not in ("domain", "name"))
if keys != expected:
    print("✗ Reihenfolge der Keys nicht korrekt.")
    print("  Soll:", expected)
    print("  Ist: ", keys)
    print()
    print("  Fix automatisch: ./scripts/bump-version.sh patch  (sortiert mit)")
    sys.exit(1)

print(f"✓ {path}: alle Checks ok (Version {data['version']})")
PY
