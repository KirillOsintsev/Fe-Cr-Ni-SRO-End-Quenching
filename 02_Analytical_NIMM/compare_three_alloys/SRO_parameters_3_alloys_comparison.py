import json
import matplotlib.pyplot as plt

# --- File Configuration ---
# Добавляем тип маркера "m" для каждого сплава
alloys = {
    "Fe20Ni50Cr30": {"file": "Fe20Ni50Cr30_sro_results.json", "ls": ":",  "m": "^"},
    "Fe34Ni33Cr33": {"file": "Fe34Ni33Cr33_sro_results.json", "ls": "--", "m": "s"},
    "Fe60Ni20Cr20": {"file": "Fe60Ni20Cr20_sro_results.json", "ls": "-",  "m": "o"}        
}

# --- Plotting Setup --- 
fig, axes = plt.subplots(1, 3, figsize=(24, 7))
plt.subplots_adjust(top=0.8) 

# --- Data Extraction & Plotting ---
for alloy_name, config in alloys.items():
    with open(config["file"], 'r') as f:
        sro_data = json.load(f)
        
    temperatures = sorted([int(temp) for temp in sro_data.keys()])
    alpha_FeNi = [sro_data[str(t)]["1st"]["alpha_FeNi"] for t in temperatures]
    alpha_FeCr = [sro_data[str(t)]["1st"]["alpha_FeCr"] for t in temperatures]
    alpha_NiCr = [sro_data[str(t)]["1st"]["alpha_NiCr"] for t in temperatures]
    
    # Теперь используем config["m"] для маркера и config["ls"] для линии
    # Параметры отрисовки вынесены в общий словарь для чистоты кода
    plot_kwargs = {
        "marker": config["m"],
        "linestyle": config["ls"],
        "markersize": 12,
        "color": 'black',
        "fillstyle": 'none',
        "label": alloy_name
    }
   
    if alloy_name == "Fe20Ni50Cr30":
            plot_kwargs["fillstyle"] = 'full'
            plot_kwargs["markerfacecolor"] = 'red'
            plot_kwargs["markeredgecolor"] = 'black'

    axes[0].plot(temperatures, alpha_FeNi, **plot_kwargs)
    axes[1].plot(temperatures, alpha_FeCr, **plot_kwargs)
    axes[2].plot(temperatures, alpha_NiCr, **plot_kwargs)

# --- Formatting ---

# Установка разных диапазонов вручную
axes[0].set_ylim(-0.1, 0.0)  # Для FeNi
axes[1].set_ylim(-0.1, 0.0) # Для FeCr
axes[2].set_ylim(0, 0.2) # Для NiCr

titles = [r'$\alpha^1_{FeNi}$', r'$\alpha^1_{FeCr}$', r'$\alpha^1_{NiCr}$']

for i, ax in enumerate(axes):
    ax.set_title(titles[i], fontsize=28, pad=20)
    ax.set_xlabel('Temperature, K', fontsize=26, fontname='Arial')
    
    if i == 0:
        ax.set_ylabel('SRO parameters', fontsize=26, fontname='Arial')
        
    ax.tick_params(axis='both', labelsize=22)

# --- Global Legend ---
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', ncol=3, fontsize=20, 
           bbox_to_anchor=(0.5, 1.0), frameon=False)

plt.savefig('three_alloys_SRO.svg', bbox_inches='tight')
plt.show()