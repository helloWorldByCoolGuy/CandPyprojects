"""
Spectrum of Hydrogen — experimental analysis (Q6–Q9).
Raw spectrometer angles -> wavelengths -> 1/λ vs (1/4 - 1/n²) -> R_H.
Includes: weighted fits, max/min gradient lines, per-line R_H,
Monte Carlo distribution of R_H, air and reduced-mass corrections.
"""

import os
import numpy as np
import matplotlib.pyplot as plt

# Save images in the same folder as this .py file (works no matter where VS Code runs it from)
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

rng = np.random.default_rng(42)

# ---------------- Raw data ----------------
a       = 1 / 600e3          # grating spacing (m), 600 lines/mm
phi0    = 230.0              # zero-order reading (deg)
dtheta  = 0.2                # angle uncertainty (deg) — see notes below
R_acc   = 1.097373e7         # accepted R_H (m^-1)

lines = [  # colour, upper level n, phi(+1), phi(-1), accepted λ (nm, in air)
    ("Red (Hα)",        3, 253.4, 206.8, 656.28),
    ("Blue (Hβ)", 4, 247.3, 213.3, 486.13),
    ("Violet (Hγ)",     5, 245.5, 215.0, 434.05),
]

names  = [l[0] for l in lines]
n_up   = np.array([l[1] for l in lines])
phi_p  = np.array([l[2] for l in lines])
phi_m  = np.array([l[3] for l in lines])
lam_acc = np.array([l[4] for l in lines]) * 1e-9

def wavelengths(phi_p, phi_m, phi0):
    """Average λ from both orders, as the lab manual specifies."""
    th_p = np.radians(phi_p - phi0)
    th_m = np.radians(phi0 - phi_m)
    return (a*np.sin(th_p) + a*np.sin(th_m)) / 2, np.degrees(th_p), np.degrees(th_m)

lam, th_p, th_m = wavelengths(phi_p, phi_m, phi0)
th_avg = (th_p + th_m) / 2

# Uncertainty in λ (prelab Q4) and in 1/λ (prelab Q5)
dth_rad = np.radians(dtheta)
dlam    = lam * dth_rad * np.sqrt((a/lam)**2 - 1)
y       = 1 / lam
dy      = dlam / lam**2
x       = 1/2**2 - 1/n_up**2

# ---------------- Q6 table ----------------
print("=" * 100)
print("Q6 — WAVELENGTHS")
print("=" * 100)
print(f"{'Line':<17}{'θ+1':>7}{'θ-1':>7}{'diff':>6}{'λ (nm)':>16}{'accepted':>10}"
      f"{'% diff':>8}{'1/λ (10⁶ m⁻¹)':>20}{'x':>8}")
for i in range(3):
    print(f"{names[i]:<17}{th_p[i]:>7.1f}{th_m[i]:>7.1f}{th_p[i]-th_m[i]:>6.1f}"
          f"{lam[i]*1e9:>9.1f} ± {dlam[i]*1e9:<4.1f}{lam_acc[i]*1e9:>10.2f}"
          f"{100*(lam[i]-lam_acc[i])/lam_acc[i]:>8.2f}"
          f"{y[i]/1e6:>12.4f} ± {dy[i]/1e6:.4f}{x[i]:>8.4f}")

# Where the zero order "really" is, judged from each pair of readings
phi0_implied = (phi_p + phi_m) / 2
print(f"\nImplied zero order from each pair: {np.round(phi0_implied, 2)}  "
      f"(mean {phi0_implied.mean():.2f}°, you measured {phi0}°)")

# ---------------- Fits ----------------
w = 1 / dy**2

def fit_origin(x, y, w):
    R  = np.sum(w*x*y) / np.sum(w*x**2)
    dR = 1 / np.sqrt(np.sum(w*x**2))
    return R, dR

def fit_line(x, y, w):
    S, Sx, Sy = w.sum(), (w*x).sum(), (w*y).sum()
    Sxx, Sxy  = (w*x*x).sum(), (w*x*y).sum()
    D = S*Sxx - Sx**2
    m = (S*Sxy - Sx*Sy) / D
    c = (Sxx*Sy - Sx*Sxy) / D
    return m, c, np.sqrt(S/D), np.sqrt(Sxx/D)

R_A, dR_A = fit_origin(x, y, w)
R_B, c_B, dR_B, dc_B = fit_line(x, y, w)
R_each  = y / x
dR_each = dy / x

# Max/min gradient lines (what the lab manual asks for):
# steepest and shallowest lines through origin that still touch every error bar
R_max = np.min((y + dy) / x)
R_min = np.max((y - dy) / x)

