# Decisions

## D1 — Read-only audit first; no phone commands (2026-11-20)
Owner policy: the Pixel 6 Pro stays on Project Infinity-X during investigation.
All early stages operate on local files only. fastboot/adb device commands are
forbidden until the owner explicitly approves a specific action.

## D2 — Donor inner ZIP read in place, not extracted (2026-11-20)
The donor's real firmware is a stored (uncompressed) inner ZIP inside the
9.58 GB outer ZIP. Python can address it by file offset, so listing and reading
its contents needs **zero extra disk space**. Rationale: 49 GB free disk; naive
extraction would burn ~9.6 GB for nothing. Originals stay untouched.

## D3 — Payload manifests parsed before any image extraction (2026-11-20)
Both ROMs ship `payload.bin`, not loose images. Parsing the DeltaArchiveManifest
first tells us partition lists and sizes so we extract only what analysis needs.
Rationale: avoid multi-GB blind extraction.

## D4 — No full source tree download yet (2026-11-20)
An AOSP/LineageOS checkout + build needs far more than the available 49 GB and
would stress 8 GB RAM. Strategy: analyze payloads/images first, define the
minimal repo set, then propose a concrete storage plan to the owner before any
`repo init`/`repo sync`.

## D5 — `/home/ansh/firmware/` is not project input (2026-11-20)
Inspection showed it is an unrelated PlatformIO firmware project (boards/pcbs/
platformio.ini), not Pixel firmware. Recorded so nobody mistakes it for input.

## D6 — `fwmanifest.xml` is mislabeled (2026-11-20)
Despite the name, it is a framework `AndroidManifest.xml` dump (protected
broadcasts etc.), not a firmware manifest. Kept as reference material only.
