import os
import json
import re
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from scipy.interpolate import griddata
import plotly.io as pio
import plotly.colors as pc

# --- Параметры ---
INPUT_FILE = "/Users/osintsevkirill/Yandex.Disk.localized/Science/Postdoc_project/Fe-Cr-Ni-SRO-End-Quenching/02_Analytical_NIMM/strengthening/SRO_Strengthening_Full_Results_correct.xlsx"

# Выбранная колонка
TARGET_VALUE_COLUMN = 'Percent_change_random_vs_sro_monocrystal'

# Единица измерения для подписей: '%' для процентов или 'MPa' для напряжений
UNITS = '%' if 'percent' in TARGET_VALUE_COLUMN.lower() else 'MPa'

# Температура формирования SRO для отображения
TARGET_TEMP = 1200 

INTERPOLATION_POINTS = 100 
AXIS_MIN_PERCENT = 20 
AXIS_MAX_PERCENT = 60 
COLORSCALE = 'Plasma' 
REVERSE_COLORSCALE = True # Выключаем инверсию для точного соответствия градиента

# Автоматический или ручной диапазон цветовой шкалы (заполняется ниже)
COLORBAR_MIN = None 
COLORBAR_MAX = None 

# --- Настройка кастомной палитры (как в старом скрипте) ---
base_plasma = pc.sequential.Plasma
cutoff_index = int(len(base_plasma) * 0.85) # Отсекаем 30% яркого желтого
truncated_plasma = base_plasma[:cutoff_index]

n_colors = len(truncated_plasma)
CUSTOM_COLORSCALE = [
    [i / (n_colors - 1), color] for i, color in enumerate(truncated_plasma)
]

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

df = pd.read_excel(INPUT_FILE)
df.columns = df.columns.astype(str).str.strip()

if TARGET_VALUE_COLUMN not in df.columns:
    print(f"\n[ОШИБКА] Колонка '{TARGET_VALUE_COLUMN}' не найдена в Excel-файле!")
    exit()

# 1. Фильтруем по температуре
df_filtered = df[df['T_formation_K'] == TARGET_TEMP].copy()

if df_filtered.empty:
    available_temps = df['T_formation_K'].unique()
    print(f"Данные для температуры {TARGET_TEMP}K не найдены. Доступные температуры: {available_temps}")
    exit()

# 2. Извлекаем координаты компонентов
comps = df_filtered['Alloy'].apply(lambda x: pd.Series(parse_alloy_name(x)))
df_filtered[['Fe', 'Ni', 'Cr']] = comps

a_coords = df_filtered['Cr'].values # Cr (верхняя ось)
b_coords = df_filtered['Fe'].values # Fe (левая ось)
c_coords = df_filtered['Ni'].values # Ni (правая ось)
target_values = df_filtered[TARGET_VALUE_COLUMN].values

# Динамическое или явное задание границ шкалы
if COLORBAR_MIN is None:
    COLORBAR_MIN = np.min(target_values)
if COLORBAR_MAX is None:
    COLORBAR_MAX = np.max(target_values)

# --- Интерполяция ---
points_cartesian = np.array([ternary_to_cartesian(np.array([a, b, c])) for a, b, c in zip(a_coords, b_coords, c_coords)])
points_x = points_cartesian[:, 0]
points_y = points_cartesian[:, 1]

grid_x = np.linspace(min(points_x), max(points_x), INTERPOLATION_POINTS)
grid_y = np.linspace(min(points_y), max(points_y), INTERPOLATION_POINTS)
grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)

grid_interpolated_values = griddata(points_cartesian, target_values, (grid_xx, grid_yy), method='cubic')
grid_ternary = np.array([cartesian_to_ternary([x, y]) for x, y in zip(grid_xx.ravel(), grid_yy.ravel())])

# Маска фильтрации
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

# Двухуровневая сортировка по координатам экрана (снизу вверх, слева направо)
grid_x_valid = grid_xx.ravel()[valid_mask]
grid_y_valid = grid_yy.ravel()[valid_mask]
sort_indices = np.lexsort((grid_x_valid, grid_y_valid))

grid_a = grid_a[sort_indices]
grid_b = grid_b[sort_indices]
grid_c = grid_c[sort_indices]
grid_interpolated_filtered = grid_interpolated_filtered[sort_indices]

