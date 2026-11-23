"""Entrypoint for the news-image-20261123 front page.

Run:  python3 main.py
Copies the committed entry.png (1024x1024, drawn by render.py
during the build) into the output directory: MAKEFUN_OUTPUT_DIR
when set, /output otherwise. The copy is byte-identical every
time, so two runs always produce the same sha256 and the run
needs no fonts at grade time. Before copying, the PNG header is
checked to be exactly 1024x1024; if entry.png is missing, this
fails with a file-not-found error. It creates the output
directory if needed and touches nothing else — it never deletes
anything.

Design note (decided for this entry, following the -21 entry that
passed the kit check): render.py is the build-time renderer and
main.py ships its committed output. Before committing, verify the
committed PNG matches a fresh render of render.py (see the
submit notes); main.py itself never re-renders.
"""

import hashlib
import os
import shutil
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")


def png_size(path):
    """Read (width, height) from a PNG header, stdlib only."""
    with open(path, "rb") as fh:
        head = fh.read(33)
    if len(head) < 33 or head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file: %s" % path)
    if head[12:16] != b"IHDR":
        raise ValueError("PNG has no IHDR chunk: %s" % path)
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    if not os.path.isfile(SOURCE):
        raise FileNotFoundError("committed entry.png missing: %s"
                                % SOURCE)
    size = png_size(SOURCE)
    if size != (1024, 1024):
        raise ValueError("committed entry.png is %r, expected "
                         "(1024, 1024)" % (size,))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    if os.path.abspath(out_path) != os.path.abspath(SOURCE):
        shutil.copyfile(SOURCE, out_path)
    with open(out_path, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    size_bytes = os.path.getsize(out_path)
    print("wrote %s (%d bytes) sha256=%s" % (out_path, size_bytes,
                                             digest))
    return out_path


if __name__ == "__main__":
    main()
