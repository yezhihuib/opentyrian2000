#!/bin/sh
# Ordinary play. Original game data stays external; existing marked saves survive.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ "$#" -lt 1 ]; then
    printf '%s\n' 'Usage: start-hd.sh /absolute/path/to/tyrian2000 [extra game options]' >&2
    exit 2
fi
data=$1
shift
case "$data" in /*) ;; *) printf '%s\n' 'Use an absolute original-data directory.' >&2; exit 2;; esac
[ -f "$data/tyrian1.lvl" ] || { printf '%s\n' 'Missing separately obtained Tyrian 2000 data.' >&2; exit 2; }
[ -x "$root/opentyrian2000" ] || { printf '%s\n' 'Missing Linux executable beside this launcher.' >&2; exit 2; }
profile=${OPENTYRIAN_HD_PROFILE:-${XDG_DATA_HOME:-${HOME:?}/.local/share}/OpenTyrian2000-HD/manual-first-level}
case "$profile" in /*) ;; *) printf '%s\n' 'Use an absolute OPENTYRIAN_HD_PROFILE directory.' >&2; exit 2;; esac
if [ -L "$profile" ]; then printf '%s\n' 'Choose a dedicated profile that is not a symlink.' >&2; exit 2; fi
mkdir -p -- "$profile"
if [ ! -f "$profile/.manual-hd-profile" ]; then
    if [ -n "$(find "$profile" -mindepth 1 -maxdepth 1 -print -quit)" ]; then
        printf '%s\n' 'Unmarked profile already contains files; choose a new dedicated directory.' >&2
        exit 2
    fi
    printf '%s\n' 'Dedicated OpenTyrian2000 manual first-level HD profile.' > "$profile/.manual-hd-profile"
fi
# The Unix engine ignores cwd for config/saves; isolate its actual XDG path.
if [ "$(printf '%s/opentyrian2000' "$profile" | LC_ALL=C wc -c)" -ge 500 ]; then
    printf '%s\n' 'Dedicated profile path exceeds the engine path limit.' >&2
    exit 2
fi
if [ -L "$profile/opentyrian2000" ]; then
    printf '%s\n' 'Choose a profile whose opentyrian2000 subdirectory is not a symlink.' >&2
    exit 2
fi
mkdir -p -- "$profile/opentyrian2000"
export XDG_CONFIG_HOME="$profile"
if [ ! -e "$profile/opentyrian2000/opentyrian.cfg" ]; then
    printf "%s\n" "section 'video'" "    item 'fullscreen' '-1'" "    item 'scaler' '2x'" "    item 'scaling_mode' 'Integer'" > "$profile/opentyrian2000/opentyrian.cfg"
fi
cd -- "$profile"
exec "$root/opentyrian2000" "--data=$data" "--manual-hd-assets=$root/assets/gameplay" "--startup-assets=$root/assets/startup" "--common-menu-assets=$root/assets/startup" "--hud-assets=$root/assets/shared-ui" "--global-assets=$root/assets/global" "--data-text-assets=$root/assets/data-text-zh-CN-v1" "--data-frame-assets=$root/assets/data-frame-v1" "--data-portrait-assets=$root/assets/data-portrait-v1" "$@"
