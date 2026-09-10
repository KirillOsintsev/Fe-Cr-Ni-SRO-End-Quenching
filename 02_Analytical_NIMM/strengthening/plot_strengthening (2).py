import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
from scipy.interpolate import griddata
import re
import os

# --- Параметры ---
# FIX: Убедитесь, что путь указывает именно на файл .xlsx
INPUT_FILE = "/Users/osintsevkirill/Yandex.Disk.localized/Science/Postdoc_project/Fe-Cr-Ni-SRO-End-Quenching/02_Analytical_NIMM/strengthening/SRO_Strengthening_Full_Results.xlsx"

# Выбранная колонка
TARGET_VALUE_COLUMN = 'Percent_change_random_vs_sro_monocrystal'

# Единица измерения для подписей: '%' для процентов или 'MPa' для напряжений
UNITS = '%' if 'percent' in TARGET_VALUE_COLUMN.lower() else 'MPa'

# Температура формирования SRO для отображения
TARGET_TEMP = 600 

INTERPOLATION_POINTS = 100 
AXIS_MIN_PERCENT = 20 
AXIS_MAX_PERCENT = 60 
COLORSCALE = 'Plasma' 
REVERSE_COLORSCALE = True 

# --- Функции преобразования ---
def ternary_to_cartesian(coords):
    a, b, c = coords / 100.0 
    x = c + b * 0.5
    y = b * np.sqrt(3) / 2
    return x, y

def cartesian_to_ternary(xy):
    x, y = xy
    b = y * 2 / np.sqrt(3)
    c = x - b * 0.5
    a = 1.0 - b - c
    return np.round(np.array([a, b, c]) * 100, 5)

def parse_alloy_name(name):
    """Извлекает проценты Fe, Ni, Cr из названия типа Fe20Ni50Cr30"""
    match = re.findall(r'([A-Z][a-z]?)(\d+)', str(name))
    comp = {el: int(val) for el, val in match}
    return comp.get('Fe', 0), comp.get('Ni', 0), comp.get('Cr', 0)

# --- Загрузка и подготовка данных ---
if not os.path.exists(INPUT_FILE):
    print(f"Файл не найден: {INPUT_FILE}")
    exit()

# FIX: Заменили pd.read_csv на pd.read_excel
df = pd.read_excel(INPUT_FILE)

# Очищаем заголовки от возможных случайных пробелов
df.columns = df.columns.astype(str).str.strip()

# Проверяем, существует ли нужная колонка
if TARGET_VALUE_COLUMN not in df.columns:
    print(f"\n[ОШИБКА] Колонка '{TARGET_VALUE_COLUMN}' не найдена в Excel-файле!")
    print("\nДоступные колонки в вашем XLSX:")
    for col in df.columns:
        print(f" - '{col}'")
    exit()

# 1. Фильтруем по температуре
df_filtered = df[df['T_formation_K'] == TARGET_TEMP].copy()

if df_filtered.empty:
    available_temps = df['T_formation_K'].unique()
    print(f"Данные для температуры {TARGET_TEMP}K не найдены. Доступные температуры: {available_temps}")
    exit()

# 2. Извлекаем координаты компонентов из названия сплава
comps = df_filtered['Alloy'].apply(lambda x: pd.Series(parse_alloy_name(x)))
df_filtered[['Fe', 'Ni', 'Cr']] = comps

a_coords = df_filtered['Cr'].values
b_coords = df_filtered['Fe'].values 
c_coords = df_filtered['Ni'].values 
target_values = df_filtered[TARGET_VALUE_COLUMN].values

# --- Интерполяция ---
points_cartesian = np.array([ternary_to_cartesian(np.array([a, b, c])) for a, b, c in zip(a_coords, b_coords, c_coords)])
points_x = points_cartesian[:, 0]
points_y = points_cartesian[:, 1]

grid_x = np.linspace(min(points_x), max(points_x), INTERPOLATION_POINTS)
grid_y = np.linspace(min(points_y), max(points_y), INTERPOLATION_POINTS)
grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)

