#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "usage: $0 PROJECT_DIR IDF_COMMAND [IDF_ARGUMENT ...]" >&2
    echo "example: $0 firmware/video/bench build" >&2
    exit 2
fi

readonly repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
project_dir="$1"
shift

if [[ "${project_dir}" != /* ]]; then
    project_dir="${repo_root}/${project_dir}"
fi

readonly idf_path="${repo_root}/.tools/esp-idf-v4.4.8"
export IDF_TOOLS_PATH="${repo_root}/.tools/idf-tools-v4.4.8"

if [[ ! -f "${idf_path}/export.sh" ]]; then
    echo "ERROR: ESP-IDF v4.4.8 is not installed at ${idf_path}" >&2
    exit 1
fi
if [[ ! -d "${project_dir}" ]]; then
    echo "ERROR: project directory does not exist: ${project_dir}" >&2
    exit 1
fi

# shellcheck disable=SC1091
source "${idf_path}/export.sh" >/dev/null
cd "${project_dir}"
exec idf.py "$@"
