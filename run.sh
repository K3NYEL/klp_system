#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

if [[ ! -x dist/klp_system ]]; then
    echo "No existe el ejecutable Linux. Primero ejecuta: ./build.sh"
    exit 1
fi

exec ./dist/klp_system "$@"
