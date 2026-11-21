@echo off
REM ============================================================
REM  Project Color Raven v0.2 — raven (Google Pixel 6 Pro)
REM  v0.2 FIXES: fstab erofs (was ext4), flat system.img repack,
REM  androidboot.selinux=permissive. Script now enters fastbootd
REM  itself via "fastboot reboot fastboot".
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

echo Step 0 - locating device...
fastboot getvar product >nul 2>&1
if errorlevel 1 (
    where adb >nul 2>&1
    if errorlevel 1 (
        echo ABORT: no device on fastboot or adb - boot it to bootloader first.
        goto :eof
    )
    echo Device found on adb - rebooting to bootloader.
    adb reboot bootloader
    timeout /t 5 /nobreak >nul
)
set TRY=0
:waitfb
fastboot getvar product >nul 2>&1
if errorlevel 1 (
    set /a TRY+=1
    if !TRY! geq 30 (
        echo ABORT: no fastboot device after 60s.
        goto :eof
    )
    timeout /t 2 /nobreak >nul
    goto waitfb
)

REM ---- Step 1: enter fastbootd automatically ----
set ISUS=
for /f "tokens=2" %%A in ('fastboot getvar is-userspace 2^>^&1 ^| findstr /C:"is-userspace:"') do set ISUS=%%A
if not "!ISUS!"=="yes" (
    echo Step 1 - entering fastbootd: fastboot reboot fastboot
    fastboot reboot fastboot
    set TRY=0
    :waitfd
    set ISUS=
    for /f "tokens=2" %%A in ('fastboot getvar is-userspace 2^>^&1 ^| findstr /C:"is-userspace:"') do set ISUS=%%A
    if "!ISUS!"=="yes" goto fddone
    set /a TRY+=1
    if !TRY! geq 30 (
        echo ABORT: fastbootd did not come up after 60s.
        goto :eof
    )
    timeout /t 2 /nobreak >nul
    goto waitfd
) else (
    echo Step 1 - already in fastbootd
)
:fddone

fastboot getvar product 2>&1 | findstr /C:"product: raven" >nul
if errorlevel 1 (
    echo ABORT: device is not raven — refusing.
    goto :eof
)

echo Type FLASH-RAVEN to proceed:
set /p CONFIRM=
if not "%CONFIRM%"=="FLASH-RAVEN" (
    echo Aborted — device untouched.
    goto :eof
)

REM ---- Stage 1: fastbootd — logical partitions ----
echo Stage 1/2 - logical partitions (super) via fastbootd
fastboot flash system      %IMG%\system.img
fastboot flash system_ext  %IMG%\system_ext.img
fastboot flash product     %IMG%\product.img
fastboot flash vendor      %IMG%\vendor.img
fastboot flash vendor_dlkm %IMG%\vendor_dlkm.img

REM ---- Stage 2: bootloader — boot chain ----
echo Rebooting to BOOTLOADER (does not boot the OS)...
fastboot reboot bootloader
timeout /t 8 /nobreak >nul
set TRY=0
:waitbl
fastboot getvar product >nul 2>&1
if errorlevel 1 (
    set /a TRY+=1
    if !TRY! geq 30 (
        echo ABORT: bootloader did not come back.
        goto :eof
    )
    timeout /t 2 /nobreak >nul
    goto waitbl
)
fastboot getvar product 2>&1 | findstr /C:"product: raven" >nul
if errorlevel 1 (
    echo ABORT: device check failed in bootloader mode.
    goto :eof
)
echo Stage 2/2 - boot chain (bootloader mode)
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
