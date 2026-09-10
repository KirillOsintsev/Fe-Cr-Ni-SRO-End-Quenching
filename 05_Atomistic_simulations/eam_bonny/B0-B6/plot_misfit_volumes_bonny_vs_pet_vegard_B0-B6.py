import numpy as np
import matplotlib.pyplot as plt

# 1. ПОДГОТОВКА ДАННЫХ
xs = np.array([-0.05, 0, 0.05])
xs_percent = xs * 100 

# Данные Vegard's Law
data_vegard = {
    'Fe': {'v': np.array([11.7547, 11.7699, 11.7851]), 'err': np.array([0.0, 0.0, 0.0]), 'marker': 'o'},
    'Ni': {'v': np.array([11.8122, 11.770, 11.7279]), 'err': np.array([0.0, 0.0, 0.0]), 'marker': 's', 'color': '#9771BD'},
    'Cr': {'v': np.array([11.7431, 11.770, 11.7944]), 'err': np.array([0.0, 0.0, 0.0]), 'marker': '^'}
}
lat_const_vegard = "a = 3.611 Å\nV = 11.770 Å$^3$"

# Данные Bonny EAM
data_bonny = {
    'Fe': {'v': np.array([10.928, 10.912, 10.895]), 'err': np.array([0.003, 0.003, 0.004]), 'marker': 'o'},
    'Ni': {'v': np.array([10.932, 10.912, 10.893]), 'err': np.array([0.002, 0.003, 0.003]), 'marker': 's', 'color': '#9771BD'},
    'Cr': {'v': np.array([10.875, 10.912, 10.947]), 'err': np.array([0.003, 0.003, 0.003]), 'marker': '^'}
}
lat_const_bonny = "a = 3.521 Å\nV = 10.912 Å$^3$"

# Данные PET-MAD
data_pet = {
    'Fe': {'v': np.array([10.5085, 10.4765, 10.4448]), 'err': np.array([0.0012, 0.0019, 0.0021]), 'marker': 'o'},
    'Ni': {'v': np.array([10.4875, 10.4765, 10.4666]), 'err': np.array([0.0017, 0.0019, 0.0014]), 'marker': 's', 'color': '#9771BD'},
    'Cr': {'v': np.array([10.4347, 10.4765, 10.5170]), 'err': np.array([0.0022, 0.0019, 0.0019]), 'marker': '^'}
}
lat_const_pet = "a = 3.473 Å\nV = 10.477 Å$^3$"

def get_regression(x, y):
    slope, intercept = np.polyfit(x, y, 1)
    y_pred = slope * x + intercept
    residuals = y - y_pred
    r_squared = 1 - (np.sum(residuals**2) / np.sum((y - np.mean(y))**2))
    return slope, intercept, y_pred, r_squared

# 2. ВИЗУАЛИЗАЦИЯ
fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(17, 8), sharex=True)
plt.rcParams.update({'font.size': 14})

# Общий заголовок
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
        slope, intercept, y_pred, r2 = get_regression(xs, d['v'])
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

plot_potential_data(ax0, data_vegard, "Vegard's Law", lat_const_vegard)
plot_potential_data(ax1, data_bonny, 'Bonny EAM Potential', lat_const_bonny)
plot_potential_data(ax2, data_pet, 'PET-MAD Potential', lat_const_pet)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig("volume_triple_comparison.png", dpi=600)
plt.savefig("volume_triple_comparison.svg")
plt.show()