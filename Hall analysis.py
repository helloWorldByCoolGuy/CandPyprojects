"""
Hall Effect - Analysis (numbers and printout only)
--------------------------------------------------
Model:  phi_H = (B / (n e T)) * I + c
        slope m = B / (n e T)   ->   n = B / (e T m)

Data: lab  run, 1-25 mA in 1 mA steps, Hall voltage read to 0.1 mV.
"""

import numpy as np

# ── Constants ──────────────────────────────────────────────
e = 1.602e-19          # elementary charge (C)
B = 0.3435             # magnetic field on module (T)
T_wafer = 1.000e-3     # wafer thickness (m)
N_Ge = 4.42e28         # Ge atomic density (m^-3), Kittel
n_i = 2e19             # intrinsic Ge carrier density at 300 K (m^-3)

delta_B = 0.001        # +/- 1 mT (assumed, gauss meter)
delta_T = 0.1e-3       # +/- 0.1 mm (assumed, last stated digit; no tolerance given)

# ── Data ───────────────────────────────────────────────────
I_mA = np.arange(1, 26, dtype=float)
phi_mV = np.array([2.5, 7.3, 13.6, 12.2, 18.8, 24.7, 27.8, 29.0, 32.0, 36.7,
                   45.3, 49.6, 50.1, 57.7, 60.9, 66.0, 70.0, 76.1, 78.4, 86.8,
                   91.9, 97.0, 102.9, 112.1, 115.2])

I = I_mA * 1e-3        # A
phi = phi_mV * 1e-3    # V
N = len(I)
dof = N - 2            # two fitted parameters: slope and intercept

# ── Linear least-squares fit ───────────────────────────────
(m, c), cov = np.polyfit(I, phi, 1, cov=True)
sigma_m = np.sqrt(cov[0, 0])
sigma_c = np.sqrt(cov[1, 1])

phi_fit = m * I + c
res = phi - phi_fit
sigma_res = np.sqrt(np.sum(res**2) / dof)   # scatter of points about the line
res_norm = res / sigma_res                  # residuals in units of sigma

R2 = 1 - np.sum(res**2) / np.sum((phi - phi.mean())**2)

# Fit forced through the origin (check: does the offset matter?)
m0 = np.sum(I * phi) / np.sum(I**2)

# ── Carrier density and uncertainty ────────────────────────
n = B / (e * T_wafer * m)
f_m = sigma_m / m
f_B = delta_B / B
f_T = delta_T / T_wafer
f_n = np.sqrt(f_m**2 + f_B**2 + f_T**2)
delta_n = n * f_n
n_rand_only = n * f_m   # random part only (systematic T, B excluded)

# ── Residual pattern check ─────────────────────────────────
signs = np.sign(res)
runs = 1 + np.sum(signs[1:] != signs[:-1])
n_pos, n_neg = np.sum(signs > 0), np.sum(signs < 0)
exp_runs = 1 + 2 * n_pos * n_neg / N

# ── Printout ───────────────────────────────────────────────
line = "=" * 60
print(line); print("HALL EFFECT ANALYSIS  ( N = %d)" % N); print(line)

print("\nLinear fit  phi_H = m I + c")
print(f"  m          = {m:.4f} +/- {sigma_m:.4f} V/A   ({f_m*100:.1f}%)")
print(f"  c          = {c*1e3:.2f} +/- {sigma_c*1e3:.2f} mV   ({abs(c)/sigma_c:.1f} sigma from zero)")
print(f"  R^2        = {R2:.4f}")
print(f"  sigma_res  = {sigma_res*1e3:.2f} mV   (dof = {dof})")
print(f"  slope through origin m0 = {m0:.4f} V/A  (diff from m: {(m0-m)/m*100:+.1f}%)")

print("\nCarrier density")
print(f"  n = {n:.3e} +/- {delta_n:.2e} m^-3")
print(f"  random (slope) only: +/- {n_rand_only:.1e} m^-3")

print("\nUncertainty budget (fractional)")
print(f"  slope (random)        {f_m*100:5.1f}%")
print(f"  thickness (systematic){f_T*100:5.1f}%")
print(f"  B field (systematic)  {f_B*100:5.1f}%")
print(f"  combined              {f_n*100:5.1f}%")

print("\nResidual pattern")
print(f"  + residuals: {n_pos},  - residuals: {n_neg}")
print(f"  sign runs: {runs}  (random expectation ~{exp_runs:.1f})")
print(f"  largest |residual| = {np.max(np.abs(res_norm)):.1f} sigma at I = {I_mA[np.argmax(np.abs(res_norm))]:.0f} mA")

print("\nLiterature comparison")
print(f"  n / n_i          ~ {n/n_i:.0f}")
print(f"  n in cm^-3       = {n*1e-6:.1e}")
print(f"  minority n_i^2/n = {n_i**2/n:.1e} m^-3  ({n_i**2/n**2*100:.3f}% of n)")
print(f"  1 dopant per     ~ {N_Ge/n:.1e} Ge atoms")

print("\nPer-point table")
print(f"  {'I(mA)':>6} {'phi(mV)':>8} {'fit(mV)':>8} {'res(mV)':>8} {'res/sig':>8}")
for a, b, f, r, z in zip(I_mA, phi_mV, phi_fit*1e3, res*1e3, res_norm):
    print(f"  {a:6.0f} {b:8.1f} {f:8.2f} {r:8.2f} {z:8.2f}")