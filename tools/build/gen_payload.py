#!/usr/bin/env python3
"""Generate an unsigned full A/B OTA payload.bin (CrAU v2) + properties.

Partitions are written as uncompressed REPLACE ops (64 MiB chunks) covering
each partition linearly. Uses the payload_dumper protobuf definitions and is
self-tested with payload_dumper's own parser (round-trip hash verification).

Usage: gen_payload.py <out_dir>
"""
import sys, os, struct, hashlib, base64, time

sys.path.insert(0, "/home/ansh/.local/share/pipx/venvs/android-payload-dumper/lib/python3.13/site-packages")
from payload_dumper import update_metadata_pb2 as um
from payload_dumper.source import FileSource
from payload_dumper.core import parse_payload, validate_operations, extract_partition_to_stream

BLOCK = 4096
CHUNK = 64 * 1024 * 1024
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PARTS = [
    ("boot",          f"{ROOT}/base/partitions/boot.img",        ""),
    ("dtbo",          f"{ROOT}/base/partitions/dtbo.img",        ""),
    ("vendor_boot",   f"{ROOT}/base/partitions/vendor_boot.img", ""),
    ("vbmeta",        f"{ROOT}/base/partitions/vbmeta.img",      ""),
    ("vbmeta_system", f"{ROOT}/base/partitions/vbmeta_system.img",""),
    ("vbmeta_vendor", f"{ROOT}/base/partitions/vbmeta_vendor.img",""),
    ("system",        f"{ROOT}/donor/partitions/system.img",     "erofs"),
    ("system_ext",    f"{ROOT}/donor/partitions/system_ext.img", "erofs"),
    ("product",       f"{ROOT}/donor/partitions/product.img",    "erofs"),
    ("vendor",        f"{ROOT}/base/partitions/vendor.img",      "ext4"),
    ("vendor_dlkm",   f"{ROOT}/base/partitions/vendor_dlkm.img", "ext4"),
]
GROUP_MAX = 8528650240  # per-slot dynamic-partition group max (super metadata)


def build_manifest():
    m = um.DeltaArchiveManifest()
    m.block_size = BLOCK
    m.minor_version = 8
    m.max_timestamp = int(time.time())
    dpm = m.dynamic_partition_metadata
    dpm.snapshot_enabled = False
    g = dpm.groups.add()
    g.name = "google_dynamic_partitions"
    g.size = GROUP_MAX
    for n in ("system", "system_ext", "product", "vendor", "vendor_dlkm"):
        g.partition_names.append(n)

    global_doff = 0  # data_offset is GLOBAL across all partitions (cumulative)
    for name, path, fstype in PARTS:
        size = os.path.getsize(path)
        assert size % BLOCK == 0, f"{name} not block-aligned"
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 24), b""):
                h.update(chunk)
        p = m.partitions.add()
        p.partition_name = name
        if fstype:
            p.filesystem_type = fstype
        p.new_partition_info.size = size
        p.new_partition_info.hash = h.digest()

        nblocks = size // BLOCK
        cb = CHUNK // BLOCK
        with open(path, "rb") as f:
            for start in range(0, nblocks, cb):
                nb = min(cb, nblocks - start)
                data = f.read(nb * BLOCK)
                assert len(data) == nb * BLOCK
                op = p.operations.add()
                op.type = um.InstallOperation.REPLACE
                op.data_offset = global_doff
                op.data_length = nb * BLOCK
                op.data_sha256_hash = hashlib.sha256(data).digest()
                ext = op.dst_extents.add()
                ext.start_block = start
                ext.num_blocks = nb
                global_doff += nb * BLOCK
    return m


def write_payload(m, out):
    manifest = m.SerializeToString()
    header = b"CrAU" + struct.pack(">Q", 2) + struct.pack(">Q", len(manifest)) + struct.pack(">I", 0)
    meta_size = len(header) + len(manifest)          # = 24 + manifest_size
    meta_hash = hashlib.sha256(header + manifest).digest()

    file_hash = hashlib.sha256()
    op_map = {p.partition_name: p for p in m.partitions}
    with open(out, "wb") as out_f:
        out_f.write(header + manifest)
        file_hash.update(header + manifest)
        for name, path, _ in PARTS:
            part = op_map[name]
            for op in part.operations:
                assert op.data_sha256_hash, f"{name}: op missing hash"
                sb = op.dst_extents[0].start_block
                nb = sum(e.num_blocks for e in op.dst_extents)
                with open(path, "rb") as f:
                    f.seek(sb * BLOCK)
                    data = f.read(nb * BLOCK)
                assert len(data) == op.data_length
                assert hashlib.sha256(data).digest() == op.data_sha256_hash
                out_f.write(data)
                file_hash.update(data)
    props = (f"FILE_HASH={base64.b64encode(file_hash.digest()).decode()}\n"
             f"FILE_SIZE={os.path.getsize(out)}\n"
             f"METADATA_HASH={base64.b64encode(meta_hash).decode()}\n"
             f"METADATA_SIZE={meta_size}\n")
    with open(out + "_props.txt", "w") as f:
        f.write(props)
    return props


def self_test(payload_path):
    """Independent validation: payload_dumper parses + hash-verifies every op
    and every final image against the source images."""
    src = FileSource(payload_path)
    pl = parse_payload(src)
    validate_operations(pl.manifest.partitions)
    print(f"self-test: parsed {len(pl.manifest.partitions)} partitions, "
          f"all ops REPLACE-class, data_offset={pl.data_offset}")
    srcmap = {n: p for n, p, _ in PARTS}
    class _H:
        def __init__(self): self.h = hashlib.sha256()
        def write(self, data): self.h.update(data)
    for part in pl.manifest.partitions:
        h = _H()
        extract_partition_to_stream(src, pl.data_offset, part, h)
        got = h.h.hexdigest()
        want = part.new_partition_info.hash.hex()
        src_hash = hashlib.sha256(open(srcmap[part.partition_name], "rb").read(0) or b"")  # noqa
        # compare against source image on disk (streamed)
        sh = hashlib.sha256()
        with open(srcmap[part.partition_name], "rb") as f:
            for chunk in iter(lambda: f.read(1 << 24), b""):
                sh.update(chunk)
        ok = got == want and want == sh.hexdigest()
        print(f"  {part.partition_name:14} {'PASS' if ok else 'FAIL'} "
              f"({len(part.operations)} ops, {part.new_partition_info.size:,} B)")
        assert ok, part.partition_name
    print("SELF-TEST: ALL PARTITIONS VERIFIED")


if __name__ == "__main__":
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    payload = os.path.join(out_dir, "payload.bin")
    m = build_manifest()
    props = write_payload(m, payload)
    print(props)
    self_test(payload)
