import os
import re
import json
import time
import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq

# ============================================================
# ------------------------- PATHS ---------------------------
# ============================================================
# Основная папка с данными сплавов
BASE_PATH = "/Users/osintsevkirill/Yandex.Disk.localized/Science/Postdoc_project/Fe-Cr-Ni-SRO-End-Quenching/02_Analytical_NIMM"
# Папка для сохранения результатов
OUTPUT_DIR = os.path.join(BASE_PATH, "strengthening")
# Файл с данными Random Solid Solution
EXCEL_FILE_NAME = "/Users/osintsevkirill/Yandex.Disk.localized/Science/Postdoc_project/Article/FeNiCr_30.09.2025/3.strength/combined_T_293.xlsx"
# Таблица коэффициентов (должна лежать по этому пути или укажите точный)
COEFF_TABLE_PATH = "/Users/osintsevkirill/Yandex.Disk.localized/Science/Postdoc_project/Article/FeNiCr_30.09.2025/coeffs_vs_w_sigma_1.5b_and_d_15b.txt"

# Константы
TAYLOR_FACTOR = 3.06  # Перевод из монокристалла в поликристалл (FCC)
KB = 8.617333262e-5
EPS_DOT_0 = 1e3
T_RT = 293.0
EV_PER_A3_TO_MPA = 160217.6
PAIRS = [('Fe', 'Ni'), ('Fe', 'Cr'), ('Ni', 'Cr')]

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# ============================================================
# --------------- Nag & Curtin numeric core ------------------
# ============================================================
def load_coeff_table(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Coefficient table not found at {path}")
    data = np.loadtxt(path)
    w = data[:, 0]
    splines = {}
    names = ['A', 'B12', 'C6', 'D24', 'E12']
    for i, name in enumerate(names):
        splines[name] = CubicSpline(w, data[:, i + 1])
    return splines, w.min(), w.max()

def S_of_w(w, splines, betas):
    b0, b1, b2, b3, b4 = betas
    return (b0 * splines['A'](w) + b1 * splines['B12'](w) + b2 * splines['C6'](w)
            + b3 * splines['D24'](w) + b4 * splines['E12'](w))

def dS_dw(w, splines, betas):
    b0, b1, b2, b3, b4 = betas
    return (b0 * splines['A'](w, 1) + b1 * splines['B12'](w, 1) + b2 * splines['C6'](w, 1)
            + b3 * splines['D24'](w, 1) + b4 * splines['E12'](w, 1))

def find_wc(splines, betas, w_min, w_max, w_scan):
    def g(w):
        return dS_dw(w, splines, betas) - S_of_w(w, splines, betas) / w
    g_vals = g(w_scan)
    roots = []
    for i in range(len(w_scan) - 1):
        if g_vals[i] * g_vals[i + 1] < 0:
            try:
                roots.append(brentq(g, w_scan[i], w_scan[i + 1]))
            except: pass
    return roots[0] if roots else np.nan

def parse_misfit_volumes(file_path):
    comp, misfits, avg_vol = {}, {}, None
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if any(x in line for x in ["Fe:", "Ni:", "Cr:"]):
                parts = line.split(":")
                comp[parts[0].strip()] = float(parts[1])
            if "Average volume" in line:
                avg_vol = float(line.split(":")[1])
            if "Element" in line:
                for j in range(i + 1, i + 4):
                    parts = lines[j].split()
                    misfits[parts[0]] = float(parts[1])
    return comp, misfits, avg_vol

def parse_epi(file_path):
    veff = {}
    with open(file_path, 'r') as f:
        f.readline()
        for line in f:
            parts = line.split()
            if len(parts) < 7 or parts[1] != "1st" or parts[2] != "Success": continue
            els = re.findall('[A-Z][a-z]?', parts[0])
            veff[''.join(sorted(els))] = float(parts[6])
    return veff

def compute_tau_A_fcc_1stNN(comp, alpha_1st, veff, a_lat):
    b = a_lat / np.sqrt(2)
    total = 0.0
    for p, q in PAIRS:
        key = ''.join(sorted([p, q]))
        a_key = f"alpha_{p}{q}" if f"alpha_{p}{q}" in alpha_1st else f"alpha_{q}{p}"
        if a_key in alpha_1st and key in veff:
            total += 2 * comp[p] * comp[q] * alpha_1st[a_key] * veff[key]
    tau_A_eV_A3 = -(2.0 / (np.sqrt(3) * b ** 3)) * total
    return tau_A_eV_A3 * EV_PER_A3_TO_MPA

# ============================================================
# ---------------- Data Loading & Discovery ------------------
# ============================================================
def load_excel_baseline(excel_path):
    df = pd.read_excel(excel_path, engine='openpyxl')
    df['Alloy'] = 'Fe' + df['Fe'].astype(int).astype(str) + 'Ni' + df['Ni'].astype(int).astype(str) + 'Cr' + df['Cr'].astype(int).astype(str)
    return df.set_index('Alloy').to_dict('index')

def discover_alloys(base_path, excel_baseline):
    alloys = []
    for entry in sorted(os.listdir(base_path)):
        if entry.startswith("Fe") and entry in excel_baseline:
            alloys.append(entry)
    return alloys

# ============================================================
# ----------------------- Main Run ---------------------------
# ============================================================
def run_calculation():
    splines, w_min, w_max = load_coeff_table(COEFF_TABLE_PATH)
    excel_baseline = load_excel_baseline(EXCEL_FILE_NAME)
    alloys = discover_alloys(BASE_PATH, excel_baseline)
    w_scan = np.linspace(max(w_min, 1e-3), w_max, 2000)
    
    results = []
    print(f"Found {len(alloys)} alloys. Starting calculation...")

    for alloy in alloys:
        alloy_dir = os.path.join(BASE_PATH, alloy)
        try:
            misfit_p = os.path.join(alloy_dir, f"{alloy}_misfit_volumes_results.txt")
            sro_p = os.path.join(alloy_dir, f"{alloy}_sro_results.json")
            epi_p = os.path.join(alloy_dir, f"{alloy}_epi_results.txt")
            
            base = excel_baseline[alloy]
            comp, misfits, avg_vol = parse_misfit_volumes(misfit_p)
            veff = parse_epi(epi_p)
            with open(sro_p) as f: sro_data = json.load(f)
            
            a_lat = (4.0 * avg_vol) ** (1.0 / 3.0)
            beta_0 = sum(comp[el] * (misfits[el]**2) for el in comp)
            wc_rand = find_wc(splines, (beta_0, 0, 0, 0, 0), w_min, w_max, w_scan)
            S_rand = S_of_w(wc_rand, splines, (beta_0, 0, 0, 0, 0))

            for temp_str, shell_data in sro_data.items():
                temp_match = re.search(r'\d+', str(temp_str))
                if not temp_match: continue
                T_K = int(temp_match.group())
                
                alpha = shell_data["1st"]
                beta_1 = 0.0
                for p1, p2 in PAIRS:
                    a_k = f"alpha_{p1}{p2}" if f"alpha_{p1}{p2}" in alpha else f"alpha_{p2}{p1}"
                    beta_1 += comp[p1]*comp[p2]*((misfits[p1]-misfits[p2])**2)*alpha.get(a_k, 0)
                
                wc_sro = find_wc(splines, (beta_0, beta_1, 0, 0, 0), w_min, w_max, w_scan)
                if np.isnan(wc_sro): continue
                
                S_sro = S_of_w(wc_sro, splines, (beta_0, beta_1, 0, 0, 0))
                eb_ratio = ((wc_sro**2 * S_sro) / (wc_rand**2 * S_rand))**(1/3)
                dtau_ratio = ((S_sro/S_rand)**2 * (wc_rand/wc_sro)**5)**(1/3)
                
                # --- Monocrystal Calculations (MPa) ---
                tau_A = compute_tau_A_fcc_1stNN(comp, alpha, veff, a_lat)
                
                sro_d_eb = base['Delta_Eb'] * eb_ratio
                sro_dtau_y0 = base['Ty0'] * dtau_ratio
                
                term = (KB * T_RT / sro_d_eb) * np.log(EPS_DOT_0 / base['strain_rate'])
                thermal_factor = (1 - term**(2/3)) if term < 1 else 0.0
                tau_thermal = sro_dtau_y0 * thermal_factor
                tau_total = tau_A + tau_thermal
                
                # --- Polycrystal Calculations (MPa) ---
                sigma_athermal = tau_A * TAYLOR_FACTOR
                sigma_thermal = tau_thermal * TAYLOR_FACTOR
                sigma_total = tau_total * TAYLOR_FACTOR

                results.append({
                    "Alloy": alloy, "T_formation_K": T_K,
                    "Monocrystal_Athermal_MPa": tau_A,
                    "Monocrystal_Thermal_MPa": tau_thermal,
                    "Monocrystal_Total_MPa": tau_total,
                    "Polycrystal_Athermal_MPa": sigma_athermal,
                    "Polycrystal_Thermal_MPa": sigma_thermal,
                    "Polycrystal_Total_MPa": sigma_total,
                    "Random_RSS_MPa": base['tau_y'] # Baseline from Excel
                })
        except Exception as e:
            print(f"Error in {alloy}: {e}")

    df_res = pd.DataFrame(results)
    output_path = os.path.join(OUTPUT_DIR, "SRO_Strengthening_Full_Results.csv")
    df_res.to_csv(output_path, index=False)
    print(f"Success! Results saved to: {output_path}")

if __name__ == "__main__":
    run_calculation()