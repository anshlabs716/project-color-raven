#!/usr/bin/env python3
"""Generate debloat reports from package_inventory_raw.tsv (read-only).

Outputs (per DEBLOAT_POLICY.md §L):
  reports/debloat/package_inventory.csv
  reports/debloat/keep_packages.md
  reports/debloat/remove_candidates.md
  reports/debloat/dependencies.md
Nothing is removed; classifications are proposals awaiting owner approval.
"""
import csv
import os
import re

RAW = "reports/debloat/package_inventory_raw.tsv"
OUT = "reports/debloat"

# --- rule tables ---------------------------------------------------------
# Classification constants
KEEP = "KEEP"
KEEP_DEP = "KEEP - DEPENDENCY"
OPTIONAL = "OPTIONAL"
REMOVE = "REMOVE"
INVESTIGATE = "INVESTIGATE"
INCOMPATIBLE = "INCOMPATIBLE"

# Core ColorOS/AOSP experience — never debloat (policy §E, §H)
KEEP_PATTERNS = [
    r"^com\.android\.systemui$", r"^com\.android\.settings$",
    r"^com\.android\.launcher$", r"^com\.android\.phone$",
    r"^com\.android\.server\.telecom$", r"^com\.android\.contacts",
    r"^com\.android\.providers\.contacts$", r"^com\.android\.contactspicker$",
    r"^com\.android\.providers\.calendar$", r"^com\.android\.mms",
    r"^com\.android\.providers\.telephony$", r"^com\.android\.stk$",
    r"^com\.android\.calendar$", r"^com\.android\.deskclock",
    r"^com\.android\.calculator", r"^com\.android\.gallery",
    r"^com\.android\.contacts$", r"^com\.android\.mtp$",
    r"^com\.android\.bluetooth$", r"^com\.android\.nfc$",
    r"^com\.android\.se$", r"^com\.android\.keychain$",
    r"^com\.android\.certinstaller$", r"^com\.android\.documentsui$",
    r"^com\.android\.externalstorage$", r"^com\.android\.providers\.downloads",
    r"^com\.android\.providers\.settings$", r"^com\.android\.settings\.intelligence$",
    r"^com\.android\.storagemanager$", r"^com\.android\.shell$",
    r"^com\.android\.networkstack$", r"^com\.android\.carrierconfig$",
    r"^com\.android\.cellbroadcast", r"^com\.android\.ons$",
    r"^com\.android\.simappdialog$", r"^com\.android\.vpndialogs$",
    r"^com\.android\.managedprovisioning$", r"^com\.android\.dynsystem$",
    r"^com\.android\.credentialmanager$", r"^com\.android\.companiondevicemanager$",
    r"^com\.android\.packageinstaller$", r"^com\.android\.permissioncontroller$",
    r"^com\.android\.localtransport$", r"^com\.android\.backupconfirm$",
    r"^com\.android\.sharedstoragebackup$", r"^com\.android\.proxyhandler$",
    r"^com\.android\.inputdevices$", r"^com\.android\.location\.fused$",
    r"^com\.android\.printspooler$", r"^com\.android\.bips$",
    r"^com\.android\.providers\.blockednumber$", r"^com\.android\.calllogbackup$",
    r"^com\.android\.htmlviewer$", r"^com\.android\.egg$",
    r"^com\.android\.dreams", r"^com\.android\.traceur$",
    r"^com\.android\.wallpaperbackup$", r"^com\.android\.musicfx$",
    r"^com\.android\.bookmarkprovider$", r"^com\.android\.captivelogin$",
    r"^com\.android\.captiveportallogin$", r"^com\.android\.carrierdefaultapp$",
    r"^com\.android\.cameraextensions$", r"^com\.android\.secureelement$",
    r"^com\.android\.pacprocessor$", r"^com\.android\.extensionservice$",
    r"^com\.android\.bluetoothmidiservice$", r"^com\.android\.mtp$",
    r"^com\.android\.DeviceAsWebcam$", r"^com\.android\.eydropper$",
    r"^com\.android\.eyedropper$", r"^com\.android\.privatespace$",
    r"^com\.android\.managedprovisioning$", r"^com\.android\.dynsystem$",
    r"^com\.android\.providers\.userdictionary$", r"^com\.android\.apps\.tag$",
    r"^com\.android\.intentsresolver$", r"^com\.android\.server\.telecom$",
    # ColorOS core experience (policy §E)
    r"^com\.oplus\.keyguard\.", r"^com\.oplus\.systemui",
    r"^com\.oplus\.gesture$", r"^com\.oplus\.blur$", r"^com\.oplus\.eyeprotect$",
    r"^com\.oplus\.battery$", r"^com\.oplus\.safecenter$",
    r"^com\.oplus\.notificationmanager$", r"^com\.oplus\.multiapp$",
    r"^com\.oplus\.appplatform$", r"^com\.oplus\.exsystemservice$",
    r"^com\.oplus\.uxdesign$", r"^com\.oplus\.qualityprotect$",
    r"^com\.oplus\.securitypermission$", r"^com\.oplus\.credential$",
    r"^com\.oplus\.location$", r"^com\.oplus\.healthservice$",
    r"^com\.oplus\.wirelesssettings$", r"^com\.oplus\.appbooster$",
    r"^com\.oplus\.lfeh$", r"^com\.oplus\.olc$", r"^com\.oplus\.athena$",
    r"^com\.oplus\.dfs$", r"^com\.oplus\.vdc$", r"^com\.oplus\.plugin$",
    r"^com\.oplus\.subsys$", r"^com\.oplus\.onetrace$",
    r"^oplus$", r"^com\.android\.launcher$",
    # AOSP foundation / Pixel-critical (policy §H)
    r"^android$", r"^com\.android\.modulemetadata$",
    r"^com\.android\.security\.fsverity", r"^com\.android\.role\.notes",
    r"^vendor\.qti\.frameworks\.utils$", r"^com\.android\.oemextensions$",
    r"^com\.android\.systemui\.accessibility",
]

