import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# 1. ПОДГОТОВКА ДАННЫХ
# Концентрации компонентов в сплаве Fe34Ni33Cr33
concentrations = {'Fe': 0.34, 'Ni': 0.33, 'Cr': 0.33}

# Индивидуальные значения Xs
xs_fe = np.array([-0.051515, 0, 0.051515])
xs_others = np.array([-0.05074627, 0, 0.05074627])

# Данные Vegard's Law
data_vegard = {
    'Fe': {'v': np.array([11.75474, 11.7699, 11.78506]), 'xs': xs_fe, 'err': np.array([0.0, 0.0, 0.0]), 'marker': 'o'},
    'Ni': {'v': np.array([11.81224, 11.7699, 11.72792]), 'xs': xs_others, 'err': np.array([0.0, 0.0, 0.0]), 'marker': 's', 'color': '#9771BD'},
    'Cr': {'v': np.array([11.74308, 11.7699, 11.79442]), 'xs': xs_others, 'err': np.array([0.0, 0.0, 0.0]), 'marker': '^'}
}
a_vegard = 3.611
lat_const_vegard = f"a = {a_vegard} Å\nV = 11.770 Å$^3$"

# Данные Bonny EAM
data_bonny = {
    'Fe': {'v': np.array([10.928, 10.912, 10.895]), 'xs': xs_fe, 'err': np.array([0.003, 0.003, 0.004]), 'marker': 'o'},
    'Ni': {'v': np.array([10.932, 10.912, 10.893]), 'xs': xs_others, 'err': np.array([0.002, 0.003, 0.003]), 'marker': 's', 'color': '#9771BD'},
    'Cr': {'v': np.array([10.875, 10.912, 10.947]), 'xs': xs_others, 'err': np.array([0.003, 0.003, 0.003]), 'marker': '^'}
}
a_bonny = 3.521
lat_const_bonny = f"a = {a_bonny} Å\nV = 10.912 Å$^3$"

# Данные PET-MAD
data_pet = {
    'Fe': {'v': np.array([10.5085, 10.4765, 10.4448]), 'xs': xs_fe, 'err': np.array([0.0012, 0.0019, 0.0021]), 'marker': 'o'},
    'Ni': {'v': np.array([10.4875, 10.4765, 10.4666]), 'xs': xs_others, 'err': np.array([0.0017, 0.0019, 0.0014]), 'marker': 's', 'color': '#9771BD'},
    'Cr': {'v': np.array([10.4347, 10.4765, 10.5170]), 'xs': xs_others, 'err': np.array([0.0022, 0.0019, 0.0019]), 'marker': '^'}
}
a_pet = 3.473
lat_const_pet = f"a = {a_pet} Å\nV = 10.477 Å$^3$"

def get_constrained_regression(x, y, v_fixed):
    y_shifted = y - v_fixed
    slope = np.sum(x * y_shifted) / np.sum(x**2)
    intercept = v_fixed
    y_pred = slope * x + intercept
    residuals = y - y_pred
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 1.0
    return slope, intercept, y_pred, r_squared

# 2. ВИЗУАЛИЗАЦИЯ
fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(17, 8), sharex=False)
plt.rcParams.update({'font.size': 14})

# ОБЩИЙ ЗАГОЛОВОК
fig.suptitle(r'Alloy: Fe34Ni33Cr33 | a_experiment = 3.587 ± 0.006 Å', 
             fontsize=14, fontweight='bold', y=0.94)

