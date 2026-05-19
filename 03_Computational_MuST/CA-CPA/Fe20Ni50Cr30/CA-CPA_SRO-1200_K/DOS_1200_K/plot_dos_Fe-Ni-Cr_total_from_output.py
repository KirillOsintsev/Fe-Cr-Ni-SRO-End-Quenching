import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from scipy.ndimage import gaussian_filter1d

# Alloy configuration
ALLOY_COMPONENTS = {
    1: 0.10, 2: 0.10, # Fe
    3: 0.25, 4: 0.25, # Ni
    5: 0.15, 6: 0.15  # Cr
}
alloy_name = "Fe20Ni50Cr30"

def gaussian_smooth(data, energy_array, sigma_ev):
    if len(data) < 5: return data
    delta_e = np.abs(energy_array[1] - energy_array[0])
    sigma_pts = sigma_ev / delta_e
    return gaussian_filter1d(data, sigma=sigma_pts)

def parse_incomplete_log(filename):
    raw_data = []
    ef_ry = 0.0
    re_energy_ia = re.compile(r"getMScatteringDOS: energy =\s+([-+]?\d+\.\d+).*ia =\s+(\d+)")
    re_dos_val = re.compile(r"Im\{-Int \[Z\*Tau\*Z-Z\*J\]/pi on VP\} =\s+([-+]?\d+\.\d+)")
    re_fermi = re.compile(r"Initial Fermi energy read from the potential:\s+([-+]?\d+\.\d+)")

    current_spin = 1
    last_energy = -1e10
    
    with open(filename, 'r') as f:
        tmp_e, tmp_ia = None, None
        for line in f:
            if "Initial Fermi energy" in line:
                m = re_fermi.search(line)
                if m: ef_ry = float(m.group(1))
            
            m_e = re_energy_ia.search(line)
            if m_e:
                energy = float(m_e.group(1))
                ia = int(m_e.group(2))
                if energy < last_energy - 0.05:
                    current_spin = 2
                last_energy = energy
                tmp_e, tmp_ia = energy, ia
                continue
            
            if tmp_e is not None:
                m_v = re_dos_val.search(line)
                if m_v:
                    raw_data.append([current_spin, tmp_e, tmp_ia, float(m_v.group(1))])
                    tmp_e = None
                    
    df = pd.DataFrame(raw_data, columns=['spin', 'energy', 'ia', 'dos'])
    return df, ef_ry

def process_and_plot(log_filename, e_range=[-10, 5], sigma_ev=0.06):
    df, ef_ry = parse_incomplete_log(log_filename)
    if df.empty:
        print("Data not found.")
        return

    plt.figure(figsize=(10, 7))
    plt.ylim(-25, 45)
    
    n_up, n_down = 0.0, 0.0
    dos_at_ef_up, dos_at_ef_down = 0.0, 0.0
    
    # Dictionaries to store smoothed data for total DOS calculation
    plot_data_up = None
    plot_data_down = None
    common_energy_ev = None

    for spin, color, label in [(1, 'royalblue', 'Spin Up'), (2, 'crimson', 'Spin Down')]:
        spin_df = df[df['spin'] == spin]
        if spin_df.empty: continue
        
        grouped = spin_df.groupby('energy')
        valid_energies, total_dos = [], []
        
        for e, group in grouped:
            if len(group) == 6:
                val = sum(group['dos'] * group['ia'].map(ALLOY_COMPONENTS))
                valid_energies.append(e)
                total_dos.append(val)
        
        if not valid_energies: continue
        
        en_ry = np.array(valid_energies)
        dos = np.array(total_dos)
        
        # Calculations for info block
        mask = en_ry <= ef_ry
        if any(mask):
            n_val = np.trapz(dos[mask], en_ry[mask])
            if spin == 1: n_up = n_val
            else: n_down = n_val
            
        d_at_ef = np.interp(ef_ry, en_ry, dos)
        if spin == 1: dos_at_ef_up = d_at_ef
        else: dos_at_ef_down = d_at_ef

        # Prepare for plotting
        en_ev = (en_ry - ef_ry) * 13.6057
        dos_plot = gaussian_smooth(dos, en_ev, sigma_ev)
        y_vals = dos_plot if spin == 1 else -dos_plot
        
        # Store for Total DOS calculation
        if spin == 1:
            plot_data_up = dos_plot
            common_energy_ev = en_ev
        else:
            plot_data_down = dos_plot

        plt.plot(en_ev, y_vals, label=label, color=color, lw=2)
        plt.fill_between(en_ev, 0, y_vals, color=color, alpha=0.3)

    # --- ADDING TOTAL DOS LINE ---
    if plot_data_up is not None and plot_data_down is not None:
        # Total DOS is the sum of both magnitudes (ignoring the negative sign for plotting)
        total_dos_sum = plot_data_up + plot_data_down
        plt.plot(common_energy_ev, total_dos_sum, label='Total DOS', 
                 color='black', ls=':', lw=1.5, alpha=0.7)

    # Info block logic
    total_electrons = n_up + n_down
    mag_moment = n_up - n_down
    dos_at_ef_total = dos_at_ef_up + dos_at_ef_down
    ef_ev = ef_ry * 13.6057

    info_text = (
        f"Fermi Energy:\n"
        f"  {ef_ry:8.4f} Ry\n"
        f"  {ef_ev:8.4f} eV\n"
        f"{'-'*20}\n"
        f"Avg Spin Up $e^-$:   {n_up:7.4f}\n"
        f"Avg Spin Down $e^-$: {n_down:7.4f}\n"
        f"Total $e^-$:       {total_electrons:7.4f}\n"
        f"Total Mag. Moment: {mag_moment:7.4f} $\mu_B$\n"
        f"DOS at $E_F$ (Total): {dos_at_ef_total:7.4f}\n"
        f"DOS at $E_F$ (Up):    {dos_at_ef_up:7.4f}\n"
        f"DOS at $E_F$ (Down):  {dos_at_ef_down:7.4f}"
    )

    plt.text(0.02, 0.98, info_text, transform=plt.gca().transAxes, 
             fontsize=10, family='monospace', verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='gray'))

    plt.axvline(x=0, color='black', ls='--', lw=1.2, label='$E_F$')
    plt.axhline(y=0, color='black', lw=0.8)
    
    plt.title(f'Density of States of {alloy_name} with SRO at 1200 K', fontsize=18, fontweight='bold')
    plt.xlabel('Energy - $E_F$ (eV)', fontsize=12)
    plt.ylabel('DOS (states/atom/Ryd)', fontsize=12)
    plt.grid(True, ls=':', alpha=0.6)
    plt.legend(loc='upper right')
    plt.xlim(e_range)
    
    plt.tight_layout()
    plt.savefig(f'{alloy_name}_DOS_plot.svg')
    plt.savefig(f'{alloy_name}_DOS_plot.png', dpi=600)
    plt.show()

# Run
log_name = "o_n0000000_Fe20Ni50Cr30_CA-CPA_DOS_1200_K" 
process_and_plot(log_name, sigma_ev=0.06)