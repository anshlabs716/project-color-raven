# Loose Image Identification (Stage 2 — completed 2026-11-20)

Files in `/home/ansh/`:

| File | Size | Identification | Evidence |
|---|---|---|---|
| `boot.img` | 67,108,864 B | **LineageOS 24 raven boot** (v4 header, GKI kernel 16.6 MB, no ramdisk) | size == payload `boot` (67,108,864); header v4 via `unpack_bootimg` |
| `vendor_boot.img` | 67,108,864 B | **LineageOS 24 raven vendor_boot** | size == payload `vendor_boot`; magic `VNDRBOOT` v4, contains `fips` |
| `dtbo.img` | 16,777,216 B | **LineageOS 24 raven dtbo** | size == payload `dtbo` |
| `vbmeta.img` | 8,192 B | **LineageOS 24 raven vbmeta — VERIFIED by hash** | SHA-256 of loose file == SHA-256 of vbmeta extracted from the LineageOS payload: `dfbe54841574f2826e38289a79668f13f6641fd8747e7f71f9feb906a5328277` |
| `super_empty.img` | 5,080 B | LP (logical partition) metadata template — `gDla` magic, empty super layout | magic + structure |

## vbmeta details (avbtool info_image)

- Algorithm SHA256_RSA4096, release `avbtool 1.4.0`
- **Rollback Index 1793491200 = 2026-11-01** — matches base security patch level
- Flags: 3 (verification-disabled flags as shipped for custom flashing)
- Chain descriptors: `boot`, `vbmeta_system` (key sha1 `cdbb7717…` = LineageOS key)

## Conclusion

The loose images are **the same LineageOS 24 raven build** as the supplied ZIP
(not Pixel factory images, not donor images). They are effectively duplicates
of payload content — use the payload as the source of truth; keep loose files
untouched as reference. `fwmanifest.xml` remains a mislabeled framework
AndroidManifest dump (see `input/README.md`).
