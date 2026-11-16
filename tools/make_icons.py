"""
Generates the Nightfall Blade app icons.

Palette is taken straight from the game:
  #06070d  void black (background)
  #22d3ee  neon cyan (blade)
  #67e8f9  pale cyan (blade core)
  #fbbf24  amber (crossguard)
  #f43f5e  rose (pommel / slash)
  #e879f9  magenta (slash arc)

The art is drawn at high resolution, then crushed down to a 128px pixel grid
and blown back up with nearest-neighbour sampling, so the result keeps the
chunky pixel-art look of the game.

Run:  python tools/make_icons.py
"""

from PIL import Image, ImageDraw, ImageFilter
import math
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "src-tauri", "icons")

S = 1024          # working resolution
GRID = 128        # logical pixel grid

VOID = (6, 7, 13, 255)
DEEP = (12, 16, 34, 255)
CYAN = (34, 211, 238, 255)
PALE = (103, 232, 249, 255)
WHITE = (236, 254, 255, 255)
AMBER = (251, 191, 36, 255)
ROSE = (244, 63, 94, 255)
MAGENTA = (232, 121, 249, 255)
SLATE = (38, 46, 77, 255)


def rot(points, deg, cx, cy):
    r = math.radians(deg)
    cos, sin = math.cos(r), math.sin(r)
    out = []
    for x, y in points:
        dx, dy = x - cx, y - cy
        out.append((cx + dx * cos - dy * sin, cy + dx * sin + dy * cos))
    return out


def layer():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))


