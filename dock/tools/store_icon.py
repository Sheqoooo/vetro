"""Draw the Apps installieren tile at Vetro's native focus size."""
from pathlib import Path
import math
import struct
import zlib

from layout_consts import FOCUS_ICON, design_num


def rounded_box(x, y, left, top, right, bottom, radius):
    dx = max(left + radius - x, x - right + radius, 0)
    dy = max(top + radius - y, y - bottom + radius, 0)
    return dx * dx + dy * dy <= radius * radius


def sample(x, y, radius):
    if not rounded_box(x, y, 0, 0, 128, 128, radius):
        return (0, 0, 0, 0)
    glow = math.exp(-((x - 24) ** 2 + (y - 8) ** 2) / 3400)
    background = (29 + 24 * glow, 36 + 35 * glow, 62 + 54 * glow, 255)
    # An app grid with a plus in the fourth cell.
    for left, top in ((34, 34), (68, 34), (34, 68)):
        if rounded_box(x, y, left, top, left + 25, top + 25, 5):
            return (232, 242, 255, 255)
    if (rounded_box(x, y, 69, 78, 93, 84, 3)
            or rounded_box(x, y, 78, 69, 84, 93, 3)):
        return (167, 214, 255, 255)
    return background


def chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


def render(path):
    size = FOCUS_ICON
    radius = design_num("IconRadiusPct") * 128 / 100
    pixels = bytearray()
    for y in range(size):
        pixels.append(0)
        for x in range(size):
            samples = [sample((x + dx) * 128 / size, (y + dy) * 128 / size, radius)
                       for dy in (0.125, 0.375, 0.625, 0.875)
                       for dx in (0.125, 0.375, 0.625, 0.875)]
            visible = [color for color in samples if color[3]]
            pixels.extend([round(sum(c[i] for c in visible) / len(visible)) if visible else 0
                           for i in range(3)])
            pixels.append(round(255 * len(visible) / len(samples)))
    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
                     + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b""))


if __name__ == "__main__":
    render(Path(__file__).resolve().parents[1] / "res/icons/apps-installieren.png")
