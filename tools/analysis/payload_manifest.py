#!/usr/bin/env python3
"""Read OTA payload.bin metadata (DeltaArchiveManifest) without extracting images.

Usage:
  payload_manifest.py <file> [offset]

Where <file> is a zip containing payload.bin (zip offset auto-detected),
or a raw payload.bin file with optional byte offset.

Prints partition names, operation types/counts, and uncompressed sizes.
Writes the raw manifest protobuf next to this script's caller cwd as
<prefix>_manifest.pb when PCR_WRITE_PB=1.
"""
import io
import os
import struct
import sys
import zipfile

# ---------------------------------------------------------------------------
# Minimal generic protobuf wire decoder (no .proto file required).
# ---------------------------------------------------------------------------


def _read_varint(buf, pos):
    shift = 0
    result = 0
    while True:
        b = buf[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            return result, pos
        shift += 7


def parse_fields(buf, start=0, end=None):
    """Yield (field_number, wire_type, value, next_pos).

    wire_type: 0=varint, 1=fixed64, 2=length-delimited, 5=fixed32.
    For wire_type 2, value is (sub_start, sub_end) into buf.
    """
    if end is None:
        end = len(buf)
    pos = start
    while pos < end:
        key, pos = _read_varint(buf, pos)
        field = key >> 3
        wtype = key & 7
        if wtype == 0:
            val, pos = _read_varint(buf, pos)
        elif wtype == 1:
            val = buf[pos:pos + 8]
            pos += 8
        elif wtype == 2:
            ln, pos = _read_varint(buf, pos)
            val = (pos, pos + ln)
            pos += ln
        elif wtype == 5:
            val = buf[pos:pos + 4]
            pos += 4
        else:
            raise ValueError(f"unsupported wire type {wtype} at field {field}")
        yield field, wtype, val, pos


OP_NAMES = {
    0: "REPLACE", 1: "REPLACE_BZ", 2: "MOVE", 3: "BSDIFF",
    4: "SOURCE_COPY", 5: "SOURCE_BSDIFF", 6: "REPLACE_XZ",
    7: "ZERO", 8: "DISCARD", 9: "BROTLI_BSDIFF", 10: "PUFFDIFF",
    11: "ZUCCHINI", 12: "LZ4DIFF_BSDIFF", 13: "LZ4DIFF_PUFFDIFF",
}


def describe(buf, start, end, indent=0):
    pad = "  " * indent
    for field, wtype, val, _ in parse_fields(buf, start, end):
        if field == 1 and wtype == 2:  # PartitionUpdate
            describe_partition(buf, val[0], val[1], indent)
        elif field in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12):
            pass  # skip manifest-level metadata for brevity


def describe_partition(buf, start, end, indent):
    pad = "  " * indent
    name = "?"
    postinstall = False
    ops = []
    total_uncompressed = 0
    total_data = 0
    run_postinstall = False
    for field, wtype, val, _ in parse_fields(buf, start, end):
        if field == 1 and wtype == 2:  # partition_name
            name = bytes(buf[val[0]:val[1]]).decode("utf-8", "replace")
        elif field == 2 and wtype == 2:  # run_postinstall
            pass
        elif field in (3, 4) and wtype == 2:  # install_operations / merge_operations
            for f2, w2, v2, _ in parse_fields(buf, val[0], val[1]):
                if f2 == 1 and w2 == 2:  # InstallOperation
                    op_type = 0
                    data_len = 0
                    dst_len = 0
                    for f3, w3, v3, _ in parse_fields(buf, v2[0], v2[1]):
                        if f3 == 1 and w3 == 0:
                            op_type = v3
                        elif f3 == 3 and w3 == 2:  # data (extent data)
                            data_len += v3[1] - v3[0]
                        elif f3 == 5 and w2 == 2:  # dst_extents count via extents
                            pass
                    ops.append((op_type, data_len))
                    total_data += data_len
        elif field == 5 and wtype == 2:  # postinstall_path
            run_postinstall = True
    # second pass for dst sizes (extents field 4 in InstallOperation handled loosely)
    print(f"{pad}partition: {name}  ops={len(ops)}  data_bytes={total_data}")
    summary = {}
    for op_type, dlen in ops:
        key = OP_NAMES.get(op_type, str(op_type))
        summary[key] = summary.get(key, 0) + 1
    print(f"{pad}  op types: {summary}")


def read_payload_manifest(path, offset=0, zip_name=None):
    f = open(path, "rb")
    if zip_name:
        with zipfile.ZipFile(path) as z:
            info = z.getinfo(zip_name)
            with z.open(info) as zf:
                header = zf.read(4)
                meta_size = struct.unpack("<I", header)[0]
                manifest = zf.read(meta_size)
                return manifest
    f.seek(offset)
    header = f.read(4)
    meta_size = struct.unpack("<I", header)[0]
    manifest = f.read(meta_size)
    f.close()
    return manifest


def main():
    path = sys.argv[1]
    offset = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    zip_name = None
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            if "payload.bin" in z.namelist():
                zip_name = "payload.bin"
            else:
                # nested: find any zip with payload.bin? assume first entry is inner zip
                first = z.namelist()[0]
                print(f"NOTE: no payload.bin at top level; entries: {z.namelist()}")
                sys.exit(2)
    manifest = read_payload_manifest(path, offset, zip_name)
    print(f"manifest bytes: {len(manifest)}")
    out = os.environ.get("PCR_MANIFEST_OUT")
    if out:
        with open(out, "wb") as o:
            o.write(manifest)
        print(f"wrote {out}")
    describe(manifest, 0, len(manifest))


if __name__ == "__main__":
    main()
