import os
import json
import re
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from scipy.interpolate import griddata
import plotly.io as pio

# --- Параметры ---
FOLDER_PATH = '/Users/osintsevkirill/Yandex.Disk.localized/Science/Postdoc_project/Fe-Cr-Ni-SRO-End-Quenching/02_Analytical_NIMM/all_sro_results'  # Укажите путь к папке с вашими JSON файлами
# FOLDER_PATH = '/path/to/your/json/files' # Пример для Linux/macOS
# FOLDER_PATH = 'C:\\path\\to\\your\\json\\files' # Пример для Windows

FILE_SUFFIX = '_sro_results.json'

TEMPERATURE = '1200'  # Температура ('100', '200', ..., '1200')
COORD_SPHERE = '1st'  # Координационная сфера ('1st', etc.)

# Параметры для интерполяции и отображения
INTERPOLATION_POINTS = 100 # Количество точек на сторону для интерполяции (больше = плавнее, но медленнее)
AXIS_MIN_PERCENT = 20  # Минимальное значение для осей (чуть меньше 20 для видимости)
AXIS_MAX_PERCENT = 60  # Максимальное значение для осей (чуть больше 60 для видимости)
COLORSCALE = 'Plasma'  # Цветовая схема для тепловой карты (например, 'Viridis', 'Plasma', 'Jet', 'RdBu')
REVERSE_COLORSCALE = True # Инвертировать ли цветовую шкалу

TARGET_ALPHA = 'alpha_NiCr'  # Какую альфу отображать ('alpha_FeNi', 'alpha_NiCr', 'alpha_FeCr')
COLORBAR_MIN = 0.06  # Минимальное значение для цветовой шкалы
COLORBAR_MAX = 0.02 # Максимальное значение для цветовой шкалы

"""
TARGET_ALPHA = 'alpha_FeCr'  # Какую альфу отображать ('alpha_FeNi', 'alpha_NiCr', 'alpha_FeCr')
COLORBAR_MIN = -0.037  # Минимальное значение для цветовой шкалы
COLORBAR_MAX = -0.005 # Максимальное значение для цветовой шкалы
"""
"""
TARGET_ALPHA = 'alpha_FeNi'  # Какую альфу отображать ('alpha_FeNi', 'alpha_NiCr', 'alpha_FeCr')
COLORBAR_MIN = -0.030  # Минимальное значение для цветовой шкалы
COLORBAR_MAX = -0.005 # Максимальное значение для цветовой шкалы
"""

# Настройка рендерера Plotly (может понадобиться в некоторых средах, например, VSFede)
# pio.renderers.default = "vscode" # или "jupyterlab", "notebook", "png", "svg", "browser"
# --- /Параметры ---

def extract_composition(filename):
    """
    Извлекает процентный состав Ni, Fe, Cr из имени файла, независимо от порядка элементов.
    Ожидаемый формат: содержит "FeXX", "NiYY", "CrZZ" в любом порядке.
    Возвращает словарь {'Fe': XX, 'Ni': YY, 'Cr': ZZ} или None при ошибке.
    """
    # Используем findall для поиска всех вхождений элементов и их процентов
    fe_match = re.search(r'Fe(\d+)', filename, re.IGNORECASE)
    ni_match = re.search(r'Ni(\d+)', filename, re.IGNORECASE)
    cr_match = re.search(r'Cr(\d+)', filename, re.IGNORECASE)

    fe, ni, cr = None, None, None

    if fe_match:
        fe = int(fe_match.group(1))
    if ni_match:
        ni = int(ni_match.group(1))
    if cr_match:
        cr = int(cr_match.group(1))

    # Проверяем, что все три элемента найдены
    if fe is not None and ni is not None and cr is not None:
        # Проверка, что сумма равна 100
        if fe + ni + cr == 100:
            return {'Fe': fe, 'Ni': ni, 'Cr': cr}
        else:
            print(f"Предупреждение: Сумма концентраций в файле {filename} не равна 100 ({fe}+{ni}+{cr}). Файл пропущен.")
            return None
    else:
        print(f"Предупреждение: Не удалось извлечь полный состав (Fe, Ni, Cr) из имени файла {filename}. Файл пропущен.")
        return None

