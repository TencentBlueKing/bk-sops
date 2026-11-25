#!/bin/bash
set -euo pipefail

if [[ "$(uname -s)" != "Linux" ]]; then
    exit 0
fi

# The Python buildpack packages this directory with the application.
build_dir="$(cd "$(dirname "$0")/.." && pwd -P)"
python_home="$build_dir/.heroku/python"
if [[ ! -x "$python_home/bin/python" ]]; then
    exit 0
fi

python_bin="$(readlink -f "$python_home/bin/python")"
if [[ "$python_bin" != "$python_home/bin/"* ]]; then
    printf 'Python interpreter resolves outside the build directory\n' >&2
    exit 1
fi

# The isolated renderer starts Python with a restricted environment.
if startup_error="$(env -i "$python_bin" -I -S -c 'import socket' 2>&1)"; then
    exit 0
fi

python_library="$("$python_bin" -I -S -c 'import sysconfig; print(sysconfig.get_config_var("INSTSONAME") or "")')"
if [[ "$python_library" != libpython*.so* ||
      "$startup_error" != *"error while loading shared libraries: $python_library:"* ||
      ! -f "$python_home/lib/$python_library" ]]; then
    printf '%s\n' "$startup_error" >&2
    exit 1
fi

patchelf_bin="$(command -v patchelf || true)"
if [[ -z "$patchelf_bin" ]]; then
    patchelf_dir="$(mktemp -d)"
    trap 'rm -rf -- "$patchelf_dir"' EXIT
    "$python_bin" -m pip --disable-pip-version-check --no-cache-dir install \
        --no-deps --only-binary=:all: --target "$patchelf_dir" 'patchelf==0.18.0.0'
    patchelf_bin="$patchelf_dir/bin/patchelf"
fi

existing_runpath="$("$patchelf_bin" --print-rpath "$python_bin")"
"$patchelf_bin" --set-rpath '$ORIGIN/../lib'"${existing_runpath:+:$existing_runpath}" "$python_bin"
env -i "$python_bin" -I -S -c 'import socket'
printf 'Verified Python startup with the bundled library search path\n'