# Residuals
chi2 = np.sum(((y - R_A*x) / dy)**2)

print("\n" + "=" * 100)
print("Q7/Q8 — RYDBERG CONSTANT")
print("=" * 100)
print(f"Fit A (through origin, weighted):  R_H = {R_A:.4e} ± {dR_A:.2e} m⁻¹")
print(f"Fit B (free intercept, weighted):  R_H = {R_B:.4e} ± {dR_B:.2e} m⁻¹,"
      f"  intercept c = {c_B:.3e} ± {dc_B:.2e} m⁻¹  ({c_B/dc_B:+.1f}σ from 0)")
print(f"Max/min gradient lines:            R_min = {R_min:.4e}, R_max = {R_max:.4e}"
      f"  → R_H = {(R_max+R_min)/2:.4e} ± {(R_max-R_min)/2:.2e}")
print("Per-line estimates R = (1/λ)/x:")
for i in range(3):
    print(f"   {names[i]:<17} {R_each[i]:.4e} ± {dR_each[i]:.2e}")
print(f"χ² for Fit A = {chi2:.2f} with 2 degrees of freedom")
print(f"\nAccepted R_H = {R_acc:.6e} m⁻¹")
print(f"Fit A differs by {100*(R_A-R_acc)/R_acc:+.2f}%  = {(R_A-R_acc)/dR_A:+.2f}σ")

# ---------------- Corrections (Q9) ----------------
n_air = 1.000293
R_vac = R_A / n_air                      # λ_vac = n_air λ_air -> 1/λ smaller
m_ratio = 9.1093837e-31 / 1.67262192e-27
R_inf = 1.0973731568e7
R_H_theory = R_inf / (1 + m_ratio)
print("\n" + "=" * 100)
print("CORRECTIONS")
print("=" * 100)
print(f"Air → vacuum (n = {n_air}):  R_H = {R_vac:.4e}   shift {100*(R_vac-R_A)/R_A:+.3f}%")
print(f"Reduced mass: R_∞ = {R_inf:.6e},  R_H = R_∞/(1+m_e/m_p) = {R_H_theory:.6e}"
      f"   shift {100*(R_H_theory-R_inf)/R_inf:+.3f}%")
print(f"Your measurement uncertainty: ±{100*dR_A/R_A:.2f}%")

# ---------------- Monte Carlo distribution ----------------
# Re-run the whole experiment N times in the computer. Each reading
# (phi+, phi-, phi0) gets random noise; we recompute λ, refit, store R_H.
N = 100_000
def simulate(noise):
    pp = phi_p[None, :] + noise(N, 3)
    pm = phi_m[None, :] + noise(N, 3)
    p0 = phi0 + noise(N, 1)
    lam_s, _, _ = wavelengths(pp, pm, p0)
    ys = 1 / lam_s
    return np.sum(w*x*ys, axis=1) / np.sum(w*x**2)   # same weighted origin fit

gauss   = lambda *s: rng.normal(0, dtheta, s)
uniform = lambda *s: rng.uniform(-0.05, 0.05, s)       # pure vernier rounding, ±half of 0.1°
R_mc_g  = simulate(gauss)
R_mc_u  = simulate(uniform)

def skew(v): return np.mean((v-v.mean())**3) / v.std()**3
def kurt(v): return np.mean((v-v.mean())**4) / v.std()**4 - 3

print("\n" + "=" * 100)
print("MONTE CARLO (100,000 simulated experiments)")
print("=" * 100)
for lab, r in [("Gaussian, σ = 0.2°", R_mc_g), ("Uniform ±0.05° (vernier only)", R_mc_u)]:
    lo, hi = np.percentile(r, [16, 84])
    print(f"{lab:<32} mean {r.mean():.4e}  std {r.std():.2e}  68% [{lo:.4e}, {hi:.4e}]"
          f"  skew {skew(r):+.3f}  excess kurtosis {kurt(r):+.3f}")
print(f"Fraction of Gaussian-noise runs that reach the accepted value: "
      f"{np.mean(R_mc_g >= R_acc)*100:.1f}%")

