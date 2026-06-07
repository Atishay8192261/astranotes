"""Generate AstraNotes app icon (PNG + ICNS for macOS .app bundle).

Run once:  python scripts/create_icon.py
Outputs:
  assets/icon.png           — 1024x1024 source
  assets/icon_256.png       — 256x256 for window title bar
  AstraNotes.app bundle     — ICNS set via iconutil
"""

from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Run:  pip install Pillow")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
ASSETS = ROOT / "astranotes" / "assets"
ASSETS.mkdir(exist_ok=True)


def _rounded_rect(draw: ImageDraw.ImageDraw, xy, radius: int, fill) -> None:
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill)


def _star_polygon(cx: float, cy: float, outer: float, inner: float, points: int):
    """Return vertex list for a star polygon."""
    verts = []
    for i in range(points * 2):
        angle = math.pi * i / points - math.pi / 2
        r = outer if i % 2 == 0 else inner
        verts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return verts


def make_icon(size: int = 1024) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # ── rounded-square background ─────────────────────────────────────────
    pad = int(size * 0.04)
    radius = int(size * 0.22)

    # Outer glow (very subtle shadow under the square)
    for blur_i in range(6, 0, -1):
        alpha = int(40 / blur_i)
        shadow_color = (108, 92, 231, alpha)
        _rounded_rect(
            draw,
            (pad + blur_i * 2, pad + blur_i * 2, size - pad + blur_i * 2, size - pad + blur_i * 2),
            radius,
            shadow_color,
        )

    # Background gradient (violet → indigo, simulated as two overlapping layers)
    # Layer 1 — base violet
    _rounded_rect(draw, (pad, pad, size - pad, size - pad), radius, (120, 86, 255, 255))
    # Layer 2 — darker indigo overlay on the bottom half
    overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    _rounded_rect(ov_draw, (pad, size // 2, size - pad, size - pad), 0, (72, 52, 212, 120))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # ── white star (✦ 4-point sparkle) ───────────────────────────────────
    cx, cy = size / 2, size * 0.44
    outer_r = size * 0.26
    inner_r = size * 0.07
    star = _star_polygon(cx, cy, outer_r, inner_r, 4)
    draw.polygon(star, fill=(255, 255, 255, 255))

    # Small extra sparkle top-right
    cx2, cy2 = cx + size * 0.18, cy - size * 0.19
    outer2 = size * 0.07
    inner2 = size * 0.02
    star2 = _star_polygon(cx2, cy2, outer2, inner2, 4)
    draw.polygon(star2, fill=(255, 255, 255, 200))

    # ── "notes" text label ────────────────────────────────────────────────
    font_size = int(size * 0.09)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/SFNSDisplay.ttf", font_size)
    except Exception:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except Exception:
            font = ImageFont.load_default()

    label = "AstraNotes"
    bbox = draw.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(
        (size / 2 - tw / 2, size * 0.73),
        label,
        fill=(255, 255, 255, 220),
        font=font,
    )

    return img


def export_icns(src_png: Path, app_bundle: Path) -> None:
    """Convert PNG → ICNS using macOS iconutil."""
    iconset = ASSETS / "AppIcon.iconset"
    iconset.mkdir(exist_ok=True)

    sizes = [16, 32, 64, 128, 256, 512, 1024]
    base = Image.open(src_png)
    for s in sizes:
        resized = base.resize((s, s), Image.LANCZOS)
        resized.save(iconset / f"icon_{s}x{s}.png")
        if s <= 512:
            resized2 = base.resize((s * 2, s * 2), Image.LANCZOS)
            resized2.save(iconset / f"icon_{s}x{s}@2x.png")

    icns_path = ASSETS / "AppIcon.icns"
    result = subprocess.run(
        ["iconutil", "-c", "icns", str(iconset), "-o", str(icns_path)],
        capture_output=True,
    )
    if result.returncode == 0:
        print(f"ICNS written: {icns_path}")
        # Copy to .app bundle
        res_dir = app_bundle / "Contents" / "Resources"
        res_dir.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy(icns_path, res_dir / "AppIcon.icns")
        print(f"Copied to .app bundle: {res_dir / 'AppIcon.icns'}")
    else:
        print("iconutil failed:", result.stderr.decode())


if __name__ == "__main__":
    print("Generating AstraNotes icon...")
    icon = make_icon(1024)
    png_path = ASSETS / "icon.png"
    icon.save(png_path, "PNG")
    print(f"Icon saved: {png_path}")

    small = icon.resize((256, 256), Image.LANCZOS)
    small.save(ASSETS / "icon_256.png", "PNG")
    print(f"Small icon saved: {ASSETS / 'icon_256.png'}")

    app_bundle = Path.home() / "Desktop" / "AstraNotes.app"
    if app_bundle.exists():
        export_icns(png_path, app_bundle)

    print("Done.")