def ternary_to_cartesian(coords):
    """Преобразует тернарные координаты (a, b, c) в декартовы (x, y)."""
    a, b, c = coords / 100.0 # Нормализуем до суммы 1
    x = c + b * 0.5
    y = b * np.sqrt(3) / 2
    return x, y

def cartesian_to_ternary(xy):
    """Преобразует декартовы координаты (x, y) обратно в тернарные (a, b, c)."""
    x, y = xy
    b = y * 2 / np.sqrt(3)
    c = x - b * 0.5
    a = 1.0 - b - c
    # Возвращаем в процентах и округляем, чтобы избежать ошибок точности
    return np.round(np.array([a, b, c]) * 100, 5)


# --- Сбор данных ---
data_points = []
print(f"Поиск файлов с суффиксом '{FILE_SUFFIX}' в папке '{os.path.abspath(FOLDER_PATH)}'")
found_files = 0
processed_files = 0

try:
    for filename in os.listdir(FOLDER_PATH):
        if filename.endswith(FILE_SUFFIX):
            found_files += 1
            filepath = os.path.join(FOLDER_PATH, filename)
            composition = extract_composition(filename)

            if composition:
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)

                    # Извлечение нужного значения alpha
                    alpha_value = data.get(TEMPERATURE, {}).get(COORD_SPHERE, {}).get(TARGET_ALPHA)
                    if alpha_value is not None:
                        data_points.append({
                            'Fe': composition['Fe'],
                            'Ni': composition['Ni'],
                            'Cr': composition['Cr'],
                            TARGET_ALPHA: alpha_value,
                            'filename': filename
                        })
                        processed_files += 1
                    else:
                        print(f"Предупреждение: Не найдено значение {TARGET_ALPHA} для T={TEMPERATURE}, сфера={COORD_SPHERE} в файле {filename}. Файл пропущен.")

                except json.JSONDecodeError:
                    print(f"Ошибка: Не удалось прочитать JSON из файла {filename}. Файл пропущен.")
                except Exception as e:
                    print(f"Ошибка при обработке файла {filename}: {e}. Файл пропущен.")

except FileNotFoundError:
    print(f"Ошибка: Папка '{FOLDER_PATH}' не найдена.")
except Exception as e:
    print(f"Произошла непредвиденная ошибка при поиске файлов: {e}")

print(f"Найдено файлов: {found_files}")
print(f"Успешно обработано файлов: {processed_files}")

if not data_points:
    print("Не найдено данных для построения графика. Проверьте путь к папке, имена файлов, суффикс, целевой параметр альфа и температуру.")

# --- Подготовка данных для Plotly ---
df = pd.DataFrame(data_points)

# Координаты исходных точек
# Fe -> b (левая ось), Ni -> c (правая ось), Cr -> a (верхняя ось)
a_coords = df['Cr'].values # Cr is now on top (a-axis)
b_coords = df['Fe'].values # Fe is now on the left (b-axis)
c_coords = df['Ni'].values # Ni is now on the right (c-axis)
alpha_values = df[TARGET_ALPHA].values

# --- Интерполяция для создания тепловой карты ---
# Преобразуем исходные точки в декартовы координаты для griddata
points_cartesian = np.array([ternary_to_cartesian(np.array([a,b,c])) for a,b,c in zip(a_coords, b_coords, c_coords)])
points_x = points_cartesian[:, 0]
points_y = points_cartesian[:, 1]

# Создаем сетку в декартовых координатах, которая соответствует тернарному пространству
min_val_frac = AXIS_MIN_PERCENT / 100.0
max_val_frac = AXIS_MAX_PERCENT / 100.0

x_grid_min, y_grid_min = ternary_to_cartesian(np.array([100 - 2*max_val_frac, max_val_frac, max_val_frac]))
x_grid_max, y_grid_max = ternary_to_cartesian(np.array([min_val_frac, min_val_frac, 100 - 2*min_val_frac]))
_, y_co_min = ternary_to_cartesian(np.array([100 - 2*min_val_frac, min_val_frac, min_val_frac]))
_, y_co_max = ternary_to_cartesian(np.array([100-2*max_val_frac, max_val_frac, max_val_frac]))

