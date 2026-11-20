# Project Status

Last updated: 2026-11-20 (Stage 1–2 audit, read-only)

## Summary

| Area | State |
|---|---|
| Phone modification | **None. Zero.** Device untouched; still on Project Infinity-X. |
| Donor archive validity | **VERIFIED** — inner ZIP SHA-256 matches FWAtlas manifest |
| Base archive validity | **VERIFIED** — signed LineageOS A/B OTA for raven, Android 17 |
| Workspace | Created at `/home/ansh/work/project-color-raven` |
| Source tree | Not downloaded (by design — storage plan required first) |
| ROM build | Not started |

## Confirmed facts

- Donor outer ZIP contains an **uncompressed inner ZIP**
  (`985c20bef2bd46aeb9fd3abddb71b763.zip`, 9,584,855,370 B).
  SHA-256 of inner ZIP = `0f9bdd0afa39c7dbd0687100a2a80bbdf68ab0f74fc766dd8cc2047ee9011742`
  → **exact match** to `FWAtlas.com.txt` inside the package.
- Inner package is an **OTA layout**: `payload.bin` (9,584,849,182 B),
  `payload_properties.txt`, `care_map.pb`, `metadata(.pb)`.
  It is **not** a collection of raw `system.img`/`vendor.img` files.
- LineageOS ZIP is a **signed A/B OTA**: `payload.bin` (1,442,544,005 B) only.
  - `post-build` = `google/raven/raven:17/CP3A.261005.002.A1/16269273:user/release-keys`
  - `post-sdk-level=37` (Android 17), `post-security-patch-level=2026-11-01`
  - `pre-device=raven`, `ota-type=AB`
- Host: Debian 13 trixie, amd64, Intel N150 (4 cores), 7.3 GB RAM + 6.2 GB swap,
  **49 GB free disk** (workspace budget ~45 GB — tight but workable with discipline).
- Toolchain present: Temurin JDK 17.0.21, Python 3.13.5 (+`protobuf` 4.21.12),
  git 2.47.3, adb/fastboot 34.0.5 (Debian), Android SDK (build-tools 35/36,
  platforms android-35/36/**37.1**), aapt/aapt2, mkbootimg/unpack_bootimg, avbtool,
  simg2img, brotli, 7z, zstd, `payload-dumper` (user local), jq, sqlite3, xmlstarlet.

## Open questions (need next stages)

1. Which partitions does the donor payload contain? (parse both manifests — in progress)
2. What exactly is in the LineageOS payload (system/system_ext/product/vendor/vendor_dlkm…)?
3. Are the loose `boot.img`/`dtbo.img`/`vbmeta.img`/`vendor_boot.img` Pixel factory
   images, LineageOS outputs, or something else? (fingerprints not yet compared)
4. `/home/ansh/firmware/` turned out to be an **unrelated PlatformIO project**,
   not Pixel firmware — do not rely on it.

## Does not work yet

Everything porting-related. Nothing has been built, extracted or flashed.
