import json
import re
from pathlib import Path

# Импортируем только нужные функции
from calculate_sro_parameters import ternary_sro_pair
from normalized_sro_parameters import calculate_normalized_sro_parameters
from normalized_sro_screening import save_normalized_sro_parameters


def parse_alloy_name(folder_name):
    """
    Разбирает имя папки вида 'Fe20Ni50Cr30' на:
    - components: ['Fe', 'Ni', 'Cr']
    - concentrations: [0.20, 0.50, 0.30]
    - composition: {'Fe': 0.20, 'Ni': 0.50, 'Cr': 0.30}
    """
    # Регулярное выражение ищет пары ХимическийЭлемент + Число
    matches = re.findall(r'([A-Z][a-z]?)(\d+)', folder_name)
    if not matches:
        return None, None, None

    components = []
    concentrations = []
    composition = {}

    for elem, conc_str in matches:
        components.append(elem)
        conc_val = float(conc_str) / 100.0  # Переводим проценты в доли
        concentrations.append(conc_val)
        composition[elem] = conc_val

    return components, concentrations, composition


def process_alloy_folder(alloy_dir, phase="fcc"):
    alloy_name = alloy_dir.name
    
    # Извлекаем состав из имени папки
    components, concentrations, composition = parse_alloy_name(alloy_name)
    if not components or len(components) != 3:
        print(f"\n[SKIP] Пропущена папка '{alloy_name}': не является тройным сплавом или некорректное имя.")
        return

    fugacity_file = alloy_dir / f"{alloy_name}_fugacity_results.txt"
    misfit_file = alloy_dir / f"{alloy_name}_misfit_volumes_results.txt"
    sro_out_file = alloy_dir / f"{alloy_name}_sro_results.json"
    prob_out_file = alloy_dir / f"{alloy_name}_pair_probabilities.json"
    norm_sro_txt_file = alloy_dir / f"{alloy_name}_normalized_sro_parameters.txt"

    # Проверяем наличие входного файла с фугитивностью
    if not fugacity_file.exists():
        print(f"\n[SKIP] Пропущена папка '{alloy_name}': файл {fugacity_file.name} не найден.")
        return

    print(f"\n==================================================")
    print(f"Обработка сплава: {alloy_name}")
    print(f"Компоненты: {components}, Концентрации: {concentrations}")
    print(f"==================================================")

    # 1. Загрузка результатов фугитивности
    print(f"Читаем фугитивность из: {fugacity_file.name}")
    with open(fugacity_file, 'r') as f:
        fugacity_results = json.load(f)

    # 2. Расчет SRO параметров СТРОГО через ternary_sro_pair
    print("Рассчитываем SRO параметры (ternary_sro_pair)...")
    sro_parameters = ternary_sro_pair(
        fugacity_results=fugacity_results,
        concentrations=concentrations,
        components=components,
        probabilities_output_file=str(prob_out_file)
    )

    # Сохраняем sro_results.json
    with open(sro_out_file, 'w') as f:
        json.dump(sro_parameters, f, indent=4)
    print(f"Файл сохранен: {sro_out_file.name}")

    # 3. Расчет нормализованных SRO метрик
    print("Рассчитываем нормализованные SRO метрики...")
    averages = calculate_normalized_sro_parameters(
        sro_parameters=sro_parameters,
        sro_output_file=str(sro_out_file),
        misfit_volume_file=str(misfit_file),
        phase=phase,
        composition=composition,
        alloy_path=alloy_dir,
        alloy_name=alloy_name
    )

    # Убираем дублирующую букву 'K' из температурных ключей
    clean_averages = {
        temp.replace('K', ''): metrics 
        for temp, metrics in averages.items()
    }

    # 4. Сохранение файла normalized_sro с помощью save_normalized_sro_parameters
    print(f"Сохраняем {norm_sro_txt_file.name}...")
    save_normalized_sro_parameters(clean_averages, norm_sro_txt_file)
    print(f"[УСПЕШНО] Сплав {alloy_name} обработан.")


def main():
    root_dir = Path("/Users/osintsevkirill/Yandex.Disk.localized/Science/Postdoc_project/Fe-Cr-Ni-SRO-End-Quenching/02_Analytical_NIMM")
    phase = "fcc"  # Укажите фазу для сплавов ("fcc" или "bcc")

    if not root_dir.exists():
        print(f"Ошибка: Директория {root_dir} не существует!")
        return

    # Находим все подпапки в корневой директории
    alloy_folders = [p for p in root_dir.iterdir() if p.is_dir()]
    print(f"Найдено папок для проверки: {len(alloy_folders)}")

    for alloy_dir in sorted(alloy_folders):
        try:
            process_alloy_folder(alloy_dir, phase=phase)
        except Exception as e:
            print(f"[ОШИБКА] Не удалось обработать папку {alloy_dir.name}: {e}")

    print("\n==================================================")
    print("Все доступные папки успешно обработаны!")
    print("==================================================")


if __name__ == "__main__":
    main()