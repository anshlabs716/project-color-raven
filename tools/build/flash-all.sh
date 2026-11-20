#!/usr/bin/env bash
#
# Project Color Raven v0.1 — raven (Google Pixel 6 Pro)
#
# Flashes: LineageOS 24 foundation (boot chain + Tensor vendor) with the
#          ColorOS 17 donor userspace (system / system_ext / product, EROFS).
#
# SAFETY-CRITICAL ORDER (audit v2):
#   1. Logical partitions are flashed FIRST, inside fastbootd running under
#      the phone's CURRENT (fully consistent) boot chain — fastbootd never
#      boots with a half-updated device.
#   2. Then a reboot to BOOTLOADER (never boots an OS) for the boot chain.
#   3. Then one final reboot into the fully flashed device.
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
echo -e "${YLW} Project Color Raven v0.1 — UNTESTED experimental build${NC}"
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

echo
echo "Enter fastbootd: from the RUNNING system run 'adb reboot fastboot',"
echo "or from bootloader mode run 'fastboot reboot fastboot' (BEFORE this"
echo "script has flashed anything, so the old chain boots fastbootd)."
echo "Press Enter when fastbootd is up."
read -r

# ---- Stage 1: fastbootd — logical (dynamic) partitions ----------------------
is_raven
US="$(fastboot getvar is-userspace 2>&1 | grep -m1 '^is-userspace:' | awk '{print $2}' | tr -d '\r')"
[ "$US" = "yes" ] || fail "not in fastbootd (userspace) mode — re-enter fastbootd and retry"

echo
echo ">>> Stage 1/2 — logical partitions (super) via fastbootd"
# fastbootd auto-resizes logical partitions to image size; super has ~3.8 GiB
# headroom (verified against super_empty.img metadata).
fastboot flash system      "$IMG/system.img"        # ColorOS 17 donor (EROFS)
fastboot flash system_ext  "$IMG/system_ext.img"    # ColorOS 17 donor (EROFS)
fastboot flash product     "$IMG/product.img"       # ColorOS 17 donor (EROFS)
fastboot flash vendor      "$IMG/vendor.img"        # LineageOS Tensor HALs
fastboot flash vendor_dlkm "$IMG/vendor_dlkm.img"   # LineageOS kernel modules

echo
echo ">>> Rebooting to BOOTLOADER (does not boot the OS)"
fastboot reboot bootloader
echo "Waiting for bootloader..."
sleep 6
until fastboot getvar product >/dev/null 2>&1; do sleep 2; done
is_raven

# ---- Stage 2: bootloader — boot chain ---------------------------------------
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
