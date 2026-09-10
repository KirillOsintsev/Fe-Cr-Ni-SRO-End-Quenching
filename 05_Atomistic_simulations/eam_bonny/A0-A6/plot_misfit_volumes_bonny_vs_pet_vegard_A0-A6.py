import numpy as np
import matplotlib.pyplot as plt

# 1. ПОДГОТОВКА ДАННЫХ
xs = np.array([-0.05, 0, 0.05])
xs_percent = xs * 100 

# Данные Vegard's Law
data_vegard = {
    'Fe': {'v': np.array([11.8863, 11.896, 11.9057]), 'err': np.array([0.0, 0.0, 0.0]), 'marker': 'o'},
    'Ni': {'v': np.array([11.9438, 11.896, 11.8482]), 'err': np.array([0.0, 0.0, 0.0]), 'marker': 's', 'color': '#9771BD'},
    'Cr': {'v': np.array([11.8773, 11.896, 11.9147]), 'err': np.array([0.0, 0.0, 0.0]), 'marker': '^'}
}
lat_const_vegard = "a = 3.624 Å\nV = 11.896 Å$^3$"

# Данные Bonny EAM
data_bonny = {
    'Fe': {'v': np.array([10.8267, 10.8180, 10.8133]), 'err': np.array([0.0053, 0.0055, 0.0046]), 'marker': 'o'},
    'Ni': {'v': np.array([10.84849, 10.8180, 10.797]), 'err': np.array([0.00434, 0.0055, 0.0051]), 'marker': 's', 'color': '#9771BD'},
    'Cr': {'v': np.array([10.77874, 10.8180, 10.86251]), 'err': np.array([0.00617, 0.0055, 0.00436]), 'marker': '^'}
}
lat_const_bonny = "a = 3.512 Å\nV = 10.818 Å$^3$"

# Данные PET-MAD
data_pet = {
    'Fe': {'v': np.array([10.2726, 10.25702, 10.24173]), 'err': np.array([0.00195, 0.0023, 0.00241]), 'marker': 'o'},
    'Ni': {'v': np.array([10.26328, 10.25702, 10.25345]), 'err': np.array([0.0026, 0.0023, 0.00253]), 'marker': 's', 'color': '#9771BD'},
    'Cr': {'v': np.array([10.20377, 10.25702, 10.30846]), 'err': np.array([0.00255, 0.0023, 0.00129]), 'marker': '^'}
}
lat_const_pet = "a = 3.449 Å\nV = 10.257 Å$^3$"

def get_regression(x, y):
    slope, intercept = np.polyfit(x, y, 1)
    y_pred = slope * x + intercept
    residuals = y - y_pred
    r_squared = 1 - (np.sum(residuals**2) / np.sum((y - np.mean(y))**2))
    return slope, intercept, y_pred, r_squared

# 2. ВИЗУАЛИЗАЦИЯ
fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(17, 8), sharex=True)
plt.rcParams.update({'font.size': 14})

# --- ДОБАВЛЕНИЕ ОБЩЕГО ЗАГОЛОВКА ПО ЦЕНТРУ ---
fig.suptitle(r'Alloy: Fe60Ni20Cr20 | a_experiment = 3.583 ± 0.004 Å', 
             fontsize=14, fontweight='bold', y=0.98)

def plot_potential_data(ax, data_dict, title, lat_const):
    # Установка диапазона Y автоматически для каждого графика
    all_v = np.concatenate([d['v'] for d in data_dict.values()])
    v_min, v_max = np.min(all_v), np.max(all_v)
    ax.set_ylim(v_min - 0.05, v_max + 0.02)
    
    # --- ЛИНИИ ПЕРЕСЕЧЕНИЯ ---
    # Вертикальная серая пунктирная линия через X=0
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.6, zorder=1)
    
    # Горизонтальная серая пунктирная линия через значение в точке Xs=0
    # Берем значение из любого элемента (например, Fe), так как в нуле они совпадают
    v_zero = data_dict['Fe']['v'][1] 
    ax.axhline(y=v_zero, color='gray', linestyle='--', linewidth=1, alpha=0.6, zorder=1)
    
    # Подпись значения на горизонтальной линии
    #ax.text(4.8, v_zero + 0.002, f'{v_zero:.3f}', color='gray', fontsize=10, ha='right')
    
    # Параметр решетки
    ax.text(0.52, 0.95, lat_const, transform=ax.transAxes, color='black', 
            fontweight='bold', fontsize=14, ha='left', va='top')

    all_stats = []
    for label, d in data_dict.items():
        slope, intercept, y_pred, r2 = get_regression(xs, d['v'])
        current_color = d.get('color', 'black')
        
        # Отрисовка точек и ошибок
        ax.errorbar(xs_percent, d['v'], yerr=d['err'], fmt=d['marker'], 
                    color=current_color, ecolor=current_color, capsize=4, 
                    markersize=6, zorder=4)
        
        # Линии регрессии
        ax.plot(xs_percent, y_pred, color=current_color, linestyle='-', 
                linewidth=1, alpha=0.6, zorder=3)
        
        # Названия элементов (с небольшим смещением, чтобы не накладываться на линии)
        ax.text(xs_percent[0] + 0.3, d['v'][0], label, 
                color=current_color, fontweight='bold', verticalalignment='center')
        
        all_stats.append(fr'{label}: $V = {slope:.3f} \cdot Xs + {intercept:.3f}$ ($R^2={r2:.3f}$)')
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Xs, at. %', fontweight='bold', fontsize=14)
    ax.set_ylabel(r'Volume, Å$^3$/atom', fontweight='bold', fontsize=14)
    ax.grid(True, linestyle=':', alpha=0.3)
    
    # Статистика регрессии
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
plt.savefig("volume_triple_comparison.png", dpi=600)
plt.savefig("volume_triple_comparison.svg")
plt.show()