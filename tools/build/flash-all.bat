@echo off
REM ============================================================
REM  Project Color Raven v0.1 — raven (Google Pixel 6 Pro)
REM  SAFETY: no wipe/erase/format commands exist in this script.
REM  super_empty.img is NOT flashed (reference only).
REM  Requires unlocked bootloader. Never re-lock the bootloader.
REM  ORDER: fastbootd (logical) FIRST, then bootloader (boot chain).
REM ============================================================
setlocal enabledelayedexpansion
set IMG=%~dp0images

for %%F in (boot dtbo vendor_boot vbmeta vbmeta_system vbmeta_vendor system system_ext product vendor vendor_dlkm) do (
    if not exist "%IMG%\%%F.img" (
        echo ABORT: missing %IMG%\%%F.img
        goto :eof
    )
)

echo Enter fastbootd (from running system: adb reboot fastboot,
echo or from bootloader: fastboot reboot fastboot), then press any key.
pause
fastboot getvar product 2>&1 | findstr /C:"product: raven" >nul
if errorlevel 1 (
    echo ABORT: device is not raven — refusing.
    goto :eof
)
fastboot getvar is-userspace 2>&1 | findstr /C:"is-userspace: yes" >nul
if errorlevel 1 (
    echo ABORT: not in fastbootd mode — re-enter fastbootd and retry.
    goto :eof
)

echo Type FLASH-RAVEN to proceed:
set /p CONFIRM=
if not "%CONFIRM%"=="FLASH-RAVEN" (
    echo Aborted — device untouched.
    goto :eof
)

REM ---- Stage 1: fastbootd — logical partitions ----
fastboot flash system      %IMG%\system.img
fastboot flash system_ext  %IMG%\system_ext.img
fastboot flash product     %IMG%\product.img
fastboot flash vendor      %IMG%\vendor.img
fastboot flash vendor_dlkm %IMG%\vendor_dlkm.img

REM ---- Stage 2: bootloader — boot chain ----
fastboot reboot bootloader
timeout /t 8 /nobreak >nul
fastboot getvar product 2>&1 | findstr /C:"product: raven" >nul
if errorlevel 1 (
    echo ABORT: device check failed in bootloader mode.
    goto :eof
)
fastboot flash boot        %IMG%\boot.img
fastboot flash dtbo        %IMG%\dtbo.img
fastboot flash vendor_boot %IMG%\vendor_boot.img
fastboot flash vbmeta        --disable-verity --disable-verification %IMG%\vbmeta.img
fastboot flash vbmeta_system --disable-verity --disable-verification %IMG%\vbmeta_system.img
fastboot flash vbmeta_vendor --disable-verity --disable-verification %IMG%\vbmeta_vendor.img

fastboot reboot
echo Flashed. First boot can take several minutes.
echo If it fails: the bootloader may fall back to the inactive slot (your
echo previous ROM), or re-flash your LineageOS nightly to roll back.
