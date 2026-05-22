#!/usr/bin/env bash
# build.sh — build Nextral for Linux/macOS
# Usage: ./build.sh [--installer] [--clean]

set -euo pipefail

INSTALLER=0
CLEAN=0
ROOT="$(cd "$(dirname "$0")" && pwd)"

for arg in "$@"; do
    case "$arg" in
        --installer) INSTALLER=1 ;;
        --clean)     CLEAN=1 ;;
    esac
done

echo "=== Nextral Build ==="

if [ "$CLEAN" -eq 1 ]; then
    echo "Cleaning previous build..."
    rm -rf "$ROOT/dist" "$ROOT/build"
    echo "Clean done."
fi

echo "Installing dependencies..."
python3 -m pip install -e "$ROOT[dev]" --quiet
python3 -m pip install pyinstaller --quiet
echo "Dependencies installed."

if [ "$INSTALLER" -eq 1 ]; then
    echo "Building installer..."
    pyinstaller "$ROOT/installer.spec" --distpath "$ROOT/dist" --workpath "$ROOT/build"
    echo "Installer built: dist/nextral-installer/"
else
    echo "Building main app..."
    pyinstaller "$ROOT/nextral.spec" --distpath "$ROOT/dist" --workpath "$ROOT/build"
    echo "App built: dist/nextral/"
    echo ""
    echo "To run: ./dist/nextral/nextral"
fi
