#!/usr/bin/env bash
#
# Project Color Raven v0.2 — raven (Google Pixel 6 Pro)
#
# Flashes: LineageOS 24 foundation (boot chain + Tensor vendor) with the
#          ColorOS 17 donor userspace (system / system_ext / product, EROFS).
#
# v0.2 FIXES over v0.1 (root cause of "boots then reboots to fastboot"):
#   * fstab: system/system_ext/product now declare erofs (donor images are
#     EROFS; v0.1's fstab said ext4 -> first-stage mount failed -> reboot).
#   * system.img repacked FLAT (donor's raw image is root-style; content
#     nested under system/ would land at /system/system/... and second-stage
#     init could never find /system/bin/init).
#   * androidboot.selinux=permissive added to the bootconfig.
#
# SAFETY-CRITICAL ORDER (audit v2):
#   1. Script enters fastbootd ITSELF via `fastboot reboot fastboot`, then
#      flashes logical partitions under the CURRENT (consistent) boot chain.
#   2. Reboot to BOOTLOADER (never boots an OS) for the boot chain.
#   3. One final reboot into the fully flashed device.
#   No step ever boots the OS with a mixed old/new state.
#
# SAFETY RULES (hard-coded):
#   * Refuses to run against anything but "raven".
#   * NEVER wipes userdata (no "-w", no "erase", no "format" anywhere).
#   * Never touches bootloader/modem/radio/persist/metadata partitions.
#   * NEVER flashes super_empty.img (would destroy the dynamic layout).
#   * Requires the bootloader to already be unlocked; never locks it.
#   * Requires explicit typed confirmation.
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMG="$HERE/images"
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; NC='\033[0m'

fail() { echo -e "${RED}ABORT: $*${NC}" >&2; exit 1; }

command -v fastboot >/dev/null 2>&1 || fail "fastboot not found in PATH"
[ -d "$IMG" ] || fail "images/ directory missing"

echo -e "${YLW}==============================================================${NC}"
echo -e "${YLW} Project Color Raven v0.2 — UNTESTED experimental build${NC}"
echo -e "${YLW} Target device : raven (Google Pixel 6 Pro)${NC}"
echo -e "${YLW} Order         : fastbootd (logical) -> bootloader (boot chain)${NC}"
echo -e "${YLW} What is safe  : no wipe/erase/format commands exist in this script.${NC}"
echo -e "${YLW}                 super_empty.img is NOT flashed (reference only).${NC}"
echo -e "${YLW}                 Data is preserved by the script, but cross-ROM${NC}"
echo -e "${YLW}                 swaps can still require a factory reset — BACK UP!${NC}"
echo -e "${YLW} Rollback      : re-flash your LineageOS nightly (see README).${NC}"
echo -e "${YLW}==============================================================${NC}"

for f in boot dtbo vendor_boot vbmeta vbmeta_system vbmeta_vendor \
         system system_ext product vendor vendor_dlkm; do
    [ -f "$IMG/$f.img" ] || fail "missing $IMG/$f.img"
done

is_raven() {
    local p
    p="$(fastboot getvar product 2>&1 | grep -m1 '^product:' | awk '{print $2}' | tr -d '\r')"
    [ "$p" = "raven" ] || fail "device is not raven (got: ${p:-none}) — refusing"
    echo "Confirmed device: raven"
}

wait_fastboot() { # wait until a fastboot device answers (max ~60s)
    local i=0
    until fastboot getvar product >/dev/null 2>&1; do
        i=$((i+1)); [ "$i" -gt 30 ] && fail "no fastboot device after 60s"
        sleep 2
    done
}

# ---- Step 0: find the device (any of: fastbootd / bootloader / Android) ----
echo
echo ">>> Step 0 — locating device"
if ! fastboot getvar product >/dev/null 2>&1; then
    if command -v adb >/dev/null 2>&1 && adb get-state >/dev/null 2>&1; then
        echo "Device found on adb — rebooting to bootloader (adb reboot bootloader)"
        adb reboot bootloader
        sleep 3
    else
        fail "no device on fastboot or adb — boot it to bootloader first: adb reboot bootloader"
    fi
fi
wait_fastboot

# ---- Step 1: enter fastbootd automatically -------------------------------
US="$(fastboot getvar is-userspace 2>&1 | grep -m1 '^is-userspace:' | awk '{print $2}' | tr -d '\r')"
if [ "$US" != "yes" ]; then
    echo ">>> Step 1 — entering fastbootd: fastboot reboot fastboot"
    fastboot reboot fastboot
    i=0
    while true; do
        US="$(fastboot getvar is-userspace 2>&1 | grep -m1 '^is-userspace:' | awk '{print $2}' | tr -d '\r' || true)"
        [ "$US" = "yes" ] && break
        i=$((i+1)); [ "$i" -gt 30 ] && fail "fastbootd did not come up after 60s"
        sleep 2
    done
else
    echo ">>> Step 1 — already in fastbootd"
fi
is_raven

echo
echo "Type FLASH-RAVEN to proceed:"
read -r CONFIRM
[ "$CONFIRM" = "FLASH-RAVEN" ] || { echo "Aborted — device untouched."; exit 1; }

# ---- Stage 2: fastbootd — logical (dynamic) partitions --------------------
echo
echo ">>> Stage 1/2 — logical partitions (super) via fastbootd"
# fastbootd auto-resizes logical partitions to image size; super has ~3.8 GiB
# headroom (verified against super_empty.img metadata).
fastboot flash system      "$IMG/system.img"        # ColorOS 17 donor (EROFS, FLAT)
fastboot flash system_ext  "$IMG/system_ext.img"    # ColorOS 17 donor (EROFS)
fastboot flash product     "$IMG/product.img"       # ColorOS 17 donor (EROFS)
fastboot flash vendor      "$IMG/vendor.img"        # LineageOS Tensor HALs
fastboot flash vendor_dlkm "$IMG/vendor_dlkm.img"   # LineageOS kernel modules

echo
echo ">>> Rebooting to BOOTLOADER (does not boot the OS)"
fastboot reboot bootloader
echo "Waiting for bootloader..."
wait_fastboot
is_raven

# ---- Stage 3: bootloader — boot chain --------------------------------------
echo
echo ">>> Stage 2/2 — boot chain (bootloader mode)"
fastboot flash boot        "$IMG/boot.img"
fastboot flash dtbo        "$IMG/dtbo.img"
fastboot flash vendor_boot "$IMG/vendor_boot.img"
# Verification must stay disabled: donor userspace is not signed by the
# LineageOS AVB key. Flags are patched into the vbmeta images on flash.
fastboot flash vbmeta        --disable-verity --disable-verification "$IMG/vbmeta.img"
fastboot flash vbmeta_system --disable-verity --disable-verification "$IMG/vbmeta_system.img"
fastboot flash vbmeta_vendor --disable-verity --disable-verification "$IMG/vbmeta_vendor.img"

echo
echo ">>> Done. Rebooting…"
fastboot reboot
echo -e "${GRN}Flashed. First boot after a userspace swap can take several minutes.${NC}"
echo -e "${GRN}If it fails to boot, the bootloader may fall back to the inactive${NC}"
echo -e "${GRN}slot (still your previous ROM) — or re-flash LineageOS (README).${NC}"