# Qualcomm/Tensor hardware-bound — INCOMPATIBLE with raven vendor (policy §H:
# keep BASE equivalents; donor versions must not be used)
QCOM_PATTERNS = [
    r"^com\.qualcomm\.", r"^com\.qti\.", r"^org\.codeaurora\.",
    r"^vendor\.qti\.", r"^com\.qualcomm\.location$",
    r"^com\.qualcomm\.qti\.telephonyservice$",
    r"^com\.qualcomm\.qcrilmsgtunnel$",
    r"^com\.qualcomm\.wfd\.service$", r"^com\.qualcomm\.qti\.xrvd",
    r"^com\.qualcomm\.qti\.xrcb", r"^com\.qualcomm\.atfwd$",
    r"^com\.qualcomm\.qti\.workloadclassifier$",
    r"^com\.qualcomm\.qti\.powersavemode$",
    r"^com\.qualcomm\.uimremote", r"^com\.qti\.dcf$",
    r"^com\.qti\.dpmserviceapp$", r"^com\.qti\.qcc$",
    r"^com\.android\.bluetooth\.oplus\.overlay$",
    r"^com\.wapi\.wapicertmanage$",  # China WAPI cert service
]

# User-facing OTA / upgrade app — REMOVE per policy §C (app only!)
OTA_PATTERNS = [
    r"^com\.oplus\.ota$", r"^com\.oplus\.upgradeguide$",
    r"^com\.android\.systemui\.update$",
]

# Engineering / factory / debug modes — REMOVE candidates (policy §A:
# demo/trial; but flagged for dependency check first)
ENGINEER_PATTERNS = [
    r"^com\.oplus\.engineermode$", r"^com\.oplus\.engineercamera$",
    r"^com\.oplus\.engineernetwork$", r"^com\.oplus\.logtrial$",
    r"^com\.oplus\.nfcengineertest$", r"^com\.oplus\.bttestmode$",
    r"^com\.oplus\.commercialengineer",
]

# Region-locked / China-only services — INVESTIGATE (policy §B: do not assume
# useless; classify after dependency/manifest review)
CHINA_PATTERNS = [
    r"^com\.oplus\.beidouservice$", r"^com\.oplus\.ttsatellite$",
    r"^com\.oplus\.rsmcsatellite$", r"^vendor\.qti\.data\.ntnsatapp$",
    r"^com\.oplus\.nas\.", r"^com\.oplus\.voice\.crs$",
    r"^com\.oplus\.eid$", r"^com\.oplus\.credential\.cn$",
    r"^com\.oplus\.atlas$", r"^com\.oplus\.sau", r"^com\.oplus\.postmanservice$",
    r"^com\.oplus\.owkservice$", r"^com\.oplus\.dcs",
    r"^com\.tencent\.soter\.soterserver$",  # WeChat Pay biometric backend
]

# AI / Fluid Cloud / media — KEEP per policy §F/§G
AI_PATTERNS = [
    r"^com\.oplus\.deepthinker$", r"^com\.oplus\.pscanvas$",
    r"^com\.oplus\.appsense$", r"^com\.oplus\.sense\.",
    r"^com\.oplus\.networksense$", r"^com\.oplus\.nwestimate$",
    r"^com\.oplus\.cell\.", r"^com\.oplus\.cellularqoe$",
    r"^com\.oplus\.tai\.", r"^com\.oplus\.motionsense$",
    r"^com\.oplus\.appsearch", r"^com\.android\.appsearch\.aiseal",
]