# ---------------- Figures ----------------
INK, MUTED, GRID = "#1f1f1f", "#6b6b6b", "#e6e6e6"
DATA, FIT, ACC   = "#2a6fdb", "#1f1f1f", "#c0392b"
plt.rcParams.update({"axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "font.size": 10})

# Figure 1: main plot + residuals
fig, ax = plt.subplots(figsize=(8, 6))
xx = np.linspace(0, 0.23, 100)
ax.plot(xx, R_A*xx/1e6, color=FIT, lw=1.6, label=f"Weighted fit through origin: R_H = {R_A/1e7:.4f}×10⁷ m⁻¹")
ax.plot(xx, R_max*xx/1e6, color=MUTED, lw=1, ls="--", label="Max / min gradient lines")
ax.plot(xx, R_min*xx/1e6, color=MUTED, lw=1, ls="--")
ax.plot(xx, R_acc*xx/1e6, color=ACC, lw=1, ls=":", label=f"Accepted: {R_acc/1e7:.4f}×10⁷ m⁻¹")
ax.errorbar(x, y/1e6, yerr=dy/1e6, fmt="o", ms=7, color=DATA, ecolor=DATA,
            elinewidth=1.5, capsize=4, label="Measured (error bars = Δ(1/λ))", zorder=5)
for i in range(3):
    ax.annotate(names[i], (x[i], y[i]/1e6), xytext=(-12, 10), textcoords="offset points",
                ha="right", fontsize=9, color=INK)
ax.set_ylabel("1/λ  (10⁶ m⁻¹)")
ax.set_title("Balmer lines: 1/λ vs (1/2² − 1/n²)", color=INK, loc="left")
ax.set_xlim(0, 0.23); ax.set_ylim(0, 2.6)
ax.grid(color=GRID, lw=0.8); ax.legend(frameon=False, fontsize=9, loc="upper left")
ax.set_xlabel("1/2² − 1/n²")
plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR, "rydberg_fit.png"), dpi=160); plt.close()

# Figure 1b: residuals (separate image)
fig, axr = plt.subplots(figsize=(8, 3.6))

# Residuals in units of each point's error bar, measured from TWO lines:
#   vs your fit      -> is a straight line through the origin a good description?
#   vs accepted R_H  -> is the theoretical value consistent with your data?
res_fit = (y - R_A*x) / dy
res_acc = (y - R_acc*x) / dy
chi2_acc = np.sum(res_acc**2)
off = 0.003
axr.axhspan(-1, 1, color="#f0f0f0", zorder=0)
axr.axhline(0, color=FIT, lw=1)
axr.plot(x - off, res_fit, "o", color=DATA, ms=7, label="from your fit")
axr.plot(x + off, res_acc, "o", mfc="white", mec=ACC, mew=1.6, ms=7, label="from accepted R_H")
for i in range(3):
    axr.vlines(x[i] - off, 0, res_fit[i], color=DATA, lw=1.2)
    axr.vlines(x[i] + off, 0, res_acc[i], color=ACC, lw=1.2)
    axr.text(x[i], -2.2, names[i], ha="center", fontsize=8, color=MUTED)
axr.set_ylabel("Residual (σ)"); axr.set_xlabel("1/2² − 1/n²  (zoomed to the data)")
axr.set_xlim(0.125, 0.225); axr.set_ylim(-2.5, 2.0); axr.grid(color=GRID, lw=0.8)
axr.legend(frameon=False, fontsize=8, loc="upper left", ncol=2)
axr.text(0.995, 0.95, "shaded band = ±1σ", transform=axr.transAxes, ha="right", va="top",
         fontsize=8, color=MUTED)
print("\nResiduals vs fit (σ):     ", np.round(res_fit, 2))
print("Residuals vs accepted (σ):", np.round(res_acc, 2),
      f"  χ² = {chi2_acc:.2f} for 3 points, 0 fitted parameters")
axr.set_title("Residuals: distance of each point from the fitted and accepted lines", loc="left", fontsize=10, color=INK)
plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR, "rydberg_residuals.png"), dpi=160); plt.close()

# Figure 2: Monte Carlo distributions
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for axm, r, ttl in [(axes[0], R_mc_g, "Gaussian noise, σ = 0.2° on every reading"),
                    (axes[1], R_mc_u, "Uniform noise, ±0.05° (vernier rounding only)")]:
    axm.hist(r/1e7, bins=120, density=True, color=DATA, alpha=0.75, edgecolor="white", lw=0.3)
    g = np.linspace(r.min(), r.max(), 400)
    axm.plot(g/1e7, 1e7*np.exp(-(g-r.mean())**2/(2*r.var()))/(r.std()*np.sqrt(2*np.pi)),
             color=FIT, lw=1.4, label="Gaussian with same mean & σ")
    axm.axvline(R_acc/1e7, color=ACC, ls=":", lw=1.5, label="Accepted R_H")
    axm.axvline(R_A/1e7, color=FIT, ls="--", lw=1, label="Your fit")
    axm.set_title(ttl, fontsize=10, color=INK, loc="left")
    axm.set_xlabel("R_H  (10⁷ m⁻¹)"); axm.set_yticks([])
    axm.text(0.02, 0.95, f"skew {skew(r):+.3f}\nexcess kurt. {kurt(r):+.3f}",
             transform=axm.transAxes, va="top", fontsize=9, color=MUTED)