# --- Создание графика Plotly ---
fig = go.Figure()

# 1. Слой интерполяции (фоновая тепловая карта из квадратов)
if len(grid_a) > 0:
    fig.add_trace(go.Scatterternary(
        a=grid_a, b=grid_b, c=grid_c,
        mode='markers',
        marker=dict(
            symbol='square',
            size=12,
            opacity=1.0,
            color=grid_interpolated_filtered,
            colorscale=CUSTOM_COLORSCALE,
            reversescale=REVERSE_COLORSCALE,
            colorbar=dict(title=f'{TARGET_VALUE_COLUMN} ({UNITS})'),
            line=dict(width=0.2, color='rgba(0,0,0,0)'),
            cmin=COLORBAR_MIN,
            cmax=COLORBAR_MAX
        ),
        hoverinfo='skip',
        showlegend=False
    ))

# 2. Слой реальных точек с интерактивными тултипами
fig.add_trace(go.Scatterternary(
    a=a_coords, b=b_coords, c=c_coords,
    mode='markers',
    marker=dict(
        symbol='circle',
        size=7,
        color=target_values,
        colorscale=CUSTOM_COLORSCALE,
        reversescale=REVERSE_COLORSCALE,
        line=dict(width=1, color='white'),
        cmin=COLORBAR_MIN,
        cmax=COLORBAR_MAX
    ),
    text=[f"Alloy: {name}<br>Cr: {cr}% Fe: {fe}% Ni: {ni}%<br>{TARGET_VALUE_COLUMN}: {val:.2f} {UNITS}"
          for name, cr, fe, ni, val in zip(df_filtered['Alloy'], a_coords, b_coords, c_coords, target_values)],
    hoverinfo='text',
    showlegend=False
))

# Настройка макета и осей
fig.update_layout(
    title=dict(
        font=dict(size=20)
    ),
    ternary=dict(
        sum=100,
        aaxis=dict(
            title=dict(
                text='Cr',
                font=dict(size=26, family="Arial", color="black")
            ),
            min=AXIS_MIN_PERCENT,
            tickformat='.0f',
            showgrid=True,
            tickcolor='black',
            gridcolor='lightgrey',
            tickvals=[30, 40, 50],
            tickfont=dict(size=24)
        ),
        baxis=dict(
            title=dict(
                text='Fe',
                font=dict(size=26, family="Arial", color="black")
            ),
            min=AXIS_MIN_PERCENT,
            tickformat='.0f',
            showgrid=True,
            tickcolor='black',
            gridcolor='lightgrey',
            tickvals=[30, 40, 50],
            tickfont=dict(size=24)
        ),
        caxis=dict(
            title=dict(
                text='Ni',
                font=dict(size=26, family="Arial", color="black")
            ),
            min=AXIS_MIN_PERCENT,
            tickformat='.0f',
            showgrid=True,
            tickcolor='black',
            gridcolor='lightgrey',
            tickvals=[30, 40, 50],
            tickfont=dict(size=24)
        )
    ),
    margin=dict(l=80, r=80, t=80, b=80),
    showlegend=False
)

# Настройка расположения горизонтального Colorbar над графиком
fig.update_traces(
    marker=dict(
        colorbar=dict(
            orientation='h',
            x=0.5,
            y=1.1,
            xanchor='center',
            yanchor='bottom',
            len=0.5,
            title=dict(
                text=f'{TARGET_VALUE_COLUMN} (T={TARGET_TEMP}K)',
                font=dict(size=26, family="Arial", color="black"),
                side='top'
            ),
            tickfont=dict(size=24, family="Arial", color="black")
        )
    ),
    selector=dict(type='scatterternary', marker_symbol='square')
)

# --- Сохранение графика ---
file_base_name = f"{TARGET_VALUE_COLUMN}_{TARGET_TEMP}K_24-08"

pio.write_html(fig, f'{file_base_name}.html', auto_open=False)

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
    print(f"Графики успешно сохранены: {file_base_name}")
except ValueError:
    print(f"\n[ВНИМАНИЕ] HTML сохранен. Для экспорта SVG/JPG установите kaleido: pip install kaleido")

fig.show()