#!/usr/bin/env bash
set -euo pipefail

readonly library_url="https://github.com/aquaticus/esp32_composite_video_lib.git"
readonly library_commit="a1f5c7669aa274f148157947cdb7c94459e23777"
readonly destination="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/components/esp32_composite_video_lib"

if [[ -d "${destination}/.git" ]]; then
    actual="$(git -C "${destination}" rev-parse HEAD)"
    if [[ "${actual}" != "${library_commit}" ]]; then
        echo "ERROR: ${destination} is at ${actual}, expected ${library_commit}" >&2
        exit 1
    fi
    echo "Composite-video dependency already pinned at ${library_commit}"
    exit 0
fi

if [[ -e "${destination}" ]]; then
    echo "ERROR: ${destination} exists but is not a Git checkout" >&2
    exit 1
fi

git clone --no-checkout "${library_url}" "${destination}"
git -C "${destination}" checkout --detach "${library_commit}"

actual="$(git -C "${destination}" rev-parse HEAD)"
[[ "${actual}" == "${library_commit}" ]]
echo "Fetched GPL-3.0-or-later bench dependency at ${actual}"
