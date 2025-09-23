#!/usr/bin/env bash
# usage: scripts/verify_evidence.sh "src/file.ts:L10-L12" "path/to/x.js:L3-L7" ...
set -euo pipefail
invalid=0
for ref in "$@"; do
  if [[ ! "$ref" =~ ^(.+):L([0-9]+)-L([0-9]+)$ ]]; then
    echo "Invalid format: $ref (expected <path>:Lx-Ly)"
    invalid=1
    continue
  fi
  path="${BASH_REMATCH[1]}"
  start="${BASH_REMATCH[2]}"
  end="${BASH_REMATCH[3]}"
  if [ ! -f "$path" ]; then
    echo "Missing file: $path"
    invalid=1
    continue
  fi
  lines=$(wc -l < "$path" | tr -d ' ')
  if [ "$start" -lt 1 ] || [ "$end" -lt "$start" ] || [ "$end" -gt "$lines" ]; then
    echo "Invalid range in $ref (file has $lines lines)"
    invalid=1
  fi
done
exit $invalid
