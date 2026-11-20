# ColorOS 17 Debloat Policy (Section 25 — owner directive)

Status: **POLICY ADOPTED — no package removed yet.** All removals require the
owner's approval after the reports in `reports/debloat/` are presented.

## Objective

Clean, lightweight, international-friendly ColorOS 17 experience for Project
Color Raven, based on the Chinese OnePlus 15 PLK110 donor — **without**
destroying the ColorOS experience. This is NOT aggressive debloat.

## Golden rule

**Never remove a package based on its name alone.** Inspect manifest,
permissions, services, shared libraries and framework relationships first.

## A. Remove candidates — promotional software (if confirmed nonessential)

Chinese shopping apps/shortcuts, promotional shopping/game apps, preinstalled
third-party games, game/app recommendation services, promotional content feeds,
marketing apps, unwanted Chinese news/video/music apps, promotional browser
shortcuts, unwanted third-party social apps, trial/demo apps, duplicate
third-party apps.

⚠️ Do **not** remove ColorOS-native apps just because they have Chinese
branding or names.

## B. Remove candidates — unnecessary Chinese regional services

Chinese regional promo feeds, app/shopping recommendation services, advertising
SDKs, regional content-discovery, promo notification services, China-only
widgets/marketing components.

**Preserve** regional components required by: Settings, Launcher, AI, Fluid
Cloud, System UI, Notifications, Location, Camera, core Android services.
A region-specific service is not automatically useless.

## C. Remove — user-facing OTA/System Update app (final experience only)

Remove the ColorOS OTA/System Update **application** from the final install,
but preserve: update infrastructure, recovery, verified boot, partition
management, bootloader functionality, essential maintenance services.
Do not remove anything just because its name contains "update"/"OTA".

## D. Remove — duplicates (investigate first, never automatic)

Browsers, music, video players, app stores, file managers, galleries, weather,
notes, assistants. Compare functionality + dependencies; keep the best native
ColorOS implementation; never replace the owner's preferred apps automatically.

## E. KEEP — core ColorOS apps (do not debloat)

Launcher, System UI, Settings, Clock, Calculator, Gallery, File Manager,
Recorder, Weather (if compatible), Phone/Contacts/Messages components,
widgets, media, lock screen, wallpaper, theme, icon, display, animation
components. **Preserve dependencies even without a launcher icon.**

## F. KEEP — AI is a priority

Never remove: AI writing, summarisation, recording, transcription, assistant,
search, image, gallery, system services, framework libraries, permissions,
settings pages, background services.

Classify each feature: on-device / cloud-dependent / region-locked /
account-dependent / language-dependent / hardware-dependent. Document why a
feature cannot work on raven before even considering removal. Never remove a
shared service used by multiple AI features.

## G. KEEP — Fluid Cloud

Preserve all confirmed dependencies (System UI integration, framework,
notification listeners, media sessions, animations, background services,
permissions). Not removable "because it's not a standalone app".

## H. KEEP — Pixel hardware & Android foundation

Never blindly remove: Tensor services, Pixel HALs, camera, fingerprint, audio,
Bluetooth, Wi-Fi, NFC, cellular, IMS, GPS, sensor, battery, thermal, power,
keystore, biometrics, System UI deps, framework libs, permission XMLs, SELinux
policy, init services, vendor interfaces.

## I. Google services policy

Do not auto-install GApps. Do not auto-remove every Google package either.
Classify: Android platform components / Pixel-specific components / optional
Google apps / Play services deps / Google framework / location / push.
Keep the base lightweight without breaking Android or Pixel hardware.
Project rule from D7: **vanilla build, no GMS** — any optional GMS integration
must be separately documented and owner-approved.

## J. Privacy & tracking audit

Investigate: ad IDs, promo analytics, third-party tracking SDKs, unwanted
telemetry, promo notification services, unnecessary background network calls.
Classify each: advertising / analytics / diagnostics / crash reporting /
essential system telemetry / core service communication. Do not disable
essential diagnostics or security functionality without understanding
consequences.

## K. Classification system (every package gets one)

1. `KEEP` — essential/desired ColorOS functionality
2. `KEEP - DEPENDENCY` — required by another app/system service
3. `OPTIONAL` — useful, owner decides
4. `REMOVE` — confirmed unnecessary promotional/duplicate
5. `INVESTIGATE` — purpose/dependencies unclear
6. `INCOMPATIBLE` — confirmed incompatible with the raven implementation

Every `REMOVE` must record: package name, app name, APK location, purpose,
dependencies, why removal is safe, shared components, tested or not.

## L. Required reports (generated before any removal)

- `reports/debloat/package_inventory.csv`
  (package, app name, category, system/user, dependencies, classification,
  justification, testing status)
- `reports/debloat/keep_packages.md`
- `reports/debloat/remove_candidates.md`
- `reports/debloat/dependencies.md`
- `reports/debloat/removed_packages.md` (post-approval)

**No removals during the initial audit. Reports first → owner approval → apply.**

## Philosophy

Lightweight, clean, international-friendly, privacy-conscious, free of
unnecessary Chinese promotional bloat and duplicates — while fully equipped
with useful ColorOS features, compatible AI, Fluid Cloud, and reliable raven
hardware. Do not sacrifice functionality for an arbitrary package count;
a smaller ROM is not automatically a better ROM.
