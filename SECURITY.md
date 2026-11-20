# Security

## Posture

- **SELinux:** must remain enforcing in any released build. Permissive is not
  an acceptable permanent state; any permissive experiment must be temporary,
  documented in DECISIONS.md, and reverted before release.
- **Verified Boot / AVB:** keep vbmeta chain-of-boot correct for raven.
  Do not disable verification to make components boot.
- **No security features traded for functionality:** keystore, encryption,
  app sandboxing, permission grading, privacy indicators (mic/camera/location,
  clipboard) stay intact.

## Input handling

- Original archives are treated as read-only evidence. Checksums recorded in
  `input/checksums/`. Never overwritten, never renamed.
- Extracted artifacts live under `donor/`, `base/`, `build/` — never in system paths.

## Repo hygiene

- `.gitignore` blocks firmware archives, extracted images (`*.img`, `payload.bin`),
  keystore material, and build outputs. Only scripts/docs/metadata/reports are pushed.
- No secrets (tokens, keys, passwords) are committed.

## Device safety

- No flashing, wiping, slot switching, or bootloader changes without the
  owner's explicit, per-action approval. The phone remains on Project Infinity-X
  during all investigation stages.

## Disclosure

If a vulnerability is found in a ported component (e.g., an exported ColorOS
service), it is documented in `reports/` and, where appropriate, reported
upstream rather than exploited.
