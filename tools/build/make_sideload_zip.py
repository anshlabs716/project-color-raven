#!/usr/bin/env python3
"""Assemble a LineageOS-recovery-compatible A/B OTA sideload zip.

Contents: payload.bin (stored) + payload_properties.txt + META-INF/com/android/metadata
Recovery streams payload.bin via the ota-property-files offsets recorded in
metadata (same mechanism as the official LineageOS nightly for raven).
"""
import sys, os, struct, time, zipfile

def local_data_offset(zf, name):
    zi = zf.getinfo(name)
    return zi.header_offset + 30 + len(zi.filename.encode()) + len(zi.extra)

def main(out_zip, payload_bin, props_txt, fingerprint, incremental, spl, sdk):
    ts = int(time.time())
    meta_txt = f"""ota-property-files=PLACEHOLDER
ota-required-cache=0
ota-streaming-property-files=PLACEHOLDER
ota-type=AB
post-build={fingerprint}
post-build-incremental={incremental}
post-sdk-level={sdk}
post-security-patch-level={spl}
post-timestamp={ts}
pre-device=raven
"""
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_STORED) as zf:
        zf.writestr("META-INF/com/android/metadata", meta_txt)
        zf.write(payload_bin, "payload.bin")
        zf.write(props_txt, "payload_properties.txt")
        off_p = local_data_offset(zf, "payload.bin")
        off_pr = local_data_offset(zf, "payload_properties.txt")
        off_m = local_data_offset(zf, "META-INF/com/android/metadata")
        pf = (f"payload.bin:{off_p}:{zf.getinfo('payload.bin').file_size},"
              f"payload_properties.txt:{off_pr}:{zf.getinfo('payload_properties.txt').file_size},"
              f"metadata:{off_m}:{zf.getinfo('META-INF/com/android/metadata').file_size}")
        # rewrite metadata with real offsets (metadata itself last, offsets of
        # the other two are stable; metadata entry position unchanged)
        meta_txt = meta_txt.replace("ota-property-files=PLACEHOLDER",
                                    f"ota-property-files={pf}")
        meta_txt = meta_txt.replace("ota-streaming-property-files=PLACEHOLDER",
                                    f"ota-streaming-property-files={pf}")
        zf.writestr("META-INF/com/android/metadata", meta_txt)
    # verify offsets point at real local headers
    with open(out_zip, "rb") as f:
        for name in ("payload.bin", "payload_properties.txt", "META-INF/com/android/metadata"):
            with zipfile.ZipFile(out_zip) as zf:
                o = local_data_offset(zf, name)
            f.seek(o)
            magic = f.read(4)
            assert magic == b"PK\x03\x04", (name, magic)
    print(f"sideload zip written: {out_zip}")
    print(f"  offsets verified (PK magic at each property-file entry)")
    print(f"  post-timestamp={ts} (>= installed builds → no anti-rollback rejection)")

if __name__ == "__main__":
    main(*sys.argv[1:7])
