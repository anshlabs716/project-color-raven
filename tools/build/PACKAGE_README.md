# Project Color Raven v0.1 — raven (Google Pixel 6 Pro)

**First experimental ColorOS-on-Tensor hybrid build. Status: ASSEMBLED, AUDITED, NOT BOOT-TESTED.**

## What this is

| Component | Source | Why |
|---|---|---|
| `boot.img`, `dtbo.img`, `vendor_boot.img` | **LineageOS 24 nightly 2026-11-16** | Proven raven boot chain (GKI 6.1.162-android14 kernel) |
| `vbmeta.img`, `vbmeta_system.img`, `vbmeta_vendor.img` | **LineageOS 24** | LineageOS AVB keys; flashed with verification disabled |
| `vendor.img`, `vendor_dlkm.img` | **LineageOS 24** | Tensor GS101 HALs + 323 kernel modules — required for Pixel 6 Pro hardware |
| `system.img`, `system_ext.img`, `product.img` | **ColorOS 17 (OnePlus 15 donor, CP2A.260605.016, SDK 37)** | The ColorOS userspace — byte-identical to the donor payload (hash-verified at extraction and again inside this zip) |
| `super_empty.img` | Reference ONLY — **never flash it** | LP metadata: dynamic-partition group max ≈ 8.53 GiB |
| `extras/gcam/splits/` | APKMirror bundle | Complete Pixel Camera split package (base + 30 splits), minSdk 37, arm64-v8a |

## Verified before assembly (independent audit 2026-11-20)

- All 11 images SHA-256-match their verified sources **inside the shipped zip**
- Kernel **GKI 6.1.162-android14**: EROFS built-in (kernel decompressed + string-verified) → donor EROFS images mount on raven
- `vendor_boot` contains `raven` + `gs101` (Tensor) identifiers; `vendor_dlkm` = 323 Exynos/GS101 modules
- Super headroom ≈ 3.8 GiB — donor `system_ext` (0.93 GiB) fits via fastbootd auto-resize
- Donor & base both Android 17 / SDK 37 / SPL 2026-11-01
- `flash-all.sh` audited: **zero** wipe/erase/format tokens; flashes exactly 11 partitions; device+unlocked gates; typed confirmation

## ⚠️ Data safety — read before flashing

- The script contains **no wipe commands** and does not touch userdata.
- **BUT:** this is a cross-ROM userspace swap. If your current ROM's file-based
  encryption / keystore policy differs from what the new userspace expects,
  userdata may fail to decrypt after boot — in that case a **factory reset is
  required and WILL erase your data.**
- **Back up your phone before flashing.** Assume data may be lost.

## Known risks (honest)

- **First boot not guaranteed.** ColorOS userspace expects some Qualcomm/oPlus vendor HALs that raven's Tensor vendor does not provide. Expected outcomes range from "boots with broken telephony/IMS and some crash-looping Oplus services" to "bootloop". This is exactly what v0.1 is for: finding out.
- Donor packages include Qualcomm/QTI apps (inert-but-present in v0.1; removal planned in v0.2).
- GCam splits are **not auto-installed** (vanilla policy). After first boot:
  `adb install-multiple extras/gcam/splits/base.apk extras/gcam/splits/split_*.apk`
  Camera function on-device is **unverified** until you test it.
- Anti-rollback: if your bootloader has a **higher** stored rollback index than this build's SPL (2026-11-01), the bootloader may refuse to boot it. If that happens, report it — do not attempt workarounds.

## How to flash (from a computer)

```
unzip project-color-raven-v0.1-raven.zip
cd project-color-raven-v0.1-raven
./flash-all.sh          # Linux/macOS   (Windows: flash-all.bat)
```

**Order (safety-critical, audited):**
1. Enter **fastbootd** (from the running system: `adb reboot fastboot`) — the logical partitions are flashed **first**, while fastbootd runs under your current, fully-consistent boot chain. No half-updated device ever boots.
2. Reboot to **bootloader** (never boots the OS) → flash boot chain + vbmeta×3 (verification disabled).
3. One final reboot into the fully flashed device.

The script checks device = raven + unlocked bootloader and requires typing
`FLASH-RAVEN`. It contains **no wipe/erase/format commands**.

## Rollback — what is actually true

- The script never wipes anything, so userdata **as stored on disk** is untouched by the flash itself.
- If first boot fails, the bootloader may automatically fall back to the **inactive slot**, which still holds your previous ROM (Infinity-X).
- Otherwise: put the phone in fastboot and re-flash your LineageOS nightly
  (`lineage-24.0-20261116-nightly-raven-signed.zip`) the way you normally
  install it.
- If the new userspace cannot decrypt existing userdata, the only fix is a
  **factory reset (data loss)** — this is the case the backup warning covers.

## Never

- Never re-lock the bootloader after flashing this (bricks the device).
- Never flash `super_empty.img` to the device (destroys the dynamic partition layout).

## Integrity

`checksums.txt` — SHA-256 of every file in this package.
Build provenance: github.com/anshlabs716/project-color-raven
