#!/usr/bin/env bash
set -eu
project=$(cd "$(dirname "$0")/.." && pwd)
root=$(dirname "$project")
evidence="$project/evidence"
mkdir -p "$evidence/screenshots"
cd "$root/OsdagBridge"
export DISPLAY=127.0.0.1:72
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export PYTHONUNBUFFERED=1
export MPIR_CVAR_CH3_INTERFACE_HOSTNAME=127.0.0.1
/usr/lib/xorg/Xorg :72 -config "$project/scripts/osdag-xorg.conf" -logfile "$evidence/logs/xorg-launch.log" -noreset -nolisten unix -nolisten local -listen tcp -ac > "$evidence/logs/xorg-console.log" 2>&1 &
display_pid=$!
app_pid=
trap 'if [[ -n "$app_pid" ]]; then kill "$app_pid" 2>/dev/null || true; fi; kill "$display_pid" 2>/dev/null || true' EXIT
for ((i=0;i<20;i++)); do
  if xdpyinfo >/dev/null 2>&1; then break; fi
  sleep 1
done
xdpyinfo >/dev/null
"$root/osdag-miniconda/envs/osdagbridge-env/bin/python" -m osdagbridge.desktop > "$evidence/logs/desktop-launch.log" 2>&1 &
app_pid=$!
for ((i=0;i<30;i++)); do
  if ! kill -0 "$app_pid" 2>/dev/null; then wait "$app_pid"; exit 1; fi
  xwininfo -root -tree > "$evidence/logs/window-tree.log"
  if rg -q '"OsdagBridge"' "$evidence/logs/window-tree.log"; then
    sleep 3
    kill -0 "$app_pid"
    import -window root "$evidence/screenshots/wp1-desktop-launch.png"
    exit 0
  fi
  sleep 1
done
exit 1
