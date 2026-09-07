"""Parse the MP4 box tree to prove what is actually in the file.

The encoder printing "audio: score.wav" only proves a strip was added. This
reads the container: track count, handler types, duration from mvhd/mdhd.
"""
import struct, sys

def walk(f, end, depth=0, out=None):
    out = out if out is not None else []
    while f.tell() < end:
        pos = f.tell()
        hdr = f.read(8)
        if len(hdr) < 8:
            break
        size, typ = struct.unpack(">I4s", hdr)
        typ = typ.decode("latin1")
        if size == 1:
            size = struct.unpack(">Q", f.read(8))[0]
            body = pos + 16
        elif size == 0:
            size = end - pos
            body = pos + 8
        else:
            body = pos + 8
        out.append((depth, typ, size))
        if typ in ("moov", "trak", "mdia", "minf", "stbl", "udta"):
            walk(f, pos + size, depth + 1, out)
        elif typ == "mvhd":
            f.seek(body)
            ver = f.read(1)[0]; f.read(3)
            if ver == 1:
                f.read(16); ts = struct.unpack(">I", f.read(4))[0]
                dur = struct.unpack(">Q", f.read(8))[0]
            else:
                f.read(8); ts = struct.unpack(">I", f.read(4))[0]
                dur = struct.unpack(">I", f.read(4))[0]
            out.append((depth + 1, "  duration=%.2fs" % (dur / ts if ts else 0), 0))
        elif typ == "hdlr":
            f.seek(body + 8)
            out.append((depth + 1, "  handler=" + f.read(4).decode("latin1"), 0))
        f.seek(pos + size)
    return out

path = sys.argv[1]
with open(path, "rb") as f:
    f.seek(0, 2); end = f.tell(); f.seek(0)
    boxes = walk(f, end)
handlers = [t.split("=")[1] for d, t, s in boxes if t.startswith("  handler=")]
dur = [t for d, t, s in boxes if t.startswith("  duration=")]
print("file      ", path)
print("top boxes ", [t for d, t, s in boxes if d == 0])
print("tracks    ", len([1 for d, t, s in boxes if t == "trak"]))
print("handlers  ", handlers)
print(dur[0].strip() if dur else "duration   UNKNOWN")
print("VIDEO", "OK" if "vide" in handlers else "MISSING",
      "| AUDIO", "OK" if "soun" in handlers else "MISSING")