def plot_potential_data(ax, data_dict, title, lat_const):
    all_v = np.concatenate([d['v'] for d in data_dict.values()])
    v_min, v_max = np.min(all_v), np.max(all_v)
    ax.set_ylim(v_min - 0.05, v_max + 0.05)
    
    # Линии пересечения в нуле
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.6, zorder=1)
    v_zero = data_dict['Fe']['v'][1] 
    ax.axhline(y=v_zero, color='gray', linestyle='--', linewidth=1, alpha=0.6, zorder=1)
    
    # Параметр решетки и объем
    ax.text(0.52, 0.95, lat_const, transform=ax.transAxes, color='black', 
            fontweight='bold', fontsize=14, ha='left', va='top')

    all_stats = []
    for label, d in data_dict.items():
        # Регрессия с использованием индивидуального xs
        current_xs = d['xs']
        slope, intercept, y_pred, r2 = get_constrained_regression(current_xs, d['v'], v_zero)
        current_color = d.get('color', 'black')
        
        ax.errorbar(current_xs * 100, d['v'], yerr=d['err'], fmt=d['marker'], 
                    color=current_color, ecolor=current_color, capsize=4, 
                    markersize=6, zorder=4)
        
        ax.plot(current_xs * 100, y_pred, color=current_color, linestyle='-', 
                linewidth=1, alpha=0.6, zorder=3)
        
        ax.text(current_xs[0]*100 + 0.3, d['v'][0], label, 
                color=current_color, fontweight='bold', verticalalignment='center')
        
        all_stats.append(fr'{label}: $V = {slope:.3f} \cdot Xs + {intercept:.3f}$ ($R^2={r2:.3f}$)')
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Xs, at. %', fontweight='bold', fontsize=14)
    ax.set_ylabel(r'Volume, Å$^3$/atom', fontweight='bold', fontsize=14)
    ax.grid(True, linestyle=':', alpha=0.3)
    
    stats_text = "\n".join(all_stats)
    ax.text(0.03, 0.03, stats_text, transform=ax.transAxes, 
            bbox=dict(facecolor='white', alpha=0.9, edgecolor='none'), 
            fontsize=12, verticalalignment='bottom')

plot_potential_data(ax0, data_vegard, "Vegard's Law", lat_const_vegard)
plot_potential_data(ax1, data_bonny, 'Bonny EAM Potential', lat_const_bonny)
plot_potential_data(ax2, data_pet, 'PET-MAD Potential', lat_const_pet)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig("volume_triple_comparison_corrected.png", dpi=600)
plt.show()

# 3. ЭКСПОРТ В EXCEL И РАСЧЕТ DELTA
results = []
summary_delta = []

potentials_info = [
    ("Vegard's Law", data_vegard, a_vegard),
    ("Bonny EAM", data_bonny, a_bonny),
    ("PET-MAD", data_pet, a_pet)
]

for name, data_dict, a_lat in potentials_info:
    v_zero = data_dict['Fe']['v'][1]
    b = a_lat / np.sqrt(2) # Burgers vector for FCC
    
    sum_cn_dv2 = 0
    for label, d in data_dict.items():
        slope, intercept, _, r2 = get_constrained_regression(d['xs'], d['v'], v_zero)
        cn = concentrations[label]
        
        # Misfit volume DVn = slope
        sum_cn_dv2 += cn * (slope**2)
        
        results.append({
            'Potential Model': name,
            'Element': label,
            'Concentration (cn)': cn,
            'Misfit Volume (slope)': round(slope, 6),
            'Intercept (V_avg)': round(intercept, 6),
            'R-squared': round(r2, 6)
        })
    
    # Formula: delta = sqrt( (2 * sum(cn * DVn^2)) / (9 * b^6) )
    delta = np.sqrt((2 * sum_cn_dv2) / (9 * (b**6)))
    summary_delta.append({
        'Potential Model': name, 
        'Delta Parameter': round(delta, 6), 
        'Burgers vector b': round(b, 4),
        'a_lattice': a_lat
    })

# Сохранение с восстановленным форматированием таблицы
with pd.ExcelWriter("misfit_volumes_and_delta.xlsx") as writer:
    pd.DataFrame(results).to_excel(writer, sheet_name='Details', index=False)
    pd.DataFrame(summary_delta).to_excel(writer, sheet_name='Summary_Delta', index=False)

print("\nSummary Table (Corrected Xs & Delta):")
print(pd.DataFrame(results).to_string(index=False))
print("\nDelta Results:")
print(pd.DataFrame(summary_delta).to_string(index=False))