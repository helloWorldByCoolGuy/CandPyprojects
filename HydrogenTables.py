"""
Spectrum of Hydrogen — Measuring the Spectrum, steps 2–5.
Makes report-ready images:
  theta_table.png          Steps 1–2: θ = φ − φ0 and the ±1 order check
  wavelength_table.png     Steps 3–4: λ (eq. 5), Δλ, 1/m² − 1/n² (6 s.f.)
  fig_zero_order.png      Why θ+1 and θ−1 disagree (zero-order offset)
  fig_energy_levels_to_scale.png  Step 5: energy levels to scale, observed lines only
Images are saved next to this .py file.
"""

import os
import numpy as np
import matplotlib.pyplot as plt

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
def save(fig, name):
    fig.savefig(os.path.join(OUT_DIR, name), dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)

# ---------------- Data ----------------
a      = 1 / 600e3    # grating spacing (m): exactly 600 lines/mm (manual rounds to 1.667 µm)
phi0   = 230.0        # zero-order position (deg)
dtheta = 0.2          # angle uncertainty (deg), estimated for one line

# colour as seen, (m, n), phi(+1), phi(-1)
lines = [
    ("Red",        (2, 3), 253.4, 206.8),
    ("Blue", (2, 4), 247.3, 213.3),
    ("Violet",     (2, 5), 245.5, 215.0),
]
col   = [l[0] for l in lines]
mn    = [l[1] for l in lines]
phi_p = np.array([l[2] for l in lines])
phi_m = np.array([l[3] for l in lines])

# Step 2 — eq. (4): θ = φ − φ0  (θ−1 comes out negative: it is on the other side)
th_p = phi_p - phi0
th_m = phi_m - phi0
diff = np.abs(th_p) - np.abs(th_m)

# Step 3 — eq. (5): λ = [a sin|θ+1| + a sin|θ−1|] / 2
lam  = (a*np.sin(np.radians(np.abs(th_p))) + a*np.sin(np.radians(np.abs(th_m)))) / 2
dth  = np.radians(dtheta)
dlam = lam * dth * np.sqrt((a/lam)**2 - 1)
x    = np.array([1/m**2 - 1/n**2 for m, n in mn])
inv  = 1/lam
dinv = dlam/lam**2

def sf(v, n=6):
    """Format to n significant figures."""
    return f"{v:#.{n}g}"   # "#" keeps trailing zeros, e.g. 0.210000

# ---------------- Table helper ----------------
INK, MUTED, RULE, HEAD, FLAG = "#1f1f1f", "#6b6b6b", "#bdbdbd", "#f2f2f2", "#fde8e6"

def draw_table(header, rows, widths, title, note, fname, flags=None):
    fig_w = sum(widths) * 1.0
    fig_h = 0.48 * (len(rows) + 1) + 0.15
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis("off")
    t = ax.table(cellText=rows, colLabels=header, cellLoc="center",
                 colWidths=[w/sum(widths) for w in widths], loc="upper center")
    t.auto_set_font_size(False); t.set_fontsize(10); t.scale(1, 1.9)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor(RULE); cell.set_linewidth(0.6)
        cell.get_text().set_color(INK)
        if r == 0:
            cell.set_facecolor(HEAD); cell.get_text().set_weight("bold")
        elif flags is not None and flags[r-1] and c == len(header) - 1:
            cell.set_facecolor(FLAG)
    ax.set_title(title, loc="left", fontsize=11, color=INK, pad=6)
    ax.text(0.0, -0.08, note, transform=ax.transAxes, fontsize=8, color=MUTED, ha="left", va="top")
    save(fig, fname)

# ---------------- θ table (steps 1–2) ----------------
rows1 = []
for i in range(3):
    rows1.append([col[i], f"{phi0:.1f}", f"{phi_p[i]:.1f}", f"{phi_m[i]:.1f}",
                  f"{th_p[i]:+.1f}", f"{th_m[i]:+.1f}"])
draw_table(
    ["Line colour", "φ₀  (°)", "φ  m = +1  (°)", "φ  m = −1  (°)", "θ  m = +1  (°)", "θ  m = −1  (°)"],
    rows1, [1.6, 1.2, 1.7, 1.7, 1.7, 1.7],
    "Calculation of θ for various hydrogen spectral lines",
    "Angles read with the vernier to 0.1°. θ = φ − φ₀ (eq. 4); θ for m = −1 is negative because that order lies on the other side of the zero order.",
    "theta_table.png")

# ---------------- Wavelength table (steps 3–4) ----------------
rows2 = []
for i in range(3):
    rows2.append([col[i], f"{abs(th_p[i]):.1f}", f"{abs(th_m[i]):.1f}",
                  sf(lam[i]*1e9), f"{dlam[i]*1e9:.2g}", f"{mn[i][0]}, {mn[i][1]}",
                  sf(x[i]), sf(inv[i]/1e6), f"{dinv[i]/1e6:.2g}"])
draw_table(
    ["Line colour", "|θ₊₁| (°)", "|θ₋₁| (°)", "λ (nm)", "Δλ (nm)", "m, n",
     "1/m² − 1/n²", "1/λ (10⁶ m⁻¹)", "Δ(1/λ) (10⁶ m⁻¹)"],
    rows2, [1.5, 1.1, 1.1, 1.3, 1.1, 0.9, 1.5, 1.7, 1.9],
    "Calculation of wavelengths for various hydrogen spectral lines",
    f"a = 1/600 mm = 1.66667 µm. Δθ = {dtheta}° = {dth:.5f} rad (estimated for one line); "
    "Δλ/λ = Δθ√((a/λ)² − 1); Δ(1/λ) = Δλ/λ². Calculations to 6 s.f.; uncertainties to 2 s.f.",
    "wavelength_table.png")

