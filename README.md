# Project Color Raven

Porting **ColorOS 17** (OnePlus 15, PLK110, China) onto the **Google Pixel 6 Pro (raven)**
on top of a **LineageOS 24 / Android 17** base — as a real ROM, not a theme.

> porting color os 17 from oneplus 15 to pixel 6 pro (raven)

| | |
|---|---|
| **Target device** | Google Pixel 6 Pro (raven), Tensor GS101 |
| **Donor ROM** | OnePlus 15 ColorOS 17 China, `PLK110_17.0.1.201(CN01)` |
| **Base** | LineageOS 24 / Android 17 (SDK 37) |
| **Host** | Debian 13 (trixie), x86_64, Intel N150, 8 GB RAM |
| **Developer** | ansh |
| **Phone's current ROM** | Project Infinity-X — **must not be modified without explicit approval** |

## Goal

A cohesive ColorOS 17 experience on the Pixel 6 Pro that keeps Pixel hardware
fully working: cellular, Wi-Fi, Bluetooth, NFC, GPS, cameras, fingerprint,
audio, charging, sensors, suspend/resume — plus ColorOS UI, system apps,
Fluid Cloud, AI features, and English-first international usability.

**Vanilla build: NO GMS.** No Google Play services, no Play Store, no Google
account infrastructure, no GMS-backed apps. The ROM ships without any Google
mobile services; push/location/notification backends must work without them
(microG is *not* auto-installed — anything extra is owner-approved only).

## Hard rules (project policy)

- **No device flashing without explicit owner approval.** No fastboot flash/erase,
  no recovery installs, no slot switches, no bootloader lock/unlock, no wipes.
- Never delete or overwrite the original input archives:
  - `/home/ansh/lineage-24.0-20261116-nightly-raven-signed.zip`
  - `/home/ansh/oneplus 15 color os 17.zip`
- No full AOSP/LineageOS source download without a storage + RAM plan first.
- No claims of "works" without evidence. Status labels:
  `VERIFIED | LIKELY COMPATIBLE | NEEDS PORTING | NEEDS REPLACEMENT | INCOMPATIBLE | UNKNOWN`
- No permissive SELinux as a permanent solution; no security features disabled to boot.

## Repository layout

```
project-color-raven/
├── README.md              ← this file
├── PROJECT_STATUS.md      ← what works / what does not (evidence-based)
├── DEVELOPMENT_PLAN.md    ← staged plan, next actions
├── CHANGELOG.md           ← actual changes only
├── DECISIONS.md           ← technical decisions + rationale
├── LIMITATIONS.md         ← known compatibility limits
├── SECURITY.md            ← security posture
├── input/                 ← manifests, checksums, inventory of supplied files
├── donor/                 ← ColorOS 17 analysis (metadata only; images stay outside repo)
├── base/                  ← LineageOS 24 raven analysis
├── framework/             ← framework analysis, integration, overlays, patches
├── system/                ← apps, services, permissions, configuration
├── features/              ← clock, lockscreen, quicksettings, fluid-cloud, ai, animations
├── tools/                 ← analysis/extraction/validation/build scripts (Python, etc.)
├── scripts/               ← workflow automation
├── reports/               ← donor/base analysis, compatibility matrix, test results
├── build/                 ← intermediates, logs, output (git-ignored)
└── backups/
```

Large firmware archives and extracted partition images are **never** committed;
`.gitignore` blocks them. Only scripts, docs, metadata and reports live here.

## Input files (verified 2026-11-20)

| File | Size | Status |
|---|---|---|
| `oneplus 15 color os 17.zip` | 9,584,856,425 B | Valid. Inner firmware ZIP SHA-256 **matches** FWAtlas manifest (`0f9bdd0a…`). Contains OTA `payload.bin` (9.58 GB) for `PLK110_17.0.1.201(CN01)`. |
| `lineage-24.0-20261116-nightly-raven-signed.zip` | 1,442,551,820 B | Valid. Signed A/B OTA, `payload.bin` 1.44 GB. Fingerprint `google/raven/raven:17/CP3A.261005.002.A1/16269273:user/release-keys`, SDK 37, SPL 2026-11-01, `pre-device=raven`. |
| `boot.img` / `dtbo.img` / `vbmeta.img` / `vendor_boot.img` / `super_empty.img` | 64 MB / 16 MB / 8 KB / 64 MB / 5 KB | Present, `boot.img` recognized as Android bootimg (kernel). To be identified against Pixel factory images. |
| `fwmanifest.xml` | 605 KB | **Not** a firmware manifest — it is an Android framework `AndroidManifest.xml` dump. Mislabeled input; recorded as-is. |

## Stage overview

1. **Stage 1 — Environment audit** ✅ (see `reports/`)
2. **Stage 2 — Input audit** ✅ checksums + inventory (`input/`)
3. **Stage 3 — Donor analysis** (ColorOS partition/app/framework inventory)
4. **Stage 4 — Base analysis** (LineageOS raven contents + missing source repos)
5. **Stage 5 — Compatibility matrix**
6. **Stage 6 — Porting design**
7. **Stage 7 — Incremental implementation**
8. **Stage 8 — Testing** (with owner approval for any flash)
9. **Stage 9 — Release preparation**

See `DEVELOPMENT_PLAN.md` for the current step.

## License

GPL-3.0 (see `LICENSE`).
