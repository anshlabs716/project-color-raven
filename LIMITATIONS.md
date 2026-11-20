# Limitations

## Known so far (audit stage)

1. **No verified component yet.** Nothing has been extracted, built or run.
   All compatibility statuses are `UNKNOWN` until Stage 5 evidence exists.
2. **Hardware gap.** OnePlus 15 (Snapdragon, PLK110) vs Pixel 6 Pro (Tensor GS101):
   vendor HALs, camera stacks, modem/IMS, fingerprint, sensors, audio and
   display drivers are **not interchangeable**. Pixel vendor must stay.
3. **Two OTAs, not source trees.** Both inputs are flashable payload packages.
   They contain no device trees, kernel source, or build scripts. A real ROM
   build needs external repos (LineageOS raven device tree, kernel gs101,
   vendor blobs) that we do not have locally yet.
4. **Storage ceiling.** 49 GB free vs ~45 GB project budget: full AOSP builds
   are borderline; strategy favors targeted extraction over full checkouts.
5. **Chinese ROM region locks.** ColorOS 17 CN features (AI cloud, accounts,
   recommendations) may be region/account-locked; nothing confirmed working
   outside China yet — see Stage 3/5 work items.
6. **RAM.** 8 GB (+6.2 GB swap) makes parallel compilation inadvisable;
   large Java/Kotlin daemon builds will be slow.

## To be documented later
Per-component limitations (Fluid Cloud, cameras, IMS/VoLTE, AI services…) belong
in `reports/compatibility/` and get summarized here after Stage 5.
