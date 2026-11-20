# Input files

Originals live in `/home/ansh/` (outside the repo, never moved or modified).

| Path | Size (bytes) | Role |
|---|---|---|
| `/home/ansh/oneplus 15 color os 17.zip` | 9,584,856,425 | **Donor** — ColorOS 17 CN `PLK110_17.0.1.201(CN01)` |
| `/home/ansh/lineage-24.0-20261116-nightly-raven-signed.zip` | 1,442,551,820 | **Base** — LineageOS 24 raven A/B OTA, Android 17 |
| `/home/ansh/boot.img` | 67,108,864 | Loose image — identity to verify (Stage 2/4) |
| `/home/ansh/vendor_boot.img` | 67,108,864 | Loose image — identity to verify |
| `/home/ansh/dtbo.img` | 16,777,216 | Loose image — identity to verify |
| `/home/ansh/vbmeta.img` | 8,192 | Loose image — identity to verify |
| `/home/ansh/super_empty.img` | 5,080 | Empty super partition metadata template |
| `/home/ansh/fwmanifest.xml` | 605,218 | **Mislabeled**: actually a framework `AndroidManifest.xml` dump |

Not project input: `/home/ansh/firmware/` (unrelated PlatformIO project).

## Integrity

See `checksums/` for recorded SHA-256 values (donor inner ZIP verified against
the `FWAtlas.com.txt` manifest shipped inside the package).
