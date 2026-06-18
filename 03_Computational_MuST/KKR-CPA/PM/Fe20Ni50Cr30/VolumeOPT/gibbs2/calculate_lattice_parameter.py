#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 17:46:05 2025

@author: osintsevkirill
"""

import os
import glob
import subprocess
import re
import math

def calculate_average_atomic_mass(alloy_name):
    """
    Рассчитывает среднюю атомную массу на основе имени сплава.
    Пример: Fe54Ni26Cr20 -> 55.82 г/моль.
    
    ВНИМАНИЕ: Эта функция должна быть адаптирована, если состав сплава
    не может быть извлечен из имени файла (например, если имя - 'PhaseA').
    Для примера используем состав Fe54Ni26Cr20.
    """
    # Предполагаем, что для вашего рабочего процесса это фиксированный состав
    # или что вы передадите его явно.
    # Если вы хотите, чтобы код извлекал состав из имени (например, 'Fe54Ni26Cr20'):
    
    # 1. Извлечение элементов и долей (упрощенный пример)
    composition_matches = re.findall(r'([A-Z][a-z]*)(\d+)', alloy_name)
    
    if not composition_matches:
        print(f"ВНИМАНИЕ: Не удалось извлечь состав из имени '{alloy_name}'. Использую фиксированный состав Fe54Ni26Cr20.")
        composition = [('Fe', 54), ('Ni', 26), ('Cr', 20)]
    else:
        composition = [(elem, int(perc)) for elem, perc in composition_matches]

    # 2. Атомные массы (г/моль)
    atomic_masses = {
        'Fe': 55.845,
        'Ni': 58.693,
        'Cr': 51.996,
        'Nb': 92.906, # Добавляем для примера, если вдруг понадобится
        'Co': 58.933,
        'Mn': 54.938,
    }

    total_percentage = sum(p for _, p in composition)
    if total_percentage == 0:
         return 56.0 # Значение по умолчанию

    average_mass = 0.0
    for element, percentage in composition:
        mass = atomic_masses.get(element, 0.0)
        average_mass += (percentage / total_percentage) * mass
        
    return average_mass

def process_collected_data():
    """
    Ищет файл collected_data_{name}.txt, обрабатывает его,
    запускает gibbs2 и переименовывает выходной файл.
    """
    # 1. Поиск входного файла
    
    # Ищем все файлы, соответствующие шаблону
    files = glob.glob("collected_data_*.txt")
    
    if not files:
        print("Ошибка: В текущей директории не найден файл 'collected_data_*.txt'.")
        return

    input_file_path = files[0]
    
    # Извлекаем имя сплава (name)
    base_name = os.path.basename(input_file_path)
    alloy_name = base_name.replace("collected_data_", "").replace(".txt", "")
    print(f"--- Обнаружен сплав: {alloy_name} ---")

    dat_file = f"{alloy_name}.dat"
    ing_file = f"{alloy_name}.ing"
    out_file = f"{alloy_name}.out"
    
    # 2. Обработка .txt и создание .dat
    
    volume_energy_data = []
    
    with open(input_file_path, 'r') as infile:
        
        # 1. Пропускаем строку заголовка
        infile.readline()
        
        for line in infile:
            # line.strip() удаляет пробелы в начале и конце
            # re.split('\\s+', ...) разбивает строку по ЛЮБОМУ количеству пробелов
            # После удаления '|' остается только пробельный разделитель
            
            # Сначала удаляем символы '|' и заменим их одним пробелом
            clean_line = line.replace('|', ' ').strip()
            
            # Затем разбиваем строку по любому количеству пробелов
            parts = re.split(r'\s+', clean_line)
            
            # parts теперь содержит 4 элемента (для строк с данными)
            if len(parts) >= 4:
                # Столбец 2 (индекс 1) - Average atomic volume (au^3)
                volume = parts[1]
                # Столubец 4 (индекс 3) - Total energy (Ry)
                energy = parts[3]
                
                # Добавляем данные в желаемом формате "объем энергия"
                volume_energy_data.append(f"{volume} {energy}")
            # else:
            #     Строка пуста или не содержит данных, игнорируем
            
    with open(dat_file, 'w') as outfile:
        outfile.write('\n'.join(volume_energy_data) + '\n')
    print(f"Создан файл данных: {dat_file}")

    # 3. Создание .ing файла
    
    # Рассчитываем среднюю атомную массу (для примера)
    mean_mass = calculate_average_atomic_mass(alloy_name)
    
    ing_content = f"""title {alloy_name}
mm {mean_mass:.4f}
vfree 1

phase BM3 file {dat_file} \\
units energy ry \\
fit strain bm 3


end
"""
    with open(ing_file, 'w') as outfile:
        outfile.write(ing_content)
    print(f"Создан входной файл GIBBS2: {ing_file}")
    
    # 4. Запуск gibbs2
    
    print(f"\n--- Запуск gibbs2: gibbs2 -n {ing_file} {out_file} ---")
    try:
        # -n: suppresses all auxiliary files except the primary output written to {name}.out
        result = subprocess.run(
            ['gibbs2', '-n', ing_file, out_file],
            check=True,
            capture_output=True,
            text=True
        )
        print("GIBBS2 успешно завершен.")
        
    except FileNotFoundError:
        print("\nОШИБКА: Команда 'gibbs2' не найдена. Убедитесь, что она установлена и добавлена в PATH.")
        return
    except subprocess.CalledProcessError as e:
        print(f"\nОШИБКА GIBBS2: Программа завершилась с ошибкой.")
        print(f"Stdout:\n{e.stdout}")
        print(f"Stderr:\n{e.stderr}")
        return

    # 5. Извлечение данных и переименование
    
    equilibrium_volume = None
    
    with open(out_file, 'r') as f:
        for line in f:
            if "Static equilibrium volume (bohr^3):" in line:
                # Используем регулярное выражение для извлечения числа
                match = re.search(r"(\d+\.\d+)", line)
                if match:
                    equilibrium_volume = float(match.group(1))
                    break
    
    if equilibrium_volume is None:
        print(f"ПРЕДУПРЕЖДЕНИЕ: Не удалось найти 'Static equilibrium volume' в {out_file}. Переименование пропущено.")
        return

    # Расчет параметра решетки (a) из атомного объема (V_atom)
    # Предполагаем, что это кубическая структура (FCC), где Z=4 атома на ячейку.
    Z = 4 # Атомов в ГЦК ячейке
    a_bohr = math.pow(equilibrium_volume * Z, 1/3)
    
    # Форматирование значения для имени файла
    a_bohr_str = f"{a_bohr:.4f}".replace('.', '_')
    new_out_file = f"{alloy_name}_{a_bohr_str}.out"
    
    os.rename(out_file, new_out_file)
    
    print(f"\n--- Результат ---")
    print(f"Равновесный объем (V_atom): {equilibrium_volume:.4f} bohr^3")
    print(f"Равновесный параметр решетки (a): {a_bohr:.4f} bohr")
    print(f"Файл переименован в: {new_out_file}")

if __name__ == "__main__":
    process_collected_data()