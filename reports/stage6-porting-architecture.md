# Stage 6 — Porting Architecture

Date: 2026-11-20 · Project Color Raven

## Architecture: image-level integration, staged by risk

```
┌─────────────────────────── raven (Pixel 6 Pro) ───────────────────────────┐
│  Bootloader (Google, untouched) · unlocked · NEVER re-locked               │
├───────────────────────────────────────────────────────────────────────────┤
│  BOOT CHAIN (LineageOS 24, proven):  boot · dtbo · vendor_boot · vbmeta*   │
│  KERNEL: GKI 6.1.162-android14 — EROFS ✅, ext4 ✅, f2fs ✅ (verified)      │
├───────────────────────────────────────────────────────────────────────────┤
│  VENDOR LAYER (LineageOS 24, proven):  vendor · vendor_dlkm               │
│  Tensor GS101 HALs + 323 modules — Pixel hardware compatibility           │
├───────────────────────────────────────────────────────────────────────────┤
│  USERSPACE (ColorOS 17 donor):  system · system_ext · product             │
│  v0.1: donor images as-is (hash-verified, internally consistent signing)  │
│  v0.2+: EROFS repack — debloat + SELinux relabel + fixes                  │
├───────────────────────────────────────────────────────────────────────────┤
│  ADDONS (never auto-installed): GCam splits, microG (owner opt-in only)   │
└───────────────────────────────────────────────────────────────────────────┘
```

**Rule:** hardware belongs to LineageOS (Tensor proven), experience belongs to
ColorOS (donor userspace). The boundary is the vendor/userspace HAL interface.

## Release ladder

| Version | Content | Purpose | Gate to next |
|---|---|---|---|
| **v0.1** (built 2026-11-20) | Donor userspace as-is + LineageOS boot/vendor | Ground truth: does ColorOS userspace boot on Tensor vendor? | Owner flash + boot result observed |
| **v0.2** | EROFS repack of donor userspace: remove Qualcomm INCOMPATIBLE (21) + approved REMOVE list, relabel SELinux via combined file_contexts | Remove known-broken services; reduce crash-loop noise | v0.1 boot log + repack tooling validated |
| **v0.3** | Telephony: donor RIL binding analysis, IMS strategy (donor IMS vs LineageOS telephony backport) | Cellular/SMS/data working | Owner device test |
| **v0.4** | Framework depth: oplus framework jars on boot classpath (requires image-level `etc/boot-image.prof`/`boot-tools` surgery or accept feature loss), SystemUI decision | ColorOS experience depth | iterative |
| **v1.0** | OTA-flashable zip (recovery/A-B payload) + microG optional module | Daily-driver candidate | owner acceptance |

## v0.2 repack pipeline (defined now, gated on v0.1 results)

1. `fsck.erofs --extract --xattrs` donor trees (labels live in image; extraction as non-root drops them — **source labels from donor `*_file_contexts` files inside the images instead**)
2. Apply approved debloat set (per DEBLOAT_POLICY §L — owner-approved lists only)
3. Merge GCam splits into `product/app/GoogleCamera/` (owner decision pending — policy: no auto-app installs)
4. `mkfs.erofs --file-contexts <combined contexts>` with uid/gid policy (confirm `--force-uid/gid` support; most files uid 0)
5. Size check against super headroom (≈3.8 GiB margin)
6. Package + checksums + owner approval before any flash

## Fallbacks / risk responses

| Failure on v0.1 boot | Response |
|---|---|
| Bootloop (VINTF strict / system_server crash) | Capture boot stage from owner description; v0.2 repack with VINTF manifest relaxation or vendor-compat overrides |
| Boots, telephony dead | v0.3: keep LineageOS `com.android.phone`/telephony stack inside donor userspace (swap telephony packages), donor RIL only if qcril-independent |
| Boots, IMS dead | Document as known limitation; VoLTE via carrier config iteration |
| Boots, oplus services crash-loop | v0.2 debloat (already-classified INCOMPATIBLE/REMOVE) |

## Constraints honored (standing)

- Phone: **never** flashed/wiped/rebooted by the project without the owner's
  explicit per-action go — all flash steps are owner-executed or owner-approved.
- Vanilla: no GMS in images; microG only as an owner opt-in module.
- Debloat: nothing removed without owner approval (DEBLOAT_POLICY).
- Originals in `/home/ansh/` never modified or deleted.
