"""Generate the two self-contained illustrations used by the dashboard.

No external image service or downloaded asset is required, so the app looks
identical on a laptop and on Render. Run: python make_art.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch
from matplotlib.transforms import Affine2D
import numpy as np

OUT = Path(__file__).resolve().parent / "assets"
OUT.mkdir(exist_ok=True)

INK = "#0B1020"
SLATE = "#1C242B"
RICE = "#F5EFE3"
SALMON = "#F08A6B"
TUNA = "#C8445B"
YELLOWTAIL = "#E8C468"
NORI = "#16231F"
AVOCADO = "#7FA650"
GINGER = "#E9A9A6"
WASABI = "#8FBF6A"


def background(ax, w, h, glow_at=(0.7, 0.5)):
    top = np.array([11, 16, 32], dtype=float)
    bottom = np.array([24, 31, 44], dtype=float)
    grad = np.zeros((300, 600, 3))
    for row in range(300):
        t = row / 299
        grad[row, :, :] = top * (1 - t) + bottom * t
    gx, gy = glow_at[0] * 600, (1 - glow_at[1]) * 300
    yy, xx = np.mgrid[0:300, 0:600]
    glow = np.exp(-(((xx - gx) / 230) ** 2 + ((yy - gy) / 150) ** 2))
    grad += glow[..., None] * np.array([34, 18, 10])
    ax.imshow(np.clip(grad, 0, 255).astype(np.uint8), extent=[0, w, 0, h], aspect="auto", zorder=0)


def shadow(ax, x, y, rx, ry):
    ax.add_patch(Ellipse((x + 0.04, y - 0.06), rx * 2, ry * 2,
                         facecolor="#000000", edgecolor="none", alpha=0.30, zorder=2))


def nigiri(ax, x, y, fish=SALMON, s=1.0, angle=0):
    trans = Affine2D().rotate_deg_around(x, y, angle) + ax.transData
    shadow(ax, x, y, 0.36 * s, 0.20 * s)
    ax.add_patch(FancyBboxPatch(
        (x - 0.34 * s, y - 0.17 * s), 0.68 * s, 0.34 * s,
        boxstyle="round,pad=0.01,rounding_size=0.16",
        facecolor=RICE, edgecolor="#D9CDBB", lw=0.5, zorder=4, transform=trans))
    ax.add_patch(FancyBboxPatch(
        (x - 0.37 * s, y - 0.03 * s), 0.74 * s, 0.27 * s,
        boxstyle="round,pad=0.01,rounding_size=0.12",
        facecolor=fish, edgecolor="none", zorder=5, transform=trans))
    if fish == SALMON:
        for dx in (-0.20, 0.0, 0.20):
            ax.add_patch(FancyBboxPatch(
                (x + dx * s - 0.012 * s, y + 0.0), 0.024 * s, 0.22 * s,
                boxstyle="round,pad=0,rounding_size=0.01",
                facecolor="#FBD2BC", edgecolor="none", alpha=0.7, zorder=6, transform=trans))


def maki(ax, x, y, r=0.30, filling=AVOCADO, accent=SALMON):
    shadow(ax, x, y, r, r * 0.9)
    ax.add_patch(Circle((x, y), r, facecolor=NORI, edgecolor="#0A1210", lw=1, zorder=4))
    ax.add_patch(Circle((x, y), r * 0.77, facecolor=RICE, edgecolor="none", zorder=5))
    ax.add_patch(Circle((x + r * 0.16, y + r * 0.06), r * 0.34,
                        facecolor=filling, edgecolor="none", zorder=6))
    ax.add_patch(Circle((x - r * 0.20, y - r * 0.12), r * 0.24,
                        facecolor=accent, edgecolor="none", zorder=6))


def sashimi(ax, x, y, color=SALMON, s=1.0, angle=-18):
    trans = Affine2D().rotate_deg_around(x, y, angle) + ax.transData
    shadow(ax, x, y, 0.45 * s, 0.18 * s)
    ax.add_patch(FancyBboxPatch(
        (x - 0.43 * s, y - 0.15 * s), 0.86 * s, 0.30 * s,
        boxstyle="round,pad=0.01,rounding_size=0.10",
        facecolor=color, edgecolor="none", zorder=5, transform=trans))
    ax.add_patch(FancyBboxPatch(
        (x - 0.36 * s, y - 0.09 * s), 0.72 * s, 0.035 * s,
        boxstyle="round,pad=0,rounding_size=0.015",
        facecolor="#FFE1CF" if color == SALMON else "#F0A0A8",
        edgecolor="none", alpha=0.45, zorder=6, transform=trans))


def garnish(ax, x, y):
    ax.add_patch(Ellipse((x, y), 0.30, 0.22, facecolor=WASABI,
                         edgecolor="none", alpha=0.9, zorder=4))
    for dx, dy in ((0, 0), (0.22, 0.10), (0.40, -0.03)):
        ax.add_patch(Ellipse((x + dx, y + dy), 0.26, 0.16,
                             facecolor=GINGER, edgecolor="none", alpha=0.85, zorder=4))


def hero():
    fig = plt.figure(figsize=(12, 4), dpi=180)
    fig.patch.set_facecolor(INK)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4)
    ax.axis("off")
    background(ax, 12, 4, glow_at=(0.72, 0.5))
    ax.add_patch(Ellipse((8.7, 2.0), 6.4, 3.5, facecolor=SLATE,
                         edgecolor="#33414B", lw=1.5, zorder=1))
    ax.add_patch(Ellipse((8.7, 2.0), 5.9, 3.1, facecolor="#151D24",
                         edgecolor="none", zorder=2))
    for px, py, fish, ang in [
        (6.9, 2.85, SALMON, -12), (7.8, 3.00, TUNA, 8), (8.7, 2.90, YELLOWTAIL, -5),
        (7.1, 1.35, TUNA, 12), (8.0, 1.25, SALMON, -8),
    ]:
        nigiri(ax, px, py, fish, s=1.05, angle=ang)
    sashimi(ax, 9.55, 2.65, SALMON, 1.05, -20)
    sashimi(ax, 9.70, 2.25, TUNA, 1.05, 16)
    sashimi(ax, 9.55, 1.85, SALMON, 1.05, -10)
    maki(ax, 10.75, 2.75, 0.34, AVOCADO, SALMON)
    maki(ax, 11.15, 2.15, 0.34, AVOCADO, TUNA)
    maki(ax, 10.55, 1.45, 0.34, YELLOWTAIL, SALMON)
    garnish(ax, 8.75, 0.95)
    ax.add_patch(Circle((6.65, 1.20), 0.30, facecolor="#2A1D18",
                        edgecolor="#4A3327", lw=1, zorder=4))
    ax.add_patch(Circle((6.65, 1.20), 0.22, facecolor="#6E3B24",
                        edgecolor="none", zorder=5))
    ax.plot([0.72, 0.72], [0.85, 3.15], color="#E4572E", lw=3, zorder=5)
    fig.savefig(OUT / "hero.png", dpi=180, facecolor=INK)
    plt.close(fig)


def plate():
    fig = plt.figure(figsize=(6, 6), dpi=180)
    fig.patch.set_facecolor(INK)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 6)
    ax.axis("off")
    background(ax, 6, 6, glow_at=(0.5, 0.5))
    ax.add_patch(Circle((3, 3), 2.45, facecolor=SLATE,
                        edgecolor="#33414B", lw=2, zorder=1))
    ax.add_patch(Circle((3, 3), 2.20, facecolor="#151D24",
                        edgecolor="none", zorder=2))
    nigiri(ax, 2.15, 4.05, SALMON, 1.0, -14)
    nigiri(ax, 3.15, 4.30, TUNA, 1.0, 6)
    nigiri(ax, 4.05, 3.95, YELLOWTAIL, 1.0, -6)
    sashimi(ax, 4.35, 3.00, SALMON, 0.9, 20)
    sashimi(ax, 4.25, 2.45, TUNA, 0.9, -14)
    maki(ax, 3.65, 1.75, 0.32, AVOCADO, SALMON)
    maki(ax, 2.75, 1.65, 0.32, AVOCADO, TUNA)
    maki(ax, 1.85, 2.10, 0.32, YELLOWTAIL, SALMON)
    sashimi(ax, 1.55, 3.05, TUNA, 0.85, 12)
    garnish(ax, 2.35, 2.75)
    fig.savefig(OUT / "plate.png", dpi=180, facecolor=INK)
    plt.close(fig)


if __name__ == "__main__":
    hero()
    plate()
    for p in sorted(OUT.glob("*.png")):
        print(f"Wrote {p.name} ({p.stat().st_size / 1024:.0f} KB)")
