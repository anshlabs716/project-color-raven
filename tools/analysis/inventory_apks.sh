#!/bin/bash
# Read-only APK inventory: package name, version, label, shared-user, permissions count
# Usage: inventory_apks.sh <root-dir> <out-tsv>
ROOT="$1"; OUT="$2"
: > "$OUT"
find "$ROOT" -name "*.apk" -type f | sort | while read -r apk; do
  rel="${apk#$ROOT/}"
  # try aapt2 first, then aapt
  b="$(aapt2 dump badging "$apk" 2>/dev/null || aapt dump badging "$apk" 2>/dev/null)"
  pkg="$(printf '%s\n' "$b" | head -1 | sed -n "s/^package: name='\([^']*\)'.*/\1/p")"
  ver="$(printf '%s\n' "$b" | head -1 | sed -n "s/.*versionCode='\([^']*\)'.*/\1/p")"
  label="$(printf '%s\n' "$b" | sed -n "s/^application: label='\([^']*\)'.*/\1/p" | head -1)"
  sdk="$(printf '%s\n' "$b" | head -1 | sed -n "s/.*sdkVersion:'\([^']*\)'.*/\1/p")"
  perms="$(printf '%s\n' "$b" | grep -c '^uses-permission')"
  suid="$(printf '%s\n' "$b" | head -1 | grep -o "sharedUserId='[^']*'" | sed "s/sharedUserId='//;s/'//")"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "${pkg:-?}" "${label:-}" "$ver" "$sdk" "$perms" "${suid:-}" "$rel" >> "$OUT"
done
echo "inventory written: $OUT ($(wc -l < "$OUT") rows)"
