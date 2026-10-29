#!/bin/bash
set -euo pipefail

remote='mosaic_hostel_media:'
destination="$HOME/Projects/Hostel Content"
rclone='/opt/homebrew/bin/rclone'

# A failed or empty Drive listing must not erase the local mirror.
count=$("$rclone" lsf "$remote" --recursive --files-only | wc -l | tr -d ' ')
if [ "$count" -eq 0 ]; then
  echo 'Drive folder is empty or unavailable; local media was left untouched.' >&2
  exit 1
fi

mkdir -p "$destination"
"$rclone" sync "$remote" "$destination" --max-delete 50 --log-level INFO
