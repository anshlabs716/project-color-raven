#!/bin/bash
# Read-only APK inventory: package, version, label, sdk, perms, shared-user, path.
# Debian aapt2 segfaults on some APKs; old aapt fails on others — run both and
# use whichever produces a valid `package:` line; merge label from either.
# Usage: inventory_apks.sh <root-dir> <out-tsv>
ROOT="$1"; OUT="$2"
: > "$OUT"
find "$ROOT" -name "*.apk" -type f | sort | while read -r apk; do
  rel="${apk#$ROOT/}"
  b2="$(aapt2 dump badging "$apk" 2>/dev/null)"
  b1="$(aapt dump badging "$apk" 2>/dev/null)"
  # prefer output that has a package line
  case "$b2" in "package: name="*) b="$b2";; *) b="$b1";; esac
  case "$b" in "package: name="*) ;; *) b="$b2$'\n'$b1";; esac

  pkg="$(printf '%s\n' "$b" | grep -m1 "^package: " | sed -n "s/^package: name='\([^']*\)'.*/\1/p")"
  ver="$(printf '%s\n' "$b" | grep -m1 "^package: " | sed -n "s/.*versionCode='\([^']*\)'.*/\1/p")"
  # label: default locale, then English, then any locale, then application: label=
  label="$(printf '%s\n' "$b" | sed -n "s/^application-label:'\([^']*\)'.*/\1/p" | head -1)"
  [ -z "$label" ] && label="$(printf '%s\n' "$b" | sed -n "s/^application-label-en[^:]*:'\([^']*\)'.*/\1/p" | head -1)"
  [ -z "$label" ] && label="$(printf '%s\n' "$b" | sed -n "s/^application-label-[^:]*:'\([^']*\)'.*/\1/p" | head -1)"
  [ -z "$label" ] && label="$(printf '%s\n' "$b" | sed -n "s/^application: label='\([^']*\)'.*/\1/p" | head -1)"
  # discard junk labels: format specifiers or non-ASCII (unresolved resource refs)
  case "$label" in
    *%*) label="" ;;
  esac
  if [ -n "$label" ] && ! printf '%s' "$label" | grep -qP '^[\x20-\x7E]+$'; then label=""; fi
  sdk="$(printf '%s\n' "$b" | grep -m1 "^package: " | sed -n "s/.*sdkVersion:'\([^']*\)'.*/\1/p")"
  [ -z "$sdk" ] && sdk="$(printf '%s\n' "$b" | grep -m1 "^sdkVersion:" | sed -n "s/^sdkVersion:'\([^']*\)'.*/\1/p")"
  perms="$(printf '%s\n' "$b" | grep -c '^uses-permission')"
  suid="$(printf '%s\n' "$b" | grep -m1 "^package: " | grep -o "sharedUserId='[^']*'" | sed "s/sharedUserId='//;s/'//")"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "${pkg:-?}" "${label:-}" "$ver" "$sdk" "$perms" "${suid:-}" "$rel" >> "$OUT"
done
echo "inventory written: $OUT ($(wc -l < "$OUT") rows)"
