#!/usr/bin/env python3
"""Assemble a LineageOS-recovery-compatible A/B OTA sideload zip.

The zip is hand-rolled (STORED entries only) so every byte offset is exact:
  META-INF/com/android/metadata  (first entry, offset 0)
  payload.bin                    (3.04 GB, streamed, CRC32 computed on the fly)
  payload_properties.txt
"""
import sys, os, struct, time, zlib

DOS_TIME = lambda t: ((t.tm_hour << 11) | (t.tm_min << 5) | (t.tm_sec // 2))
DOS_DATE = lambda t: (((t.tm_year - 1980) << 9) | (t.tm_mon << 5) | t.tm_mday)

def main(out_zip, payload_bin, props_txt, fingerprint, incremental, spl, sdk):
    payload_size = os.path.getsize(payload_bin)
    with open(props_txt, "rb") as f:
        props_data = f.read()
    props_size = len(props_data)
    ts = int(time.time())
    tt = time.gmtime(ts)

    guess = 600
    while True:  # converge metadata length ↔ offsets
        off_meta = 0
        off_payload = 30 + len("META-INF/com/android/metadata") + guess
        off_props = off_payload + 30 + len("payload.bin") + payload_size
        pf = (f"payload.bin:{off_payload}:{payload_size},"
              f"payload_properties.txt:{off_props}:{props_size},"
              f"metadata:{off_meta}:{guess}")
        meta = (f"ota-property-files={pf}\n"
                f"ota-required-cache=0\n"
                f"ota-streaming-property-files={pf}\n"
                f"ota-type=AB\n"
                f"post-build={fingerprint}\n"
                f"post-build-incremental={incremental}\n"
                f"post-sdk-level={sdk}\n"
                f"post-security-patch-level={spl}\n"
                f"post-timestamp={ts}\n"
                f"pre-device=raven\n")
        if len(meta) == guess:
            break
        guess = len(meta)
    meta_crc = zlib.crc32(meta.encode()) & 0xFFFFFFFF
    meta_dt = (DOS_TIME(tt), DOS_DATE(tt))

    entries = [  # (name, src_bytes_or_path, size, crc_or_None, dos)
        ("META-INF/com/android/metadata", meta.encode(), len(meta), meta_crc, meta_dt),
        ("payload.bin", payload_bin, payload_size, None, meta_dt),
        ("payload_properties.txt", props_data, props_size,
         zlib.crc32(props_data) & 0xFFFFFFFF, meta_dt),
    ]

    entries_crc_patch = 0
    with open(out_zip, "wb") as z:
        offsets = {}
        for name, src, size, crc, dos in entries:
            offsets[name] = z.tell()
            if crc is None:
                crc = 0  # payload: patched after streaming
            z.write(struct.pack("<IHHHHHIIIHH", 0x04034B50, 20, 0, 0,
                                dos[1], dos[0], crc, size, size,
                                len(name), 0) + name.encode())
            if isinstance(src, bytes):
                z.write(src)
            else:  # stream payload.bin, compute CRC on the fly
                c = zlib.crc32(b"")
                with open(src, "rb") as f:
                    while True:
                        chunk = f.read(1 << 24)
                        if not chunk:
                            break
                        c = zlib.crc32(chunk, c)
                        z.write(chunk)
                entries_crc_patch = c & 0xFFFFFFFF
                cur = z.tell()
                z.seek(offsets[name] + 14)
                z.write(struct.pack("<I", entries_crc_patch))
                z.seek(cur)
        # central directory
        cd_start = z.tell()
        for name, src, size, crc, dos in entries:
            if name == "payload.bin":
                crc = entries_crc_patch
            z.write(struct.pack("<IHHHHHHIIIHHHHHII", 0x02014B50, 20, 20, 0, 0,
                                dos[1], dos[0], crc, size, size,
                                len(name), 0, 0, 0, 0, 0,
                                offsets[name]) + name.encode())
        cd_size = z.tell() - cd_start
        z.write(struct.pack("<IHHHHIIH", 0x06054B50, 0, 0, len(entries), len(entries),
                            cd_size, cd_start, 0))

    with open(out_zip, "rb") as f:
        for name, off in (("payload.bin", off_payload),
                          ("payload_properties.txt", off_props),
                          ("META-INF/com/android/metadata", 0)):
            f.seek(off)
            assert f.read(4) == b"PK\x03\x04", (name, off)
    print(f"sideload zip: {out_zip}")
    print(f"  metadata    @0 ({len(meta)} B)")
    print(f"  payload.bin @{off_payload:,} ({payload_size:,} B)")
    print(f"  properties  @{off_props:,} ({props_size} B)")
    print(f"  post-timestamp={ts} — offsets verified (PK magic)")

if __name__ == "__main__":
    main(*sys.argv[1:8])
