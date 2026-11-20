#!/usr/bin/env python3
"""Extract + parse DeltaArchiveManifest from AOSP OTA payload.bin (read-only).

Handles the payload header empirically:
  magic "CrAU" (4) | version (8 BE) | manifest_size (8 BE) | sig_size (8 or 4 BE) | manifest
Both sig-field widths are tried; the candidate whose manifest parses into
plausible top-level submessages with partition-name strings wins.

Usage:
  payload_manifest.py <zip-with-payload.bin>
  payload_manifest.py <raw-file> <byte-offset>

Env PCR_MANIFEST_OUT=<path> saves the winning manifest protobuf.
"""
import os
import struct
import sys
import zipfile

OP_NAMES = {
    0: "REPLACE", 1: "REPLACE_BZ", 2: "MOVE", 3: "BSDIFF",
    4: "SOURCE_COPY", 5: "SOURCE_BSDIFF", 6: "REPLACE_XZ",
    7: "ZERO", 8: "DISCARD", 9: "BROTLI_BSDIFF", 10: "PUFFDIFF",
    11: "ZUCCHINI", 12: "LZ4DIFF_BSDIFF", 13: "LZ4DIFF_PUFFDIFF",
}


def _varint(buf, pos):
    shift = result = 0
    while True:
        b = buf[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            return result, pos
        shift += 7


def parse_fields(buf, start=0, end=None):
    if end is None:
        end = len(buf)
    pos = start
    while pos < end:
        key, pos = _varint(buf, pos)
        field, wtype = key >> 3, key & 7
        if wtype == 0:
            val, pos = _varint(buf, pos)
        elif wtype == 1:
            val = buf[pos:pos + 8]; pos += 8
        elif wtype == 2:
            ln, pos = _varint(buf, pos)
            val = (pos, pos + ln); pos += ln
        elif wtype == 5:
            val = buf[pos:pos + 4]; pos += 4
        else:
            raise ValueError(f"bad wire type {wtype}")
        yield field, wtype, val


def looks_like_name(s):
    return (s and len(s) <= 64 and s[0].isalpha()
            and all(c.isalnum() or c in "_-." for c in s))


def extract_partitions(buf):
    """Return dict name -> list of (op_type, data_length) from a manifest."""
    parts = {}
    for f, w, v in parse_fields(buf, 0, len(buf)):
        if w != 2:
            continue
        # candidate PartitionUpdate: subfield 1 = string partition_name
        name = None
        try:
            for f2, w2, v2 in parse_fields(buf, v[0], v[1]):
                if f2 == 1 and w2 == 2:
                    cand = buf[v2[0]:v2[1]].decode("utf-8", "replace")
                    if looks_like_name(cand):
                        name = cand
                    break
        except Exception:
            continue
        if not name:
            continue
        ops = []
        try:
            for f2, w2, v2 in parse_fields(buf, v[0], v[1]):
                if w2 != 2:
                    continue
                # either a container of InstallOperation (field1=bytes) or one op
                inner = list(parse_fields(buf, v2[0], v2[1]))
                if not inner:
                    continue
                cands = []
                if inner[0][0] == 1 and inner[0][1] == 2:
                    cands = [(v2[0], v2[1])] if (inner[0][0] == 1 and inner[0][1] == 0) else None
                    cands = None
                    # container: iterate children
                    for f3, w3, v3 in inner:
                        if f3 == 1 and w3 == 2:
                            cands = cands or []
                            cands.append((v3[0], v3[1]))
                elif inner[0][0] == 1 and inner[0][1] == 0:
                    cands = [(v2[0], v2[1])]
                if not cands:
                    continue
                for (s, e) in cands:
                    op_type = data_len = None
                    data_len = 0
                    for f3, w3, v3 in parse_fields(buf, s, e):
                        if f3 == 1 and w3 == 0 and v3 <= 13:
                            op_type = v3
                        elif f3 == 3 and w3 == 0:
                            data_len = v3
                    if op_type is not None:
                        ops.append((op_type, data_len))
        except Exception:
            pass
        if ops or name not in parts:
            parts.setdefault(name, []).extend(ops)
    return parts


def score(parts):
    return len(parts), sum(len(v) for v in parts.values())


def try_candidates(head, fp, msize):
    """Try manifest offsets for sig-field widths 8 and 4 bytes."""
    results = []
    # layout A: magic(4)+ver(8)+msize(8)+sig(8)  -> manifest at 28
    # layout B: magic(4)+ver(8)+msize(8)+sig(4)  -> manifest at 24
    for manifest_off in (28, 24):
        fp.seek(manifest_off)
        manifest = fp.read(msize)
        if len(manifest) < msize:
            continue
        try:
            parts = extract_partitions(manifest)
            results.append((score(parts), manifest_off, manifest, parts))
        except Exception as ex:
            results.append(((0, 0), manifest_off, manifest, {}))
    results.sort(key=lambda r: r[0], reverse=True)
    return results


def process(label, fp, base=0):
    magic = fp.read(4)
    if magic != b"CrAU":
        raise SystemExit(f"{label}: bad magic {magic!r}")
    version = struct.unpack(">Q", fp.read(8))[0]
    msize = struct.unpack(">Q", fp.read(8))[0]
    print(f"{label}: magic OK, version={version}, manifest_size={msize}")
    results = try_candidates(None, fp, msize)
    (sc, off, manifest, parts) = results[0]
    print(f"{label}: using manifest layout with sig-field width {'8' if off==28 else '4'} "
          f"-> partitions={sc[0]}, ops={sc[1]}")
    if sc[0] == 0:
        # fallback: dump raw strings to see what's there
        import re
        strs = re.findall(rb"[\x20-\x7e]{4,}", manifest[:200000])
        print(f"{label}: NO partitions parsed; first strings: "
              f"{[s.decode() for s in strs[:20]]}")
    else:
        print(f"{'partition':<24} {'ops':>5} {'data(MB)':>10}  types")
        total_ops = 0
        for name, ops in sorted(parts.items()):
            dsum = sum(d for _, d in ops)
            total_ops += len(ops)
            types = {}
            for t, _ in ops:
                k = OP_NAMES.get(t, str(t))
                types[k] = types.get(k, 0) + 1
            print(f"{name:<24} {len(ops):>5} {dsum/1048576:>10.1f}  {types}")
        print(f"{'TOTAL':<24} {total_ops:>5}")
    out = os.environ.get("PCR_MANIFEST_OUT")
    if out:
        with open(out, "wb") as o:
            o.write(manifest)
        print(f"saved manifest -> {out}")
    return parts


class _OffsetIO:
    """Seekable view over a region of a file (for zipfile over stored entries)."""
    def __init__(self, path, offset, size):
        self._f = open(path, "rb"); self._off = offset; self._size = size
    def seek(self, off, whence=0):
        t = off if whence == 0 else (self._f.tell() + off if whence == 1 else self._size + off)
        return self._f.seek(self._off + t) - self._off
    def tell(self): return self._f.tell() - self._off
    def read(self, n=-1):
        if n is None or n < 0: n = self._size - self.tell()
        return self._f.read(min(n, self._size - self.tell()))
    def seekable(self): return True
    def readable(self): return True
    def close(self): self._f.close()


def open_zip_payload(path, label):
    with zipfile.ZipFile(path) as z:
        with z.open("payload.bin") as fp:
            return process(label, fp)


def open_raw_payload(path, offset, label):
    with open(path, "rb") as fp:
        fp.seek(offset)
        return process(label, fp)


def open_donor_payload(outer_path, inner_name):
    """Donor: inner zip is STORED inside outer zip at offset 86."""
    inner_off = 86
    inner_size = 9584855370
    io = _OffsetIO(outer_path, inner_off, inner_size)
    iz = zipfile.ZipFile(io)
    info = iz.getinfo("payload.bin")
    # read local header to get exact data offset (relative to inner zip)
    io.seek(info.header_offset)
    lh = io.read(30)
    nlen, xlen = struct.unpack("<HH", lh[26:30])
    data_rel = info.header_offset + 30 + nlen + xlen
    io.close()
    return open_raw_payload(outer_path, inner_off + data_rel, "donor")


def main():
    path = sys.argv[1]
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
        if "payload.bin" in names:
            open_zip_payload(path, os.path.basename(path)[:40])
            return
        # nested donor zip
        if len(names) >= 1 and names[0].endswith(".zip"):
            open_donor_payload(path, names[0])
            return
        raise SystemExit(f"no payload.bin; entries: {names}")
    offset = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    open_raw_payload(path, offset, os.path.basename(path)[:40])


if __name__ == "__main__":
    main()
