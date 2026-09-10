import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# 1. ПОДГОТОВКА ДАННЫХ
xs = np.array([-0.05, 0, 0.05])
xs_percent = xs * 100 

# Данные Vegard's Law
data_vegard = {
    'Fe': {'v': np.array([11.8863, 11.896, 11.9057]), 'err': np.array([0.0, 0.0, 0.0]), 'marker': 'o'},
    'Ni': {'v': np.array([11.9438, 11.896, 11.8482]), 'err': np.array([0.0, 0.0, 0.0]), 'marker': 's', 'color': '#9771BD'},
    'Cr': {'v': np.array([11.8773, 11.896, 11.9147]), 'err': np.array([0.0, 0.0, 0.0]), 'marker': '^'}
}
a_vegard = 3.624
lat_const_vegard = "a = 3.624 Å\nV = 11.896 Å$^3$"

# Данные Bonny EAM
data_bonny = {
    'Fe': {'v': np.array([10.8267, 10.8180, 10.8133]), 'err': np.array([0.0053, 0.0055, 0.0046]), 'marker': 'o'},
    'Ni': {'v': np.array([10.84849, 10.8180, 10.797]), 'err': np.array([0.00434, 0.0055, 0.0051]), 'marker': 's', 'color': '#9771BD'},
    'Cr': {'v': np.array([10.77874, 10.8180, 10.86251]), 'err': np.array([0.00617, 0.0055, 0.00436]), 'marker': '^'}
}

a_bonny = 3.512
lat_const_bonny = "a = 3.512 Å\nV = 10.818 Å$^3$"

# Данные PET-MAD
data_pet = {
    'Fe': {'v': np.array([10.2726, 10.25702, 10.24173]), 'err': np.array([0.00195, 0.0023, 0.00241]), 'marker': 'o'},
    'Ni': {'v': np.array([10.26328, 10.25702, 10.25345]), 'err': np.array([0.0026, 0.0023, 0.00253]), 'marker': 's', 'color': '#9771BD'},
    'Cr': {'v': np.array([10.20377, 10.25702, 10.30846]), 'err': np.array([0.00255, 0.0023, 0.00129]), 'marker': '^'}
}
a_pet = 3.449
lat_const_pet = "a = 3.449 Å\nV = 10.257 Å$^3$"

def get_constrained_regression(x, y, v_fixed):
    """
    Fits y = slope * x + intercept, where intercept is fixed to v_fixed.
    This ensures the physical constraint sum(cn * deltaVn) = 0 at Xs=0.
    """
    # To fix intercept, we solve for: y - v_fixed = slope * x
    y_shifted = y - v_fixed
    # Least squares for a line through the origin: slope = sum(x*y)/sum(x^2)
    slope = np.sum(x * y_shifted) / np.sum(x**2)
    intercept = v_fixed
    
    y_pred = slope * x + intercept
    residuals = y - y_pred
    # R^2 calculation
    r_squared = 1 - (np.sum(residuals**2) / np.sum((y - np.mean(y))**2))
    return slope, intercept, y_pred, r_squared

# 2. ВИЗУАЛИЗАЦИЯ
fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(17, 8), sharex=True)
plt.rcParams.update({'font.size': 14})

fig.suptitle(r'Alloy: Fe60Ni20Cr20 | a_experiment = 3.583 ± 0.004 Å', 
             fontsize=14, fontweight='bold', y=0.94)

def plot_potential_data(ax, data_dict, title, lat_const):
    all_v = np.concatenate([d['v'] for d in data_dict.values()])
    v_min, v_max = np.min(all_v), np.max(all_v)
    ax.set_ylim(v_min - 0.05, v_max + 0.05)
    
    # --- ЛИНИИ ПЕРЕСЕЧЕНИЯ ---
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.6, zorder=1)
    
    # Значение в центре (средний объем сплава)
    v_zero = data_dict['Fe']['v'][1] 
    ax.axhline(y=v_zero, color='gray', linestyle='--', linewidth=1, alpha=0.6, zorder=1)
    
    ax.text(0.52, 0.95, lat_const, transform=ax.transAxes, color='black', 
            fontweight='bold', fontsize=14, ha='left', va='top')

    all_stats = []
    for label, d in data_dict.items():
        # ПРИМЕНЕНИЕ ФИЗИЧЕСКОГО ОГРАНИЧЕНИЯ (intercept = v_zero)
        slope, intercept, y_pred, r2 = get_constrained_regression(xs, d['v'], v_zero)
        
        current_color = d.get('color', 'black')
        
        ax.errorbar(xs_percent, d['v'], yerr=d['err'], fmt=d['marker'], 
                    color=current_color, ecolor=current_color, capsize=4, 
                    markersize=6, zorder=4)
        
        ax.plot(xs_percent, y_pred, color=current_color, linestyle='-', 
                linewidth=1, alpha=0.6, zorder=3)
        
        ax.text(xs_percent[0] + 0.3, d['v'][0], label, 
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

# Отрисовка трех графиков
plot_potential_data(ax0, data_vegard, "Vegard's Law", lat_const_vegard)
plot_potential_data(ax1, data_bonny, 'Bonny EAM Potential', lat_const_bonny)
plot_potential_data(ax2, data_pet, 'PET-MAD Potential', lat_const_pet)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
# Сохранение и показ
plt.savefig("volume_triple_comparison_constrained.png", dpi=600)
plt.show()

# 3. ЭКСПОРТ В EXCEL И РАСЧЕТ DELTA
results = []
summary_delta = []

# Определяем концентрации для сплава A0-A6 (Fe60 Ni20 Cr20)
concentrations = {'Fe': 0.60, 'Ni': 0.20, 'Cr': 0.20}

# Для A0-A6 Xs одинаков для всех (обычно 0.05), но если вы считали иначе, 
# убедитесь, что переменная xs определена в начале скрипта.
# В вашем коде в начале: xs = np.array([-0.05, 0, 0.05])

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
        # ИСПРАВЛЕНО: используем правильные ключи 'xs' (если есть) или глобальный 'xs'
        # и 'v' вместо 'y'
        current_xs = d.get('xs', xs) 
        current_v = d['v']
        
        slope, intercept, _, r2 = get_constrained_regression(current_xs, current_v, v_zero)
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

# Сохранение результатов
with pd.ExcelWriter("misfit_volumes_and_delta_A0_A6.xlsx") as writer:
    pd.DataFrame(results).to_excel(writer, sheet_name='Details', index=False)
    pd.DataFrame(summary_delta).to_excel(writer, sheet_name='Summary_Delta', index=False)

print("\nSummary Table (A0-A6):")
print(pd.DataFrame(results).to_string(index=False))
print("\nDelta Results (A0-A6):")
print(pd.DataFrame(summary_delta).to_string(index=False))