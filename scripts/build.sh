#!/usr/bin/env bash
# Baut lokal das Release-ZIP genauso wie der GitHub-Release-Workflow.
# Output: dist/alternative_time.zip
#
# Optionen:
#   --no-fix    Ruff Auto-Fix überspringen
#   --strict    Build abbrechen, wenn Ruff nach --fix noch Probleme meldet
#
set -euo pipefail

cd "$(dirname "$0")/.."

DOMAIN="alternative_time"
SRC="custom_components/${DOMAIN}"
DIST="dist"
ZIP="${DIST}/${DOMAIN}.zip"

# ── Optionen ────────────────────────────────────────────────────────────────
SKIP_RUFF=0
STRICT=0
for arg in "$@"; do
  case "$arg" in
    --no-fix) SKIP_RUFF=1 ;;
    --strict) STRICT=1 ;;
    -h|--help)
      sed -n '2,9p' "$0"
      exit 0
      ;;
    *)
      echo "✗ Unbekannte Option: $arg" >&2
      exit 1
      ;;
  esac
done

if [ ! -d "$SRC" ]; then
  echo "✗ Quellverzeichnis '$SRC' fehlt." >&2
  exit 1
fi

# ── Ruff Auto-Fix ───────────────────────────────────────────────────────────
if [ "$SKIP_RUFF" = "0" ]; then
  if command -v ruff >/dev/null 2>&1; then
    echo "→ Ruff Auto-Fix (custom_components/)"
    # E501 (line-too-long) wird bewusst ignoriert: das Plugin enthält
    # mehrsprachige Beschreibungs-Strings, die nicht sinnvoll umgebrochen
    # werden können. Alle anderen Checks (Imports, ungenutzte Variablen,
    # bare except, etc.) bleiben aktiv.
    set +e
    ruff check custom_components/ --select E,F,W,I --ignore E501 --fix
    RUFF_EXIT=$?
    set -e

    if [ "$STRICT" = "1" ] && [ "$RUFF_EXIT" -ne 0 ]; then
      echo "✗ Ruff meldet nach --fix noch Probleme (--strict aktiv)." >&2
      exit 1
    fi

    # Hinweis bei nicht-leerem git diff
    if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
      if ! git diff --quiet "$SRC" 2>/dev/null; then
        echo
        echo "⚠ Ruff hat Quelldateien geändert. Bitte committen vor Release:"
        echo "    git add ${SRC} && git commit -m 'style: ruff auto-fix'"
        echo
      fi
    fi
  else
    echo "⚠ ruff nicht installiert – überspringe Auto-Fix"
    echo "   Installation: pip install ruff"
  fi
else
  echo "→ Ruff Auto-Fix übersprungen (--no-fix)"
fi

# ── Version aus manifest.json ───────────────────────────────────────────────
VERSION=$(python3 -c "import json; print(json.load(open('${SRC}/manifest.json'))['version'])")

echo "→ Baue ${DOMAIN} v${VERSION}"

# pycache & .DS_Store etc. wegräumen
find "$SRC" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
find "$SRC" -name '.DS_Store' -delete 2>/dev/null || true

mkdir -p "$DIST"
rm -f "$ZIP"

(
  cd "$SRC"
  zip -rq "${OLDPWD}/${ZIP}" . \
    -x "__pycache__/*" "*/__pycache__/*" "*.pyc" ".DS_Store"
)

echo
echo "✓ Fertig: $ZIP"
echo
echo "── Inhalt ──"
unzip -l "$ZIP"
echo
echo "── Größe ──"
ls -lh "$ZIP" | awk '{print $5}'
echo
echo "Tag-Vorschlag:  git tag v${VERSION} && git push origin v${VERSION}"
