import json
from pathlib import Path

# Импортируем только нужные функции
from calculate_sro_parameters import ternary_sro_pair
from normalized_sro_parameters import calculate_normalized_sro_parameters
from normalized_sro_screening import save_normalized_sro_parameters

def main():
    # 1. Настройка путей
    base_dir = Path("/Users/osintsevkirill/Yandex.Disk.localized/Science/Postdoc_project/Fe-Cr-Ni-SRO-End-Quenching/02_Analytical_NIMM/Fe20Ni50Cr30")
    alloy_name = "Fe20Ni50Cr30"
    
    fugacity_file = base_dir / f"{alloy_name}_fugacity_results.txt"
    misfit_file = base_dir / f"{alloy_name}_misfit_volumes_results.txt"
    sro_out_file = base_dir / f"{alloy_name}_sro_results.json"
    prob_out_file = base_dir / f"{alloy_name}_pair_probabilities.json"
    norm_sro_txt_file = base_dir / f"{alloy_name}_normalized_sro_parameters.txt"  # FIX 1: Добавили путь!
    
    # 2. Параметры сплава Fe20Ni50Cr30
    components = ['Fe', 'Ni', 'Cr']
    concentrations = [0.20, 0.50, 0.30] 
    composition = {'Fe': 0.20, 'Ni': 0.50, 'Cr': 0.30}
    phase = "fcc"
    
    # 3. Загрузка результатов фугитивности
    print(f"Читаем фугитивность из: {fugacity_file}")
    with open(fugacity_file, 'r') as f:
        fugacity_results = json.load(f)

    # 4. Расчет SRO параметров СТРОГО через ternary_sro_pair
    print("\n--- Рассчитываем SRO параметры (ternary_sro_pair) ---")
    sro_parameters = ternary_sro_pair(
        fugacity_results=fugacity_results,
        concentrations=concentrations,
        components=components,
        probabilities_output_file=str(prob_out_file)
    )

    # Сохраняем sro_results.json
    with open(sro_out_file, 'w') as f:
        json.dump(sro_parameters, f, indent=4)
    print(f"Файл сохранен: {sro_out_file}")

    # 5. Расчет нормализованных SRO метрик
    print("\n--- Рассчитываем нормализованные SRO метрики ---")
    averages = calculate_normalized_sro_parameters(
        sro_parameters=sro_parameters,
        sro_output_file=str(sro_out_file),
        misfit_volume_file=str(misfit_file),
        phase=phase,
        composition=composition,
        alloy_path=base_dir,
        alloy_name=alloy_name
    )

    # FIX 2: Убираем дублирующую букву 'K' из ключей (чтобы в файле не было '1000KK')
    clean_averages = {
        temp.replace('K', ''): metrics 
        for temp, metrics in averages.items()
    }

    # 6. Сохранение файла normalized_sro с помощью save_normalized_sro_parameters
    print(f"\n--- Сохраняем {norm_sro_txt_file.name} ---")
    save_normalized_sro_parameters(clean_averages, norm_sro_txt_file)

    print("Готово! Все файлы успешно пересчитаны и перезаписаны.")

if __name__ == "__main__":
    main()