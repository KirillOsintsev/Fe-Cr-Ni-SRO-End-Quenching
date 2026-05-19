import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from scipy.ndimage import gaussian_filter1d

# Конфигурация сплава из position.dat
ALLOY_COMPONENTS = {
    'c1': 0.17, 'c2': 0.17, # Fe (итого 20%)
    'c3': 0.165, 'c4': 0.165, # Ni (итого 50%)
    'c5': 0.165, 'c6': 0.165  # Cr (итого 30%)
}

alloy_name = "Fe34Ni33Cr33"  # Для отображения в заголовке и инфо-блоке

def gaussian_smooth(data, energy_array, sigma_ev):
    delta_e = np.abs(energy_array[1] - energy_array[0])
    sigma_pts = sigma_ev / delta_e
    return gaussian_filter1d(data, sigma=sigma_pts)

def plot_alloy_total_dos(basename, e_range=None, dos_range=None, sigma_ev=0.06, font_size=12):
    try:
        total_dos_up = None
        total_dos_down = None
        total_dos_all = None
        energy_ry = None
        ef_ry = None

        # 1. Сбор и суммирование данных
        for c_idx, weight in ALLOY_COMPONENTS.items():
            filename = f"{basename}_{c_idx}"
            
            # Парсинг заголовка для каждого файла
            current_ef = None
            data_start_line = 0
            with open(filename, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if "Fermi energy" in line:
                        current_ef = float(re.findall(r"[-+]?\d*\.\d+|\d+", line)[0])
                    if "Energy" in line:
                        data_start_line = i + 1
            
            df = pd.read_csv(filename, sep='\s+', skiprows=data_start_line, header=None)
            
            if energy_ry is None:
                energy_ry = df[0].values
                ef_ry = current_ef
                total_dos_all = df[1].values * weight
                total_dos_up = df[2].values * weight
                total_dos_down = df[3].values * weight
            else:
                total_dos_all += df[1].values * weight
                total_dos_up += df[2].values * weight
                total_dos_down += df[3].values * weight

        # 2. Расчеты для инфо-блока (на основе среднего по сплаву)
        mask = energy_ry <= ef_ry
        n_up = np.trapz(total_dos_up[mask], energy_ry[mask])
        n_down = np.trapz(total_dos_down[mask], energy_ry[mask])
        total_electrons = n_up + n_down
        mag_moment = n_up - n_down
        ef_ev = ef_ry * 13.6057
        dos_at_ef_total = np.interp(ef_ry, energy_ry, total_dos_all)
        dos_at_ef_up    = np.interp(ef_ry, energy_ry, total_dos_up)
        dos_at_ef_down  = np.interp(ef_ry, energy_ry, total_dos_down)

        # 3. Подготовка к отрисовке (перевод в eV и сдвиг к Ферми)
        energy_ev_rel = (energy_ry - ef_ry) * 13.6057
        
        if sigma_ev > 0:
            dos_up_p = gaussian_smooth(total_dos_up, energy_ev_rel, sigma_ev)
            dos_down_p = gaussian_smooth(total_dos_down, energy_ev_rel, sigma_ev)
            dos_total_p = gaussian_smooth(total_dos_all, energy_ev_rel, sigma_ev)
        else:
            dos_up_p, dos_down_p, dos_total_p = total_dos_up, total_dos_down, total_dos_all

        # 4. График
        plt.figure(figsize=(10, 7))
        plt.plot(energy_ev_rel, dos_up_p, label='Total Spin Up', color='royalblue', lw=2)
        plt.plot(energy_ev_rel, -dos_down_p, label='Total Spin Down', color='crimson', lw=2)
        plt.plot(energy_ev_rel, dos_total_p, label='Total DOS (Average)', color='black', ls=':', alpha=0.3)
        
        plt.fill_between(energy_ev_rel, dos_up_p, color='royalblue', alpha=0.3)
        plt.fill_between(energy_ev_rel, -dos_down_p, color='crimson', alpha=0.3)

        plt.axvline(x=0, color='black', ls='--', lw=1.2, label='$E_F$')
        plt.axhline(y=0, color='black', lw=0.8)

        if e_range: plt.xlim(e_range)
        if dos_range: plt.ylim(dos_range)

        # Текст с информацией (суммарной по сплаву)
        info_text = (
            f"Fermi Energy:\n"
            f"  {ef_ry:8.4f} Ry\n"
            f"  {ef_ev:8.4f} eV\n"
            f"{'-'*20}\n"
            f"Avg Spin Up $e^-$:   {n_up:7.4f}\n"
            f"Avg Spin Down $e^-$: {n_down:7.4f}\n"
            f"Total $e^-$:       {total_electrons:7.4f}\n"
            f"Total Mag. Moment: {mag_moment:7.4f} $\mu_B$ \n"
            f"DOS at $E_F$ (Total): {dos_at_ef_total:7.4f}\n"
            f"DOS at $E_F$ (Up):    {dos_at_ef_up:7.4f}\n"
            f"DOS at $E_F$ (Down):  {dos_at_ef_down:7.4f}"
        )
        
        plt.text(0.02, 0.98, info_text, transform=plt.gca().transAxes, 
                 fontsize=font_size-2, family='monospace', verticalalignment='top',
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='gray'))

        plt.title(f'{alloy_name} Density of States', fontsize=font_size+4, fontweight='bold')
        plt.xlabel('Energy - $E_F$ (eV)', fontsize=font_size)
        plt.ylabel('DOS (states/atom/Ryd)', fontsize=font_size)
        plt.legend(loc='upper right')
        plt.grid(True, ls=':', alpha=0.6)
        
        plt.tight_layout()
        plt.savefig(f'{alloy_name}_DOS.png', dpi=600, bbox_inches='tight')
        plt.savefig(f'{alloy_name}_DOS.svg', bbox_inches='tight')
        plt.show()

    except Exception as e:
        print(f"Ошибка при расчете общего DOS: {e}")

# Запуск расчета для всего сплава
plot_alloy_total_dos('DOS_Fe34Ni33Cr33_atom000001', e_range=[-10, 5], sigma_ev=0.06)