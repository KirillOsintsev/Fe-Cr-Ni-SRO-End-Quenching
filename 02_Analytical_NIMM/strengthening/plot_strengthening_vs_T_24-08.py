import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# --- CONFIGURATION (Сплавы и стили из вашего примера) ---
alloys_config = {
    "Fe20Ni50Cr30": {"ls": ":",  "m": "^"},
    "Fe34Ni33Cr33": {"ls": "--", "m": "s"},
    "Fe60Ni20Cr20": {"ls": "-",  "m": "o"}        
}

# --- PATHS ---
INPUT_FILE = "/Users/osintsevkirill/Yandex.Disk.localized/Science/Postdoc_project/Fe-Cr-Ni-SRO-End-Quenching/02_Analytical_NIMM/strengthening/SRO_Strengthening_Full_Results.csv"

# --- ПОЛЬЗОВАТЕЛЬСКИЕ НАСТРОЙКИ ГРАФИКА ---
TARGET_COLUMN = 'Monocrystal_Total_MPa'  # Любая колонка из файла результатов
BASELINE_COLUMN = 'Random_RSS_MPa'       # Колонка для горизонтальной линии (RSS)

TEMP_MIN, TEMP_MAX, TEMP_TO_SKIP = 400, 1200, 773

# --- PLOTTING STYLE CONSTANTS (Строго из вашего примера) ---
FONT_SIZE_AXIS_LABEL = 26
FONT_SIZE_TICK = 24
FONT_SIZE_LEGEND = 20 
MARKER_SIZE = 10
LINE_WIDTH = 3.0
FIGURE_SIZE = (7, 7) 
FONT_NAME = 'Arial'

CUSTOM_COLORS = {
    'Fe60Ni20Cr20': 'black',
    'Fe34Ni33Cr33': 'black',
    'Fe20Ni50Cr30': 'black',
}

# --- DATA PROCESSING ---
def generate_plots():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: File not found {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)
    
    # Фильтрация по температуре и списку сплавов
    df = df[
        (df['T_formation_K'] >= TEMP_MIN) & 
        (df['T_formation_K'] <= TEMP_MAX) & 
        (df['T_formation_K'] != TEMP_TO_SKIP) &
        (df['Alloy'].isin(alloys_config.keys()))
    ].copy()

    if df.empty:
        print("No data found for the given parameters.")
        return

    # Создание фигуры
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    ax.set_box_aspect(1)
    
    for alloy in alloys_config.keys():
        alloy_data = df[df['Alloy'] == alloy].sort_values('T_formation_K')
        if alloy_data.empty: continue
        
        config = alloys_config[alloy]
        current_color = CUSTOM_COLORS.get(alloy, 'black')

        # Общие настройки для линии
        line_kwargs = {
            "linestyle": config["ls"],
            "linewidth": LINE_WIDTH,
            "color": current_color,
            "label": alloy
        }

        # 1. Отрисовка основной линии БЕЗ маркеров
        ax.plot(alloy_data['T_formation_K'], alloy_data[TARGET_COLUMN], marker=None, **line_kwargs)

        # 2. Выделение только точек при T = 400 K и T = 1200 K
        highlight_data = alloy_data[alloy_data['T_formation_K'].isin([400, 1200])]
        
        if not highlight_data.empty:
            marker_kwargs = {
                "marker": config["m"],
                "markersize": MARKER_SIZE,
                "color": current_color,
                "fillstyle": 'full',
                "markerfacecolor": 'white',
                "markeredgecolor": current_color,
                "linestyle": 'None'  # Линию повторно не рисуем
            }
            
            # Специфическое условие для красного маркера Fe20Ni50Cr30
            if alloy == "Fe20Ni50Cr30":
                marker_kwargs["markerfacecolor"] = 'red'
                marker_kwargs["markeredgecolor"] = 'black'

            ax.plot(highlight_data['T_formation_K'], highlight_data[TARGET_COLUMN], **marker_kwargs)

        # 3. Отрисовка горизонтальной линии RSS (Baseline)
        if BASELINE_COLUMN in alloy_data.columns:
            rss_val = alloy_data[BASELINE_COLUMN].iloc[0]
            ax.axhline(
                y=rss_val, 
                color=current_color, 
                linestyle=config["ls"], 
                linewidth=2.0, 
                alpha=0.8
            )
            
            # Подпись линии RSS (координата X смещена влево, так как ось инвертирована)
            ax.text(
                TEMP_MAX - 20, 
                rss_val, 
                f'{alloy} RSS', 
                color=current_color, 
                fontsize=FONT_SIZE_TICK * 0.6, 
                va='bottom',
                fontname=FONT_NAME
            )

    # Настройка осей (шрифты, метки)
    ax.set_xlabel('Temperature for SRO formation (K)', fontsize=FONT_SIZE_AXIS_LABEL, fontname=FONT_NAME)
    
    ylabel = TARGET_COLUMN.replace('_', ' ') + ' (MPa)'
    ax.set_ylabel(ylabel, fontsize=FONT_SIZE_AXIS_LABEL, fontname=FONT_NAME)
    
    # 1. РАЗВОРОТ ОСИ X (начинаем с 1200 и идем к 400)
    ax.set_xlim(TEMP_MAX + 30, TEMP_MIN - 30)
    
    # Автоматическая настройка лимитов Y
    y_min_data = df[TARGET_COLUMN].min()
    y_max_data = df[TARGET_COLUMN].max()
    ax.set_ylim(y_min_data * 0.7, y_max_data * 1.1)

    ax.tick_params(labelsize=FONT_SIZE_TICK)
    
    # Деления (Locators)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(200))

    # Легенда сверху
    ax.legend(
        loc='upper center', 
        bbox_to_anchor=(0.5, 1.18), 
        ncol=len(alloys_config), 
        fontsize=FONT_SIZE_LEGEND, 
        frameon=False
    )

    # Сохранение файлов
    clean_name = TARGET_COLUMN.lower()
    plt.savefig(f"SRO_plot_{clean_name}.png", bbox_inches='tight', dpi=300)
    plt.savefig(f"SRO_plot_{clean_name}.svg", bbox_inches='tight')
    
    print(f"Done! Plots saved: SRO_plot_{clean_name}.png/svg")
    plt.show()

if __name__ == "__main__":
    generate_plots()