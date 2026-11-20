# Stage 5 — Compatibility Matrix (evidence-based)

Date: 2026-11-20 · Project Color Raven · raven (Pixel 6 Pro) ← ColorOS 17 donor (OnePlus 15)

Every claim below was verified against the actual images this session. Web search
was unavailable (provider returned no results all session) — all evidence is
first-party, extracted from the artifacts themselves.

## 1. Filesystem compatibility — ✅ VERIFIED COMPATIBLE

| Question | Method | Result |
|---|---|---|
| Base system filesystem | `file` on extracted images | ext4 |
| Donor userspace filesystem | `file` on donor/partitions/*.img | EROFS (LZ4_0PADDING, BIG_PCLUSTER) |
| Does the raven kernel support EROFS? | Decompressed boot.img kernel (LZ4-legacy, 16 MiB → 35.7 MB) | **YES — built-in**: banner `Linux 6.1.162-android14-11-g7b58131aec77-ab16736902`; 271 `erofs` strings, 31 `EROFS`, registered fs name `\0erofs\0` |
| ext4 / f2fs also present | same kernel scan | yes (33 / 1264 refs) |

Consequence: donor images can be flashed **as-is** (v0.1) and any future
repack (v0.2) can be EROFS via `mkfs.erofs --file-contexts`.

## 2. Partition / super capacity — ✅ FITS

- LP metadata parsed from `super_empty.img`: groups `google_dynamic_partitions_a/b`, maximum_size ≈ **8.53 GiB**
- Base payload logical partitions sum: **4.42 GiB** → headroom **≈ 3.8 GiB**
- Donor sizes: system 1.05 GiB (base 1.19), system_ext **0.93 GiB (base 0.54 — grows, fits)**, product 0.17 GiB (base 2.04)
- fastbootd auto-resizes logical partitions to image size on flash

## 3. Android version / API — ✅ MATCHED

| | Base (LineageOS 24) | Donor (ColorOS 17) |
|---|---|---|
| SDK | 37 (Android 17) | 37 (Android 17) |
| SPL | 2026-11-01 | 2026-11-01 |
| Kernel | GKI 6.1.162-android14 | (donor: Qualcomm 5.x-class, irrelevant — we keep raven kernel) |

## 4. AVB / verified boot — ⚠️ MANAGED (no blocker)

- Root `vbmeta.img` Flags = 3 (verification disabled) — LineageOS ships this for unlockable devices
- `vbmeta_system` / `vbmeta_vendor` Flags = 0 → donor userspace would fail hash checks
- **Mitigation (in flash-all.sh):** flash all three vbmeta images with
  `--disable-verity --disable-verification`. Bootloader stays unlocked; **never re-lock** (would brick).
- Donor images are byte-identical to the donor payload (hash-verified) → no donor-side integrity concern.

## 5. SELinux metadata — ⚠️ KNOWN GAPS, PLANNED

- Donor images **do contain** `security.selinux` xattrs (fsck.erofs extraction warning proves presence)
- Base system ships full policy: `plat_file_contexts` (50 KB), `plat_sepolicy.cil` (3.4 MB), `plat_mac_permissions.xml`, `plat_property_contexts`
- Donor-side contexts are baked into donor images (fine for as-is flash); **risk**: donor `untrusted_app`/platform policy vs raven vendor labels — vendor-label mismatches surface as denials logged at boot (input for v0.2)
- v0.2 repack must label via `mkfs.erofs --file-contexts` using **combined base + donor file_contexts**

## 6. Signing / priv-app integrity — ⚠️ STRUCTURAL RISK (accepted for v0.1)

- Donor priv-apps are signed with ColorOS platform keys; base platform key is LineageOS.
- **v0.1 is internally consistent**: the *entire userspace* is donor (donor platform key = donor priv-app key) → privapp checks pass within the donor userspace.
- Cert-level confirmation was attempted (APK Signing Block parser) and is **incomplete** — logged as pending, non-blocking for v0.1.
- Mixing donor priv-apps into a LineageOS userspace (naive overlay) is **ruled out** — would fail privilege whitelist/signature checks.

## 7. Vendor interface (HAL) coupling — ⚠️ TOP RISK

| Area | Status |
|---|---|
| Donor system → Qualcomm HALs | Donor userspace carries Qualcomm/QTI apps (21 classified INCOMPATIBLE) and references oPlus/Qualcomm services absent from Tensor vendor |
| Tensor vendor (LineageOS) | Exynos GS101 HALs (aoc, cpif, bcmdhd4389, clk_exynos_gs — 323 modules verified in vendor_dlkm) |
| Telephony/IMS | **Highest boot-critical risk**: donor RIL stack expects qcril HALs; raven exposes Shannon RIL via standard IRadio AIDL — may bind, may crash-loop |
| VINTF | Donor framework compatibility matrix may require oPlus vendor HALs — if mandatory, boot fails at `vintf` check; if optional, degraded features only |

Verdict: v0.1 expected outcomes range from "boots with broken IMS/telephony +
crash-looping oPlus services" to "bootloop". This uncertainty is the reason the
build exists — it is the cheapest possible experiment that yields ground truth.

## 8. GCam (Pixel Camera) split package — ✅ COMPATIBLE (static), function pending

- Bundle: `com.google.android.GoogleCamera` v11.1.040 (versionCode 69703284), **minSdk 37 / targetSdk 37**, arm64-v8a only
- 31 splits complete (base + feature + asset modules incl. per-device variants kodiak/grizzly/yogi/cubs) — nothing discarded
- raven-specific camera asset split **not present** in this bundle (device variants target newer Pixels) → app should install & run with generic config; true camera functionality can only be verified on-device (owner-gated, after first boot)
- Included as `extras/gcam/splits/` + `adb install-multiple` instructions; **not auto-installed** (vanilla policy)

## 9. Tooling constraints discovered (affect v0.2+)

- No root on build host; `debugfs rdump` drops SELinux xattrs + uid/gid → **ext4 repack is not viable** on this host
- `mkfs.erofs 1.8.6` supports `--file-contexts` (SELinux) — the chosen v0.2 repack path; uid/gid handling to be confirmed (`--force-uid/gid` options) before repack
- Web search provider down all session — compatibility claims above are first-party evidence only

## Overall verdict

**v0.1 (as-assembled): GO for a controlled, reversible experiment.**
Boot-critical unknowns (telephony HAL binding, VINTF strictness) cannot be
resolved without booting real hardware. Rollback is clean: re-flash the
LineageOS nightly; no wipe commands exist anywhere in the flash tooling.
