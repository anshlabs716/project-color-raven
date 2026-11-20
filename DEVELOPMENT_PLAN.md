# Development Plan

Staged plan per the master prompt. **No stage that modifies the phone begins
without explicit owner approval.**

## Stage 1 — Environment audit ✅ DONE (2026-11-20)

Confirmed: Debian 13 amd64, 4-core N150, 7.3 GB RAM + 6.2 GB swap, 49 GB free,
JDK 17, Python 3.13 + protobuf, git, adb/fastboot (device NOT used), SDK with
platform android-37.1, payload-dumper, avbtool, mkbootimg, aapt2, 7z/zstd/brotli.

Missing vs. a full AOSP build: `repo` launcher, ccache, and — most importantly —
~40 GB+ of source + out/ tree that does not fit comfortably in 49 GB free.
**Decision: do not fetch a full source tree yet.** Work from payloads/images first.

## Stage 2 — Input audit ✅ DONE (2026-11-20)

- Donor ZIP: valid, inner SHA-256 matches FWAtlas manifest. OTA layout, payload 9.58 GB.
- LineageOS ZIP: valid, signed A/B OTA for raven, Android 17 / SDK 37 / SPL 2026-11-01.
- Loose images inventoried (boot/dtbo/vbmeta/vendor_boot/super_empty), `fwmanifest.xml`
  identified as a mislabeled framework AndroidManifest dump.
- Checksums + inventory recorded under `input/`.

## Stage 3 — Donor analysis (NEXT, in progress)

1. Parse donor `payload.bin` manifest → partition list, op types, sizes.
   (script: `tools/analysis/payload_manifest.py`)
2. Extract selected metadata only (build.prop reads, package lists) — no bulk extraction.
3. Inventory: system apps, framework JARs, services, permissions, AI packages,
   Chinese-only services, OnePlus-specific assumptions.
4. Write `reports/donor-analysis/*`.

## Stage 4 — Base analysis

1. Parse LineageOS payload manifest → partition list.
2. Identify Pixel hardware support present in the base.
3. List device/kernel/vendor repos actually required for a raven build.
4. Write `reports/base-analysis/*`.

## Stage 5 — Compatibility matrix

Per component: donor location, base equivalent, HW/FW dependency, required
modifications, status, testing, limitations → `reports/compatibility/`.

## Stage 6 — Porting design

Architecture for integration: framework vs. app vs. vendor separation;
decide reuse/adapt/replace/reject per component. Owner review gate.

## Stage 7 — Implementation (incremental)

One subsystem at a time, patches under `framework/patches/`, every change logged
in `CHANGELOG.md` and `DECISIONS.md`.

## Stage 8 — Testing

Requires owner-approved flashing (explicitly NOT yet approved).
Read-only tests possible earlier: payload extraction validation, APK install-
ability checks via aapt, static dependency analysis.

## Stage 9 — Release preparation

Only after Stage 8 evidence. Never a renamed donor/base ZIP.

## Resource guardrails

- Check `df -h` before any extraction > 5 GB; check `free -h` before builds.
- One extracted payload at a time; delete intermediates after analysis (with approval).
- No parallel compiles; incremental only; stay under ~45 GB workspace.