# ---------------- Figure: zero-order check ----------------
# If φ0 is read off by δ, every θ+1 grows by δ and every |θ−1| shrinks by δ.
# So (φ+1 + φ−1)/2 is an independent estimate of the true zero order from each line.
phi0_line = (phi_p + phi_m) / 2
err = 0.1 / np.sqrt(2)          # two vernier readings averaged
fig, ax = plt.subplots(figsize=(7, 3.2))
ypos = np.arange(3)[::-1]
ax.axvline(phi0, color="#c0392b", ls=":", lw=1.5, label=f"Measured φ₀ = {phi0:.1f}°")
ax.axvline(phi0_line.mean(), color=INK, lw=1, ls="--",
           label=f"Mean implied φ₀ = {phi0_line.mean():.2f}°")
ax.errorbar(phi0_line, ypos, xerr=err, fmt="o", color="#2a6fdb", ms=8, capsize=4, lw=1.5,
            label="(φ₊₁ + φ₋₁)/2 for each line")
ax.set_yticks(ypos, col)
ax.set_xlabel("Zero-order position (°)")
ax.set_xlim(229.8, 230.5); ax.set_ylim(-0.7, 2.7)
ax.set_title("Each line's ± readings imply the zero order sits ~0.2° above the measured φ₀",
             loc="left", fontsize=10, color=INK)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="x", color="#e6e6e6")
ax.legend(frameon=False, fontsize=8, loc="lower right")
save(fig, "fig_zero_order.png")

# ---------------- Figure: energy levels to scale ----------------
# Two panels, both on a LINEAR energy axis (so both are "to scale"):
#   left  = all levels n = 1..6, shows the true size of the n = 1 gap
#   right = zoom on -3.7 to 0 eV, where n = 2..6 and the observed lines live
# The zoom is what stops n = 4, 5, 6 and the arrows from piling on top of each other.
from matplotlib.patches import Rectangle, ConnectionPatch
E = lambda n: -13.6057 / n**2
colours = {"Red": "#d62728", "Blue": "#1f77b4", "Violet": "#7b3fbf"}
ZOOM = (-3.75, 0.25)

fig, (axL, axR) = plt.subplots(1, 2, figsize=(10, 7.5),
                               gridspec_kw={"width_ratios": [1, 2.4], "wspace": 0.35})

# Left: full scale
for n in range(1, 7):
    axL.plot([0, 1], [E(n)]*2, color=INK, lw=1.2)
axL.plot([0, 1], [0, 0], color=MUTED, lw=1, ls=":")
for n in (1, 2, 3):
    axL.text(1.06, E(n), f"n = {n}", va="center", fontsize=9, color=INK)
axL.text(1.06, -0.55, "n = 4–6", va="center", fontsize=9, color=INK)
axL.add_patch(Rectangle((-0.04, ZOOM[0]), 1.08, ZOOM[1]-ZOOM[0], fill=False,
                        ec=MUTED, lw=1, ls="--"))
axL.set_xlim(-0.1, 1.5); axL.set_ylim(-14.5, 0.8)
axL.set_xticks([]); axL.set_ylabel("Energy (eV)")
axL.spines[["top", "right", "bottom"]].set_visible(False)
axL.set_title("All levels (n = 1 to 6)", loc="left", fontsize=10, color=INK)

# Right: zoom on the Balmer region
for n in range(2, 7):
    axR.plot([0, 1], [E(n)]*2, color=INK, lw=1.4)
axR.plot([0, 1], [0, 0], color=MUTED, lw=1, ls=":")
# In the zoom there is room to label every level at its true height
for n in range(2, 7):
    axR.text(1.04, E(n), f"n = {n}   {E(n):.2f} eV", va="center", fontsize=9.5, color=INK)
axR.text(1.04, 0, "n = ∞   0 eV", va="center", fontsize=9.5, color=MUTED)

for i, (m, n) in enumerate(mn):
    xp = 0.15 + 0.30*i
    axR.annotate("", xy=(xp, E(m)), xytext=(xp, E(n)),
                 arrowprops=dict(arrowstyle="-|>", color=colours[col[i]], lw=2.4,
                                 shrinkA=0, shrinkB=0, mutation_scale=16))
    axR.text(xp + 0.03, -2.75, f"{n} → {m}\n{col[i]}\n{lam[i]*1e9:.1f} nm",
             fontsize=9, color=INK, va="center", linespacing=1.3)
axR.set_xlim(-0.05, 1.55); axR.set_ylim(*ZOOM)
axR.set_xticks([]); axR.set_ylabel("Energy (eV)")
axR.spines[["top", "right", "bottom"]].set_visible(False)
axR.set_title("Zoom of dashed box: observed Balmer transitions", loc="left",
              fontsize=10, color=INK)

fig.suptitle("Hydrogen energy levels to scale with the observed transitions",
             x=0.06, ha="left", fontsize=11, color=INK)
save(fig, "fig_energy_levels_to_scale.png")

# Console summary
print("\nθ:", np.round(th_p, 1), np.round(th_m, 1), "  |θ+|−|θ−| =", np.round(diff, 1))
print("λ (nm):", [sf(v*1e9) for v in lam], " Δλ (nm):", np.round(dlam*1e9, 2))