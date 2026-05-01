#!/usr/bin/env bash
# Baut lokal das Release-ZIP genauso wie der GitHub-Release-Workflow.
# Output: dist/haushaltsdoku.zip
set -euo pipefail

cd "$(dirname "$0")/.."

DOMAIN="haushaltsdoku"
SRC="custom_components/${DOMAIN}"
DIST="dist"
ZIP="${DIST}/${DOMAIN}.zip"

if [ ! -d "$SRC" ]; then
  echo "✗ Quellverzeichnis '$SRC' fehlt." >&2
  exit 1
fi

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
