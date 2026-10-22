"""
Hall Effect - Report figures and table images
---------------------------------------------
Saves (next to this .py file):
  hall_data_table.png         Hall voltage measurements table
  hall_voltage_vs_current.png phi_H vs I with linear fit
  hall_residuals.png          residuals in units of sigma
"""

import os
import numpy as np
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))

# ── Data (same as analysis script) ─────────────────────────
I_mA = np.arange(1, 26, dtype=float)
phi_mV = np.array([2.5, 7.3, 13.6, 12.2, 18.8, 24.7, 27.8, 29.0, 32.0, 36.7,
                   45.3, 49.6, 50.1, 57.7, 60.9, 66.0, 70.0, 76.1, 78.4, 86.8,
                   91.9, 97.0, 102.9, 112.1, 115.2])

(m, c) = np.polyfit(I_mA, phi_mV, 1)          # mV per mA = V/A
res = phi_mV - (m * I_mA + c)
sigma = np.sqrt(np.sum(res**2) / (len(I_mA) - 2))

plt.rcParams.update({"font.size": 11, "font.family": "serif"})

# ── Table image ────────────────────────────────────────────
rows = [[f"{a:.0f}", f"{b:.1f}"] for a, b in zip(I_mA, phi_mV)]
fig, ax = plt.subplots(figsize=(4.2, 9.0))
ax.axis("off")
tbl = ax.table(cellText=rows, colLabels=["Current (mA)", "Voltage (mV)"],
               loc="center", cellLoc="center")
tbl.auto_set_font_size(False)
tbl.set_fontsize(11)
tbl.scale(1, 1.55)
for (r, _), cell in tbl.get_celld().items():
    cell.set_edgecolor("#999999")
    if r == 0:
        cell.set_text_props(weight="bold")
        cell.set_facecolor("#eeeeee")
ax.set_title("Hall voltage measurements", fontsize=12, pad=8)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "hall_data_table.png"), dpi=200, bbox_inches="tight")
plt.close(fig)

# ── Figure: phi_H vs I with fit ────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4.5))
Ix = np.linspace(0, 26, 100)
ax.plot(I_mA, phi_mV, "o", color="#2b6cb0", ms=5, label="Measured")
ax.plot(Ix, m * Ix + c, "-", color="#c53030", lw=1.5,
        label=fr"Linear fit, slope = {m:.2f} V/A")
ax.set_xlabel(r"Current $I$ (mA)")
ax.set_ylabel(r"Hall voltage $\phi_H$ (mV)")
ax.set_xlim(0, 26)
ax.set_ylim(0, None)
ax.grid(alpha=0.3)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "hall_voltage_vs_current.png"), dpi=200)
plt.close(fig)

# ── Figure: residuals in units of sigma ────────────────────
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.axhline(0, color="black", lw=0.8)
for k in (1, 2):
    ax.axhline(k, color="grey", ls="--", lw=0.6)
    ax.axhline(-k, color="grey", ls="--", lw=0.6)
ax.plot(I_mA, res / sigma, "o", color="#2b6cb0", ms=5)
ax.set_xlabel(r"Current $I$ (mA)")
ax.set_ylabel(r"Residual ($\sigma$)")
ax.set_xlim(0, 26)
ax.set_ylim(-3, 3)
ax.text(0.99, 0.95, fr"$\sigma$ = {sigma:.2f} mV", transform=ax.transAxes,
        ha="right", va="top")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "hall_residuals.png"), dpi=200)
plt.close(fig)

# ── Figure: carrier density on a log scale ─────────────────
e, B, T = 1.602e-19, 0.3435, 1.000e-3
n_meas = B / (e * T * m)          # m is in mV/mA = V/A
dn = n_meas * 0.102               # combined 10.2% from analysis script

fig, ax = plt.subplots(figsize=(8, 2.8))
ax.set_xscale("log")
ax.set_xlim(1e18, 1e30)
ax.set_ylim(-1, 1)
ax.axhline(0, color="black", lw=1)

# shaded regions (m^-3); lightly < 1e16 cm^-3 = 1e22 m^-3, heavily > 1e18 cm^-3 = 1e24 m^-3
ax.axvspan(1e20, 1e22, ymin=0.35, ymax=0.65, color="#90cdf4", alpha=0.6,
           label=r"Typical doped Ge ($10^{20}$–$10^{22}$ m$^{-3}$)")
ax.axvspan(1e24, 1e30, ymin=0.35, ymax=0.65, color="#e2e8f0", alpha=0.8,
           label=r"Heavily doped ($>10^{24}$ m$^{-3}$)")

refs = [(2e19, "Intrinsic Ge\n" r"$2\times10^{19}$", 0.45),
        (4.42e28, "Ge atoms\n" r"$4.4\times10^{28}$", -0.45),
        (8.5e28, "Copper\n" r"$8.5\times10^{28}$", 0.45)]
for x, lab, y in refs:
    ax.plot(x, 0, "s", color="#4a5568", ms=7, zorder=3)
    ax.annotate(lab, (x, 0), (x, y), ha="center",
                va="bottom" if y > 0 else "top", fontsize=9,
                arrowprops=dict(arrowstyle="-", color="#4a5568", lw=0.6))

ax.errorbar(n_meas, 0, xerr=dn, fmt="o", color="#c53030", ms=8,
            capsize=4, zorder=4)
ax.annotate("Measured (Ge wafer)\n" r"$4.6\times10^{20}$", (n_meas, 0), (n_meas, -0.45),
            ha="center", va="top", fontsize=9, color="#c53030",
            arrowprops=dict(arrowstyle="-", color="#c53030", lw=0.6))

ax.set_yticks([])
for s in ("left", "right", "top"):
    ax.spines[s].set_visible(False)
ax.set_xlabel(r"Carrier density $n$ (m$^{-3}$)")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.32), ncol=2,
          frameon=False, fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "hall_density_scale.png"), dpi=200,
            bbox_inches="tight")
plt.close(fig)

print("Saved: hall_data_table.png, hall_voltage_vs_current.png, hall_residuals.png, hall_density_scale.png")
print("Folder:", OUT)