def build():
    # --- background: void with a soft blue core -------------------------
    base = Image.new("RGBA", (S, S), VOID)
    glow_bg = layer()
    ImageDraw.Draw(glow_bg).ellipse(
        [S * 0.12, S * 0.12, S * 0.88, S * 0.88], fill=DEEP)
    glow_bg = glow_bg.filter(ImageFilter.GaussianBlur(S * 0.09))
    base = Image.alpha_composite(base, glow_bg)

    # --- magenta slash arc behind the blade -----------------------------
    arc = layer()
    ad = ImageDraw.Draw(arc)
    ad.arc([S * 0.06, S * 0.06, S * 0.94, S * 0.94], start=200, end=325,
           fill=MAGENTA, width=int(S * 0.038))
    arc_glow = arc.filter(ImageFilter.GaussianBlur(S * 0.03))
    rose_glow = layer()
    ImageDraw.Draw(rose_glow).arc(
        [S * 0.06, S * 0.06, S * 0.94, S * 0.94], start=200, end=325,
        fill=ROSE, width=int(S * 0.07))
    rose_glow = rose_glow.filter(ImageFilter.GaussianBlur(S * 0.05))
    for _ in range(2):
        base = Image.alpha_composite(base, rose_glow)
    for _ in range(2):
        base = Image.alpha_composite(base, arc_glow)
    base = Image.alpha_composite(base, arc)

    cx, cy = S * 0.5, S * 0.52
    ANGLE = -38  # blade leans to the upper right

    # --- blade ----------------------------------------------------------
    blade = layer()
    bd = ImageDraw.Draw(blade)
    half = S * 0.052
    top = S * 0.11          # tip
    guard = S * 0.63        # where the crossguard sits
    bd.polygon(rot([
        (cx, top),
        (cx + half, top + S * 0.10),
        (cx + half, guard),
        (cx - half, guard),
        (cx - half, top + S * 0.10),
    ], ANGLE, cx, cy), fill=CYAN)

    # bright core down the middle of the blade
    core = half * 0.38
    bd.polygon(rot([
        (cx, top + S * 0.015),
        (cx + core, top + S * 0.105),
        (cx + core, guard - S * 0.01),
        (cx - core, guard - S * 0.01),
        (cx - core, top + S * 0.105),
    ], ANGLE, cx, cy), fill=WHITE)

    # pale edge highlight
    bd.polygon(rot([
        (cx - half, top + S * 0.105),
        (cx - half + S * 0.014, top + S * 0.105),
        (cx - half + S * 0.014, guard - S * 0.01),
        (cx - half, guard - S * 0.01),
    ], ANGLE, cx, cy), fill=PALE)

    # --- crossguard, grip, pommel ---------------------------------------
    hilt = layer()
    hd = ImageDraw.Draw(hilt)
    hd.polygon(rot([
        (cx - S * 0.165, guard),
        (cx + S * 0.165, guard),
        (cx + S * 0.135, guard + S * 0.055),
        (cx - S * 0.135, guard + S * 0.055),
    ], ANGLE, cx, cy), fill=AMBER)

    hd.polygon(rot([
        (cx - S * 0.032, guard + S * 0.055),
        (cx + S * 0.032, guard + S * 0.055),
        (cx + S * 0.032, guard + S * 0.19),
        (cx - S * 0.032, guard + S * 0.19),
    ], ANGLE, cx, cy), fill=SLATE)

    for i in range(3):
        y = guard + S * (0.075 + i * 0.038)
        hd.polygon(rot([
            (cx - S * 0.032, y),
            (cx + S * 0.032, y),
            (cx + S * 0.032, y + S * 0.016),
            (cx - S * 0.032, y + S * 0.016),
        ], ANGLE, cx, cy), fill=ROSE)

    hd.ellipse([0, 0, 1, 1], fill=None)
    px, py = rot([(cx, guard + S * 0.215)], ANGLE, cx, cy)[0]
    hd.ellipse([px - S * 0.042, py - S * 0.042,
                px + S * 0.042, py + S * 0.042], fill=ROSE)

    # --- glow passes ----------------------------------------------------
    sword = Image.alpha_composite(blade, hilt)
    wide = sword.filter(ImageFilter.GaussianBlur(S * 0.07))
    tight = sword.filter(ImageFilter.GaussianBlur(S * 0.02))
    for _ in range(3):
        base = Image.alpha_composite(base, wide)
    for _ in range(2):
        base = Image.alpha_composite(base, tight)
    base = Image.alpha_composite(base, sword)

    # --- thin neon frame ------------------------------------------------
    fr = layer()
    ImageDraw.Draw(fr).rectangle(
        [S * 0.035, S * 0.035, S * 0.965, S * 0.965],
        outline=CYAN, width=int(S * 0.012))
    base = Image.alpha_composite(base, Image.blend(
        Image.new("RGBA", (S, S), (0, 0, 0, 0)),
        fr.filter(ImageFilter.GaussianBlur(S * 0.012)), 0.55))
    base = Image.alpha_composite(base, Image.blend(
        Image.new("RGBA", (S, S), (0, 0, 0, 0)), fr, 0.7))

    # --- crush to a pixel grid -----------------------------------------
    pixel = base.resize((GRID, GRID), Image.BOX)
    return pixel


def main():
    os.makedirs(OUT, exist_ok=True)
    pixel = build()
    big = pixel.resize((S, S), Image.NEAREST)

    big.resize((512, 512), Image.NEAREST).save(os.path.join(OUT, "icon.png"))
    big.resize((128, 128), Image.NEAREST).save(os.path.join(OUT, "128x128.png"))
    big.resize((256, 256), Image.NEAREST).save(
        os.path.join(OUT, "128x128@2x.png"))
    pixel.resize((32, 32), Image.BOX).save(os.path.join(OUT, "32x32.png"))

    sizes = [(16, 16), (24, 24), (32, 32), (48, 48),
             (64, 64), (128, 128), (256, 256)]
    frames = [pixel.resize(s, Image.BOX if s[0] < 128 else Image.NEAREST)
              for s in sizes]
    frames[-1].save(os.path.join(OUT, "icon.ico"), format="ICO", sizes=sizes,
                    append_images=frames[:-1])
    print("icons written to", OUT)


if __name__ == "__main__":
    main()