axes[0].legend(frameon=False, fontsize=8, loc="upper right")
plt.suptitle("Monte Carlo: R_H from 100,000 simulated repeats of your experiment",
             x=0.01, ha="left", color=INK)
plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR, "rydberg_montecarlo.png"), dpi=160); plt.close()
print(f"\nSaved rydberg_fit.png, rydberg_residuals.png and rydberg_montecarlo.png in: {OUT_DIR}")

# ---------------- Uncertainty budget (Q9) ----------------
# How big is each effect, as a % of R_H? Compared on one log axis because they
# span three orders of magnitude.
R_maxmin  = (R_max + R_min) / 2
dR_maxmin = (R_max - R_min) / 2
delta0    = np.radians(phi0_implied.mean() - phi0)   # zero-order offset (rad)
budget = [
    ("Line-centre judgement (Δθ = 0.2°)",      100 * dR_maxmin / R_maxmin, "random"),
    ("Vernier resolution only (±0.05°)",        100 * R_mc_u.std() / R_mc_u.mean(), "random"),
    ("Reduced mass (R∞ → R_H)",                 100 * (R_inf - R_H_theory) / R_inf, "correction"),
    ("Air refractive index (n = 1.0003)",       100 * (1 - 1/1.0003), "correction"),
    ("Zero-order offset after ± averaging",     100 * (1 - np.cos(delta0)), "systematic"),
]
gap = 100 * abs(R_maxmin - R_acc) / R_acc

# What second-order (m = 2) diffraction would do to Δλ/λ for each line
print("\n" + "=" * 100)
print("UNCERTAINTY BUDGET AND IMPROVEMENTS")
print("=" * 100)
for name, v, kind in budget:
    print(f"  {name:<40} {v:9.4f} %   ({kind})")
print(f"  {'Observed gap from accepted value':<40} {gap:9.4f} %")
print("\nFactor √((a/mλ)² − 1) that multiplies Δθ in Δλ/λ:")
for i in range(3):
    f1 = np.sqrt((a/lam[i])**2 - 1)
    s2 = 2*lam[i]/a
    f2 = np.sqrt((a/(2*lam[i]))**2 - 1)
    print(f"  {names[i]:<17} m=1: {f1:.2f}   m=2: {f2:.2f} (θ = {np.degrees(np.arcsin(s2)):.1f}°)"
          f"   → {f1/f2:.1f}× smaller Δλ/λ")
print(f"Grating spacing: R_H ∝ 1/a, so a {gap:.2f}% error in a alone would explain the whole gap.")

colours_kind = {"random": DATA, "correction": "#8c8c8c", "systematic": "#e0a030"}
fig, ax = plt.subplots(figsize=(8.5, 3.6))
yb = np.arange(len(budget))[::-1]
for yy, (name, v, kind) in zip(yb, budget):
    ax.barh(yy, v, color=colours_kind[kind], height=0.55)
    ax.text(v * 1.15, yy, f"{v:.2g} %", va="center", fontsize=9, color=INK)
ax.axvline(gap, color=ACC, ls=":", lw=1.5)
ax.text(gap * 0.92, yb[0] + 0.5, f"observed gap from accepted value ({gap:.2f} %)",
        fontsize=8, color=ACC, va="bottom", ha="right")
ax.set_ylim(-0.6, len(budget) - 0.1)
ax.set_xscale("log"); ax.set_xlim(1e-4, 5)
ax.set_yticks(yb, [b[0] for b in budget], fontsize=9)
ax.set_xlabel("Size of effect on R_H  (% , log scale)")
ax.set_title("Uncertainty budget: line-centre judgement dominates; everything else is ≥10× smaller",
             loc="left", fontsize=10, color=INK)
ax.grid(axis="x", color=GRID, lw=0.8, which="major")
ax.spines[["top", "right"]].set_visible(False)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=DATA, label="random"), Patch(color="#e0a030", label="systematic"),
                   Patch(color="#8c8c8c", label="known correction")],
          frameon=False, fontsize=8, loc="lower right")
plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR, "uncertainty_budget.png"), dpi=160); plt.close()
print(f"Saved uncertainty_budget.png in: {OUT_DIR}")
