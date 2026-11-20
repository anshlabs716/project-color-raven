# Changelog

## 2026-11-21 — **v0.2 BUILD ASSEMBLED** (sideload package)

- Built `build/out/project-color-raven-v0.2-raven-sideload.zip` (3.04 GB) —
  recovery-native A/B OTA package (`adb sideload`), images identical to v0.1
  (donor userspace as-is + LineageOS foundation; no repack)
- Wrote `tools/build/gen_payload.py`: CrAU v2 payload generator (unsigned,
  minor_version=8, REPLACE ops 64 MiB, global data_offset, per-op sha256,
  dynamic_partition_metadata for super resize)
- Bug found by self-test & fixed: `data_offset` is global across partitions —
  per-partition reset made dtbo fail (read boot's bytes)
- Format ground truth verified against the real LineageOS signed OTA:
  METADATA_SIZE = 24 + manifest_size; METADATA_HASH = sha256(header+manifest)
- Self-test: independent parser (payload_dumper) verified ALL 11 partitions
  op-by-op and image-by-image against sources — ALL PASS
- Wrote `tools/build/make_sideload_zip.py`: hand-rolled stored zip (zipfile
  streaming hits 3 GB guard; auto-extras broke offsets) with exact
  ota-property-files offsets verified by PK-magic probe; `unzip -t` clean
- Install flow: sideload → factory reset (FBE fix for reported symptom (b)) → reboot
- **No device commands executed. Phone untouched.**

## 2026-11-20 — **v0.1 BUILD ASSEMBLED** (first installable package)

- Built `build/out/project-color-raven-v0.1-raven.zip` (3.78 GB, integrity-tested):
  - **Foundation (LineageOS 24 nightly, hash-verified):** boot, dtbo, vendor_boot,
    vbmeta ×3, vendor, vendor_dlkm (Tensor GS101 HALs + 323 modules)
  - **Userspace (ColorOS 17 donor, byte-identical, EROFS):** system, system_ext, product
  - **Addon:** complete GCam split package (base + 30 splits, minSdk 37, arm64-v8a)
    in `extras/gcam/splits/` — NOT auto-installed (vanilla policy)
  - `flash-all.sh` / `flash-all.bat`: raven + unlocked gates, typed confirmation,
    two-stage flash (bootloader → fastbootd), **zero wipe/erase/format commands**
- **Compatibility verification (Stage 5, evidence-based)** — see
  `reports/stage5-compatibility-matrix.md`:
  - raven kernel = GKI **6.1.162-android14**; decompressed kernel (35.7 MB) and
    **confirmed EROFS built-in** → donor EROFS images mountable
  - super capacity parsed from `super_empty.img`: group max ≈ 8.53 GiB,
    base usage 4.42 GiB → **≈ 3.8 GiB headroom** (donor system_ext growth fits)
  - donor & base both Android 17 / SDK 37 / SPL 2026-11-01
  - AVB: root vbmeta flags=3; vbmeta_system/vendor flags=0 → flash with
    `--disable-verity --disable-verification` (in scripts); never re-lock bootloader
  - signing: full-donor userspace is internally key-consistent (mixing donor
    priv-apps into LineageOS userspace ruled out)
- **Porting architecture documented (Stage 6)** — `reports/stage6-porting-architecture.md`:
  release ladder v0.1→v1.0, v0.2 EROFS repack pipeline (mkfs.erofs --file-contexts),
  failure→response table
- Build report: `reports/build/v0.1-build-report.md`
- GCam verified compatible (static): package/SDK/ABI checked; camera function
  pending on-device test
- Blockers logged: APK signing-block cert parser incomplete; web search provider
  down all session (all evidence first-party)
- **No device commands executed. Phone untouched.**

## 2026-11-20 — Project initialization (read-only audit)

- Created workspace `/home/ansh/work/project-color-raven`.
- Verified donor archive `oneplus 15 color os 17.zip`:
  - outer ZIP → stored inner ZIP `985c20bef2bd46aeb9fd3abddb71b763.zip`
  - inner SHA-256 `0f9bdd0a…11742` **matches** `FWAtlas.com.txt`
  - OTA payload layout confirmed (no raw partition images at top level).
- Verified base archive `lineage-24.0-20261116-nightly-raven-signed.zip`:
  signed A/B OTA, raven, Android 17 / SDK 37 / SPL 2026-11-01.
- Inventoried host toolchain and disk/RAM (49 GB free, 7.3 GB RAM + 6.2 GB swap).
- Added `tools/analysis/payload_manifest.py` (read-only payload metadata parser).
- Added project documentation set (README, STATUS, PLAN, DECISIONS, LIMITATIONS, SECURITY).
- **No device commands executed. No files deleted. No archives modified.**

## 2026-11-20 — Stage 3/4 payload manifest analysis

- Parsed both OTA manifests with installed `payload-dumper` (AOSP schema).
- Base: 21 partitions / 5.00 GB (raven full OTA, Android 17).
- Donor: 65 partitions / 12.87 GB (ColorOS 17 CN, minor_version=9).
- Classified: 14 shared names, 7 base-only (Tensor bootloader), 51 donor-only
  (44 = Qualcomm/OnePlus hardware → INCOMPATIBLE, never flash).
- Identified porting surface: donor `system`/`system_ext`/`product` +
  selective `odm`/`my_*`; debloat zones `my_stock`+`my_product` (6.2 GB).
- Reports: `reports/donor-analysis/partitions.md`, partition JSONs copied.
