"""
Band Gap Experiment Analysis (v2)
---------------------------------
- Linearised equation (3) → Eg from y-intercept
- Varshni equation comparison
- dV/dT using independent Eg values (not fitted)
- Uncertainty analysis with standard error
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ── Constants ──────────────────────────────────────────────
k_B = 1.381e-23      # Boltzmann constant (J/K)
e   = 1.602e-19      # electron charge (C)

# ── Varshni parameters ────────────────────────────────────
# E_g(T) = E_g(0) - α T² / (T + β)
varshni = {
    'Si': {'Eg0': 1.166, 'alpha': 4.73e-4, 'beta': 636},
    'Ge': {'Eg0': 0.7437, 'alpha': 4.77e-4, 'beta': 235},
}

def varshni_Eg(T, params):
    """Band gap at temperature T using Varshni equation."""
    return params['Eg0'] - params['alpha'] * T**2 / (T + params['beta'])

# ── Read data ──────────────────────────────────────────────
filepath = r"D:\4th Sem\Advanced Mathematics and Physics\Physics Lab\experiment data.xlsx"
df = pd.read_excel(filepath, sheet_name="band gap", header=0)

T_ge = df.iloc[2:17, 2].astype(float).values
V_ge = df.iloc[2:17, 3].astype(float).values
T_si = df.iloc[2:17, 8].astype(float).values
V_si = df.iloc[2:17, 9].astype(float).values

# ── Compute Y-axis: equation (3) LHS ──────────────────────
def compute_Y(V, T):
    return V + (3 * k_B * T / e) * np.log(T)

Y_ge = compute_Y(V_ge, T_ge)
Y_si = compute_Y(V_si, T_si)

# ── Linear fit with uncertainty ───────────────────────────
def linear_fit_with_error(x, y):
    """Returns slope, intercept, and their standard errors."""
    n = len(x)
    coeffs, cov = np.polyfit(x, y, 1, cov=True)
    m, c = coeffs
    sigma_m = np.sqrt(cov[0, 0])
    sigma_c = np.sqrt(cov[1, 1])

    # Residual standard deviation
    y_fit = m * x + c
    residuals = y - y_fit
    sigma_res = np.sqrt(np.sum(residuals**2) / (n - 2))

    return m, c, sigma_m, sigma_c, sigma_res

m_ge, c_ge, sm_ge, sc_ge, sr_ge = linear_fit_with_error(T_ge, Y_ge)
m_si, c_si, sm_si, sc_si, sr_si = linear_fit_with_error(T_si, Y_si)

# ── Varshni Eg at key temperatures ────────────────────────
T_points = [0, 298.15, 368.15]

print("="*60)
print("VARSHNI BAND GAP vs TEMPERATURE")
print("="*60)
print(f"\n{'T (K)':<10} {'Si Eg (eV)':<14} {'Ge Eg (eV)':<14}")
print("-"*38)
for T in T_points:
    Eg_si = varshni_Eg(T, varshni['Si'])
    Eg_ge = varshni_Eg(T, varshni['Ge'])
    print(f"{T:<10.1f} {Eg_si:<14.4f} {Eg_ge:<14.4f}")

# ── Main results ──────────────────────────────────────────
print(f"\n{'='*60}")
print("BAND GAP FROM LINEARISED FIT")
print("="*60)

print(f"\nGERMANIUM")
print(f"  Slope        m  = ({m_ge:.2e} ± {sm_ge:.2e}) V/K")
print(f"  Intercept    Eg = ({c_ge:.4f} ± {sc_ge:.4f}) eV")
print(f"  Varshni Eg(0)   = {varshni['Ge']['Eg0']:.4f} eV")
print(f"  Accepted (300K) = 0.67 eV")
print(f"  Residual σ      = {sr_ge:.6f} V")

print(f"\nSILICON")
print(f"  Slope        m  = ({m_si:.2e} ± {sm_si:.2e}) V/K")
print(f"  Intercept    Eg = ({c_si:.4f} ± {sc_si:.4f}) eV")
print(f"  Varshni Eg(0)   = {varshni['Si']['Eg0']:.4f} eV")
print(f"  Accepted (300K) = 1.12 eV")
print(f"  Residual σ      = {sr_si:.6f} V")

# ── dV/dT comparison (independent Eg, not fitted) ─────────
# Theory: dV/dT = -(Eg/e - V_avg) / T_avg - 3k/e
# Using Varshni Eg at mean temperature (independent values)
T_avg = np.mean(T_si)  # ~333 K, same for both

Eg_si_varshni = varshni_Eg(T_avg, varshni['Si'])
Eg_ge_varshni = varshni_Eg(T_avg, varshni['Ge'])

V_avg_si = np.mean(V_si)
V_avg_ge = np.mean(V_ge)

dVdT_theory_si = -(Eg_si_varshni / e * e - V_avg_si) / T_avg - 3 * k_B / e
dVdT_theory_ge = -(Eg_ge_varshni / e * e - V_avg_ge) / T_avg - 3 * k_B / e

# Measured: slope of straight-line fit of V vs T
mV_si, _ = np.polyfit(T_si, V_si, 1)
mV_ge, _ = np.polyfit(T_ge, V_ge, 1)

print(f"\n{'='*60}")
print("dV/dT COMPARISON")
print("="*60)
print(f"Using independent Varshni Eg at T_avg = {T_avg:.1f} K")
print(f"\n{'':>20} {'Theory (mV/K)':<16} {'Measured (mV/K)':<16}")
print("-"*52)
print(f"{'Si':>20} {dVdT_theory_si*1000:<16.2f} {mV_si*1000:<16.2f}")
print(f"{'Ge':>20} {dVdT_theory_ge*1000:<16.2f} {mV_ge*1000:<16.2f}")

# ── eV/kT validity check ─────────────────────────────────
print(f"\n{'='*60}")
print("eV/kT VALIDITY CHECK (need >> 1, at least > 4)")
print("="*60)
print(f"\n{'T (K)':<10} {'Si eV/kT':<14} {'Ge eV/kT':<14} {'Ge valid?':<10}")
print("-"*48)
for i in range(len(T_ge)):
    evkt_si = e * V_si[i] / (k_B * T_si[i])
    evkt_ge = e * V_ge[i] / (k_B * T_ge[i])
    valid = "✓" if evkt_ge > 4 else "✗"
    print(f"{T_ge[i]:<10.1f} {evkt_si:<14.1f} {evkt_ge:<14.1f} {valid:<10}")

# ── Plot ──────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

T_fit = np.linspace(0, 380, 200)

# --- Left panel: Y vs T with fit ---
ax1.scatter(T_ge, Y_ge, color='#E24B4A', s=40, zorder=3, label='Ge data')
ax1.plot(T_fit, m_ge * T_fit + c_ge, color='#E24B4A', linestyle='--',
         label=f'Ge fit: $E_g$ = {c_ge:.3f} ± {sc_ge:.3f} eV')

ax1.scatter(T_si, Y_si, color='#378ADD', s=40, zorder=3, label='Si data')
ax1.plot(T_fit, m_si * T_fit + c_si, color='#378ADD', linestyle='--',
         label=f'Si fit: $E_g$ = {c_si:.3f} ± {sc_si:.3f} eV')

# Mark the intercepts
ax1.plot(0, c_ge, 'o', color='#E24B4A', markersize=8, zorder=4)
ax1.plot(0, c_si, 'o', color='#378ADD', markersize=8, zorder=4)

ax1.set_xlabel('Temperature $T$ (K)', fontsize=12)
ax1.set_ylabel(r'$V + \frac{3kT}{e}\ln T$  (V)', fontsize=12)
ax1.set_title('Band Gap: Linearised Diode Equation', fontsize=13)
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(-10, 390)

# --- Right panel: Varshni Eg vs T ---
T_var = np.linspace(0, 400, 300)
Eg_si_var = [varshni_Eg(T, varshni['Si']) for T in T_var]
Eg_ge_var = [varshni_Eg(T, varshni['Ge']) for T in T_var]

ax2.plot(T_var, Eg_si_var, color='#378ADD', linewidth=2, label='Si (Varshni)')
ax2.plot(T_var, Eg_ge_var, color='#E24B4A', linewidth=2, label='Ge (Varshni)')

# Mark fitted Eg(0) values
ax2.errorbar(0, c_si, yerr=sc_si, fmt='s', color='#378ADD',
             markersize=8, capsize=4, label=f'Si measured: {c_si:.3f} eV')
ax2.errorbar(0, c_ge, yerr=sc_ge, fmt='s', color='#E24B4A',
             markersize=8, capsize=4, label=f'Ge measured: {c_ge:.3f} eV')

# Mark accepted 300K values
ax2.axhline(y=1.12, color='#378ADD', linestyle=':', alpha=0.5)
ax2.axhline(y=0.67, color='#E24B4A', linestyle=':', alpha=0.5)
ax2.text(310, 1.13, 'Si accepted (300K)', fontsize=8, color='#378ADD')
ax2.text(310, 0.68, 'Ge accepted (300K)', fontsize=8, color='#E24B4A')

ax2.set_xlabel('Temperature $T$ (K)', fontsize=12)
ax2.set_ylabel('$E_g$ (eV)', fontsize=12)
ax2.set_title('Varshni Band Gap vs Temperature', fontsize=13)
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('bandgap_analysis.png', dpi=150)
plt.show()

print("\nPlot saved as bandgap_analysis.png")