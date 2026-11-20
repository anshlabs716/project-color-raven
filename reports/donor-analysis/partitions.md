# Partition Manifest Analysis (Stage 3/4 — parsed 2026-11-20)

Both OTA payloads parsed with the installed `payload-dumper` library
(AOSP CrAU format, `update_metadata_pb2` schema). Raw JSON:
`build/logs/base_partitions.json`, `build/logs/donor_partitions.json`.
Manifests: `build/logs/{base,donor}_manifest.pb`.

## Base — LineageOS 24 raven (21 partitions, 5.00 GB total)

Full (non-incremental) OTA. `minor_version=0`, `block_size=4096`.
Fingerprint `google/raven/raven:17/CP3A.261005.002.A1/16269273`.

| Partition | Size | Notes |
|---|---|---|
| system | 1.2 GB | Android 17 framework |
| product | 2.0 GB | apps/resources |
| system_ext | 518 MB | |
| vendor | 647 MB | **Pixel/Tensor HALs — keep** |
| vendor_dlkm | 53 MB | |
| boot | 64 MB | raven kernel |
| vendor_boot | 64 MB | |
| modem | 93 MB | Tensor modem — keep |
| dtbo | 16 MB | |
| abl / bl1 / bl2 / bl31 / gsa / ldfw / pbl / tzsw | small | Tensor bootloader chain — keep |
| pvmfw / vbmeta* | small | AVB — keep |

## Donor — ColorOS 17 PLK110 (65 partitions, 12.87 GB total)

`minor_version=9` (newer payload format), full OTA.

### Software partitions (porting interest)

| Partition | Size | Porting role |
|---|---|---|
| **system** | 1.05 GB | ColorOS framework (framework.jar, services, SystemUI) |
| **system_ext** | 934 MB | System UI / priv-apps — **highest porting value** |
| **product** | 169 MB | resources/overlays |
| **odm** | 3.0 GB | OnePlus ODM layer — mostly hardware-bound, audit needed |
| **my_stock** | 4.76 GB | OnePlus "my_*" carrier/promo partition — **debloat target** |
| **my_product** | 1.46 GB | OnePlus apps (likely preloads) — **debloat target** |
| **my_region / my_engineering / my_heytap / my_carrier / my_bigball / my_manifest** | ~8 MB | OnePlus regional/carrier config — audit for i18n |
| **vendor** | 464 MB | Qualcomm HALs — **INCOMPATIBLE with Tensor, do not use** |
| vendor_dlkm | 155 MB | Qualcomm kernel modules — incompatible |
| system_dlkm | 14 MB | audit |

### Hardware partitions — INCOMPATIBLE (Snapdragon/Qualcomm, never flash to raven)

`xbl, xbl_config, xbl_ramdump, tz, hyp, aop, uefi, uefisecapp, keymaster,
secretkeeper, qupfw, shrm, cpucp, dcp, soccp*, pdp*, devcfg, dsp, bluetooth,
modem (Qualcomm!), tme_*, multiimg*, splash, recovery, init_boot,
engineering_cdt, featenabler, spuservice, imagefv, *_ac_config, oplus_sec`

Note: donor `modem` (367 MB) is a **Qualcomm** modem image — the base raven
`modem` (93 MB, Tensor) must win. Same name, different hardware.

## Shared-name partitions (same name, different hardware — keep BASE versions)

`abl, boot, dtbo, modem, product, pvmfw, system, system_ext, vbmeta*,
vendor, vendor_boot, vendor_dlkm`

Of these, only `system`, `system_ext`, `product` are legitimate ColorOS
*content* sources. The rest must remain Pixel/LineageOS builds.

## Conclusion for Stage 5/6

- The port surface = donor `system` + `system_ext` + `product` (+ selective
  `odm`/`my_*` content), layered onto the raven base.
- No OnePlus/Qualcomm hardware partition is ever written to the device.
- `my_stock`/`my_product` (6.2 GB combined) are prime debloat/investigation
  zones per DEBLOAT_POLICY.md §A/§B.
- Full donor payload is 12.87 GB uncompressed → extract **selectively**
  (metadata first, then targeted partitions), never all at once (45 GB budget).
