#!/usr/bin/env bash
# Bump die Version und legt einen CHANGELOG-Eintrag an.
#
# Usage:
#   ./scripts/bump-version.sh patch              # 0.2.4    → 0.2.5
#   ./scripts/bump-version.sh minor              # 0.2.4    → 0.3.0
#   ./scripts/bump-version.sh major              # 0.2.4    → 1.0.0
#   ./scripts/bump-version.sh build              # 2.6.0.1  → 2.6.0.2  (4. Komponente, legt sie an wenn nötig)
#   ./scripts/bump-version.sh 0.5.7              # explizite Version (3- oder 4-teilig)
#   ./scripts/bump-version.sh 2.6.0.1            # explizite 4-teilige Version
#
# Hinweise zu 4-teiligen Versionen:
#   - patch/minor/major liefern immer eine 3-teilige Version (verwerfen die 4. Komponente).
#     Für inkrementelle Builds desselben x.y.z statt dessen `build` benutzen.
#
#   Mit --release am Ende: macht zusätzlich Commit, Tag und Push.
#   ./scripts/bump-version.sh patch --release
set -euo pipefail
cd "$(dirname "$0")/.."

DOMAIN="alternative_time"
MANIFEST="custom_components/${DOMAIN}/manifest.json"
CHANGELOG="CHANGELOG.md"

if [ $# -lt 1 ]; then
  echo "Usage: $0 {patch|minor|major|build|<x.y.z[.b]>} [--release]" >&2
  exit 1
fi

DO_RELEASE=0
for arg in "$@"; do
  [ "$arg" = "--release" ] && DO_RELEASE=1
done

CURRENT=$(python3 -c "import json; print(json.load(open('${MANIFEST}'))['version'])")
echo "Aktuelle Version: $CURRENT"

case "$1" in
  patch|minor|major|build)
    NEW=$(python3 - "$CURRENT" "$1" <<'PY'
import sys
cur, kind = sys.argv[1], sys.argv[2]
parts = [int(p) for p in cur.split(".")] + [0, 0, 0]
major, minor, patch, build = parts[:4]
if kind == "patch":
    patch += 1
    print(f"{major}.{minor}.{patch}")
elif kind == "minor":
    minor += 1; patch = 0
    print(f"{major}.{minor}.{patch}")
elif kind == "major":
    major += 1; minor = 0; patch = 0
    print(f"{major}.{minor}.{patch}")
elif kind == "build":
    build += 1
    print(f"{major}.{minor}.{patch}.{build}")
PY
)
    ;;
  *)
    if [[ ! "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+(\.[0-9]+)?(-[A-Za-z0-9.]+)?$ ]]; then
      echo "✗ Ungültige Version: $1 (erwartet: x.y.z oder x.y.z.b, optional -prerelease)" >&2
      exit 1
    fi
    NEW="$1"
    ;;
esac

echo "Neue Version:     $NEW"
read -p "Fortfahren? [y/N] " -n 1 -r; echo
[[ $REPLY =~ ^[Yy]$ ]] || { echo "Abgebrochen."; exit 0; }

# manifest.json — Version setzen UND Keys sortieren (hassfest-konform)
python3 - "$MANIFEST" "$NEW" <<'PY'
import json, sys
from collections import OrderedDict

path, new = sys.argv[1], sys.argv[2]
data = json.load(open(path))
data["version"] = new

# hassfest verlangt: domain, name zuerst, dann alphabetisch
ordered = OrderedDict()
ordered["domain"] = data.pop("domain")
ordered["name"] = data.pop("name")
for k in sorted(data.keys()):
    ordered[k] = data[k]

with open(path, "w") as f:
    json.dump(ordered, f, indent=2, ensure_ascii=False)
    f.write("\n")
print(f"✓ {path} → {new} (Keys sortiert)")
PY

# CHANGELOG
TODAY=$(date +%Y-%m-%d)
python3 - "$CHANGELOG" "$NEW" "$TODAY" <<'PY'
import sys, re, os
path, ver, today = sys.argv[1], sys.argv[2], sys.argv[3]
section = f"""## [{ver}] — {today}

### Hinzugefügt
- _todo_

### Geändert
- _todo_

### Behoben
- _todo_

"""
if not os.path.exists(path):
    open(path, "w").write("# Changelog\n\n" + section)
    print(f"✓ {path} neu angelegt mit Sektion [{ver}]")
else:
    text = open(path).read()
    m = re.search(r"^## \[", text, re.M)
    out = (text[:m.start()] + section + text[m.start():]) if m else (text + "\n" + section)
    open(path, "w").write(out)
    print(f"✓ {path} um Sektion [{ver}] erweitert")
PY

if [ "$DO_RELEASE" = "1" ]; then
  echo
  echo "── Bitte CHANGELOG-Platzhalter jetzt ausfüllen ──"
  read -p "Fertig? Drücke Enter um Commit + Tag + Push auszulösen…"

  git add "$MANIFEST" "$CHANGELOG"
  git commit -m "chore: release v${NEW}"
  git tag "v${NEW}"
  git push
  git push --tags
  echo
  echo "✓ v${NEW} gepusht. release.yml sollte jetzt laufen:"
  echo "  https://github.com/Lexorius/alternative_time/actions"
else
  echo
  echo "→ Trage die Änderungen unter '## [$NEW]' im CHANGELOG nach."
  echo "→ Dann manuell:"
  echo "    git add ${MANIFEST} ${CHANGELOG}"
  echo "    git commit -m \"chore: release v${NEW}\""
  echo "    git tag v${NEW}"
  echo "    git push && git push --tags"
fi