def classify(pkg: str) -> tuple[str, str]:
    """Return (classification, justification)."""
    for pat in OTA_PATTERNS:
        if re.match(pat, pkg):
            return REMOVE, ("User-facing ColorOS OTA/upgrade app; removed per policy §C "
                            "(update infra/recovery/AVB preserved separately)")
    for pat in QCOM_PATTERNS:
        if re.match(pat, pkg):
            return INCOMPATIBLE, ("Qualcomm/SoC-specific; raven uses Tensor vendor — "
                                  "base (LineageOS) equivalent must be used instead")
    for pat in ENGINEER_PATTERNS:
        if re.match(pat, pkg):
            return INVESTIGATE, ("Engineering/factory/trial mode — candidate for removal "
                                 "per policy §A; verify no system dependency first")
    for pat in CHINA_PATTERNS:
        if re.match(pat, pkg):
            return INVESTIGATE, ("Region-specific (CN) service — verify dependency on "
                                 "Settings/Launcher/AI/FluidCloud before any removal (§B)")
    for pat in AI_PATTERNS:
        if re.match(pat, pkg):
            return KEEP, "AI/Fluid Cloud/network-sense component — priority per policy §F/§G"
    for pat in KEEP_PATTERNS:
        if re.match(pat, pkg):
            return KEEP, "Core ColorOS/Android foundation (policy §E/§H)"
    # overlays and resource packages are dependency-ish
    if ".overlay" in pkg or pkg.endswith(".rro") or "auto_generated" in pkg:
        return KEEP_DEP, "Resource overlay — required by target component"
    if pkg.startswith("com.android.providers.") or pkg.startswith("com.android.server."):
        return KEEP_DEP, "Content provider / system server component"
    return INVESTIGATE, "Purpose/dependencies unclear — manual manifest review required"


def category(pkg: str, path: str) -> str:
    p = path.lower()
    if "/overlay" in p:
        return "overlay"
    if "/priv-app" in p:
        return "priv-app"
    if "/app/" in p:
        return "app"
    if "/framework" in p:
        return "framework-res"
    return "other"


def main():
    rows = []
    with open(RAW) as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 7:
                parts += [""] * (7 - len(parts))
            pkg, label, ver, sdk, perms, suid, path = parts
            cls, just = classify(pkg)
            rows.append({
                "package": pkg,
                "app_name": label or "(label not resolved — aapt fallback needed)",
                "category": category(pkg, path),
                "type": "system" if path.startswith(("system/", "system_ext/")) else
                        ("product" if path.startswith("product/") else "system"),
                "dependencies": "see dependencies.md" if cls in (KEEP_DEP, INVESTIGATE) else "",
                "classification": cls,
                "justification": just,
                "testing_status": "NOT TESTED",
                "path": path,
            })

    os.makedirs(OUT, exist_ok=True)

    # CSV (required schema)
    with open(f"{OUT}/package_inventory.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "package", "app_name", "category", "type", "dependencies",
            "classification", "justification", "testing_status", "path"])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # summary
    counts = {}
    for r in rows:
        counts[r["classification"]] = counts.get(r["classification"], 0) + 1

    def write_md(name, title, pred, note):
        sel = [r for r in rows if pred(r)]
        with open(f"{OUT}/{name}", "w") as f:
            f.write(f"# {title}\n\n{note}\n\n")
            f.write(f"Total: **{len(sel)}** packages\n\n")
            f.write("| Package | Class | Location | Justification |\n")
            f.write("|---|---|---|---|\n")
            for r in sorted(sel, key=lambda x: x["package"]):
                f.write(f"| `{r['package']}` | {r['classification']} | `{r['path']}` | {r['justification']} |\n")

    write_md("keep_packages.md", "KEEP Packages (proposed — not applied)",
             lambda r: r["classification"] in (KEEP, KEEP_DEP, OPTIONAL),
             "Core ColorOS + Android foundation + AI/Fluid Cloud components. "
             "**No package has been removed.** Awaiting owner approval.")
    write_md("remove_candidates.md", "REMOVE Candidates (proposed — NOT applied)",
             lambda r: r["classification"] == REMOVE,
             "Confirmed-safe removals per policy §C (user-facing OTA app only so far). "
             "**Nothing has been removed.** Owner approval required before applying.")
    write_md("dependencies.md", "Dependencies & INVESTIGATE / INCOMPATIBLE",
             lambda r: r["classification"] in (INVESTIGATE, INCOMPATIBLE),
             "Packages needing manual manifest/dependency review, plus "
             "Qualcomm-bound packages replaced by base equivalents.")

    print("Classification summary:")
    for k in (KEEP, KEEP_DEP, OPTIONAL, REMOVE, INVESTIGATE, INCOMPATIBLE):
        print(f"  {k:<20} {counts.get(k, 0)}")
    print(f"CSV rows: {len(rows)}")


if __name__ == "__main__":
    main()
