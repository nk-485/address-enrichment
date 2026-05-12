#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install -r requirements-build.txt
PYINSTALLER_CONFIG_DIR="$PWD/.pyinstaller-cache" python3 -m PyInstaller --clean --noconfirm address_enrichment_app.spec

echo
echo "Built standalone app in:"
echo "  dist/AddressEnrichment"
echo
echo "Put a .env file next to the executable if you want to preconfigure the API key."