grid_interpolated_values = griddata(points_cartesian, target_values, (grid_xx, grid_yy), method='cubic')

grid_ternary = np.array([cartesian_to_ternary([x, y]) for x, y in zip(grid_xx.ravel(), grid_yy.ravel())])

valid_mask = (
    np.isclose(np.sum(grid_ternary, axis=1), 100.0) &
    (grid_ternary >= AXIS_MIN_PERCENT).all(axis=1) &
    (grid_ternary <= AXIS_MAX_PERCENT).all(axis=1) &
    ~np.isnan(grid_interpolated_values.ravel())
)

grid_a = grid_ternary[valid_mask, 0]
grid_b = grid_ternary[valid_mask, 1]
grid_c = grid_ternary[valid_mask, 2]
grid_interpolated_filtered = grid_interpolated_values.ravel()[valid_mask]

# --- Создание графика ---
fig = go.Figure()

# Слой интерполяции (квадраты)
if len(grid_a) > 0:
    fig.add_trace(go.Scatterternary(
        a=grid_a, b=grid_b, c=grid_c,
        mode='markers',
        marker=dict(
            symbol='square', size=10,
            color=grid_interpolated_filtered,
            colorscale=COLORSCALE,
            reversescale=REVERSE_COLORSCALE,
            colorbar=dict(
                title=dict(text=f'{TARGET_VALUE_COLUMN}<br>({UNITS})', font=dict(size=18)),
                tickfont=dict(size=14)
            ),
            line_width=0
        ),
        hoverinfo='skip', showlegend=False
    ))

# Слой реальных точек (кружки)
fig.add_trace(go.Scatterternary(
    a=a_coords, b=b_coords, c=c_coords,
    mode='markers',
    marker=dict(
        symbol='circle', size=8,
        color=target_values,
        colorscale=COLORSCALE,
        reversescale=REVERSE_COLORSCALE,
        line=dict(color='black', width=1)
    ),
    text=[f"Alloy: {name}<br>Fe: {fe}% Ni: {ni}% Cr: {cr}%<br>{TARGET_VALUE_COLUMN}: {val:.2f} {UNITS}"
          for name, fe, ni, cr, val in zip(df_filtered['Alloy'], b_coords, c_coords, a_coords, target_values)],
    hoverinfo='text', showlegend=False
))

fig.update_layout(
    title=dict(
        text=f"{TARGET_VALUE_COLUMN} at T_SRO = {TARGET_TEMP} K",
        x=0.5, font=dict(size=24)
    ),
    ternary=dict(
        sum=100,
        aaxis=dict(title=dict(text='Cr (%)', font=dict(size=26)), min=AXIS_MIN_PERCENT, tickfont=dict(size=18)),
        baxis=dict(title=dict(text='Fe (%)', font=dict(size=26)), min=AXIS_MIN_PERCENT, tickfont=dict(size=18)),
        caxis=dict(title=dict(text='Ni (%)', font=dict(size=26)), min=AXIS_MIN_PERCENT, tickfont=dict(size=18))
    ),
    margin=dict(l=50, r=50, b=50, t=100)
)

# --- БЛОК СОХРАНЕНИЯ ГРАФИКА ---
file_base_name = f"{TARGET_VALUE_COLUMN}_{TARGET_TEMP}"

# 1. Сохранение в HTML
pio.write_html(fig, f'{file_base_name}.html', auto_open=False)

# 2. Сохранение в SVG/JPG
try:
    pio.write_image(fig, f'{file_base_name}.svg')
    pio.write_image(
        fig,
        file=f'{file_base_name}.jpg',
        format='jpg',
        scale=6,
        width=1200,
        height=800
    )
    print(f"Графики успешно сохранены с префиксом: {file_base_name}")
except ValueError:
    print(f"\n[ВНИМАНИЕ] HTML сохранен, но для сохранения в SVG/JPG требуется библиотека kaleido (pip install kaleido).")

fig.show()