grid_x = np.linspace(min(points_x) * 1, max(points_x) * 1, INTERPOLATION_POINTS)
grid_y = np.linspace(min(points_y) * 1, max(points_y) * 1, INTERPOLATION_POINTS)
grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)

# Интерполируем значения alpha на сетку
grid_alpha = griddata(points_cartesian, alpha_values, (grid_xx, grid_yy), method='cubic')

# Преобразуем координаты сетки обратно в тернарные
grid_ternary = np.array([cartesian_to_ternary([x,y]) for x, y in zip(grid_xx.ravel(), grid_yy.ravel())])

# Отфильтровываем точки сетки
valid_mask = (
    np.isclose(np.sum(grid_ternary, axis=1), 100.0) &
    (grid_ternary >= AXIS_MIN_PERCENT).all(axis=1) &
    (grid_ternary <= AXIS_MAX_PERCENT).all(axis=1) &
    ~np.isnan(grid_alpha.ravel())
)

grid_a = grid_ternary[valid_mask, 0]
grid_b = grid_ternary[valid_mask, 1]
grid_c = grid_ternary[valid_mask, 2]
grid_alpha_filtered = grid_alpha.ravel()[valid_mask]


if len(grid_a) == 0:
    print("Предупреждение: Не удалось сгенерировать точки для интерполяции в заданном диапазоне концентраций.")

# --- Создание графика Plotly ---
fig = go.Figure()

# 1. Добавляем интерполированные данные как "тепловую карту"
if len(grid_a) > 0:
    fig.add_trace(go.Scatterternary(
        a=grid_a,
        b=grid_b,
        c=grid_c,
        mode='markers',
        marker=dict(
            symbol='square',
            size=10,
            color=grid_alpha_filtered,
            colorscale=COLORSCALE,
            reversescale=REVERSE_COLORSCALE,
            colorbar=dict(title=f'{TARGET_ALPHA} (T={TEMPERATURE}K)'),
            line_width=0,
            cmin=COLORBAR_MIN,
            cmax=COLORBAR_MAX
        ),
        hoverinfo='skip',
        showlegend=False
    ))

# 2. Добавляем исходные точки данных поверх тепловой карты
fig.add_trace(go.Scatterternary(
    a=a_coords,
    b=b_coords,
    c=c_coords,
    mode='markers',
    marker=dict(
        symbol='circle',
        size=8,
        color=alpha_values,
        colorscale=COLORSCALE,
        reversescale=REVERSE_COLORSCALE,
        colorbar=None,
        line=dict(width=1, color='white'),
        cmin=COLORBAR_MIN,
        cmax=COLORBAR_MAX
    ),
    text=[f"Cr: {a}% Fe: {b}% Ni: {c}%<br>{TARGET_ALPHA}: {val:.4f}<br>File: {fname}"
          for a, b, c, val, fname in zip(a_coords, b_coords, c_coords, alpha_values, df['filename'])],
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
                text='Cr',  # Top axis title
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
                text='Fe',  # Left axis title
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
                text='Ni',  # Right axis title
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

# Дополнительно: настройка шрифта для цветовой шкалы
fig.update_traces(
    marker=dict(
        colorbar=dict(
            title=dict(
                text=f'{TARGET_ALPHA} (T={TEMPERATURE}K)',
                font=dict(size=26, family="Arial", color="black")
            ),
            tickfont=dict(size=24, family="Arial", color="black")
        )
    ),
    selector=dict(type='scatterternary', marker_symbol='square')
)

# Отображение графика
fig.show()

# Можно также сохранить график в файл
pio.write_html(fig, f'{TARGET_ALPHA}_{TEMPERATURE}_{COORD_SPHERE}_18.08.html', auto_open=False)
pio.write_image(fig, f'{TARGET_ALPHA}_{TEMPERATURE}_{COORD_SPHERE}_18.08.svg')
# Сохранение графика в формате JPG с высоким качеством
pio.write_image(
    fig,
    file=f'{TARGET_ALPHA}_{TEMPERATURE}_{COORD_SPHERE}_18.08.jpg',
    format='jpg',
    scale=6,
    width=1200,
    height=800
)