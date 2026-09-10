import numpy as np
import matplotlib.pyplot as plt

# 1. ПОДГОТОВКА ДАННЫХ
xs = np.array([-0.05, 0, 0.05])
xs_percent = xs * 100 

# Данные Vegard's Law
data_vegard = {
    'Fe': {'v': np.array([11.5416, 11.5690, 11.5937]), 'err': np.array([0.0, 0.0, 0.0]), 'marker': 'o'},
    'Ni': {'v': np.array([11.6018, 11.5690, 11.5362]), 'err': np.array([0.0, 0.0, 0.0]), 'marker': 's', 'color': '#9771BD'},
    'Cr': {'v': np.array([11.5353, 11.5690, 11.6027]), 'err': np.array([0.0, 0.0, 0.0]), 'marker': '^'}
}
lat_const_vegard = "a = 3.59 Å\nV = 11.770 Å$^3$"

# Данные Bonny EAM
data_bonny = {
    'Fe': {'v': np.array([10.915067, 10.891741, 10.870017]), 'err': np.array([0.001773, 0.002097, 0.002232]), 'marker': 'o'},
    'Ni': {'v': np.array([10.903252, 10.891741, 10.878967]), 'err': np.array([0.002990, 0.002097, 0.002902]), 'marker': 's', 'color': '#9771BD'},
    'Cr': {'v': np.array([10.860664, 10.891741, 10.923542]), 'err': np.array([0.002902, 0.002097, 0.002659]), 'marker': '^'}
}
lat_const_bonny = "a = 3.517 Å\nV = 10.892 Å$^3$"

# Данные PET-MAD
data_pet = {
    'Fe': {'v': np.array([10.5458, 10.5141, 10.4798]), 'err': np.array([0.002, 0.0012, 0.0027]), 'marker': 'o'},
    'Ni': {'v': np.array([10.5228, 10.514, 10.5040]), 'err': np.array([0.0024, 0.0012, 0.0029]), 'marker': 's', 'color': '#9771BD'},
    'Cr': {'v': np.array([10.4772, 10.514, 10.5492]), 'err': np.array([0.0009, 0.0012, 0.0028]), 'marker': '^'}
}
lat_const_pet = "a = 3.476 Å\nV = 10.514 Å$^3$"

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
fig.suptitle(r'Alloy: Fe20Ni50Cr30 | a_experiment = 3.585 ± 0.003 Å', 
             fontsize=14, fontweight='bold', y=0.94)

def plot_potential_data(ax, data_dict, title, lat_const):
    all_v = np.concatenate([d['v'] for d in data_dict.values()])
    v_min, v_max = np.min(all_v), np.max(all_v)
    ax.set_ylim(v_min - 0.05, v_max + 0.02)
    
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