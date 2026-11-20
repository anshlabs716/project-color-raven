# Changelog

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
