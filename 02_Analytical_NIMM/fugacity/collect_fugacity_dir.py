import shutil
from pathlib import Path
from shutil import SameFileError

# Укажите вашу корневую папку с результатами
base_dir = Path(
    "/Users/osintsevkirill/Yandex.Disk.localized/Science/Postdoc_project/Fe-Cr-Ni-SRO-End-Quenching/02_Analytical_NIMM"
)

# Папка, куда копируем все json‑файлы
target_dir = base_dir / "all_fugacity_results"
target_dir.mkdir(exist_ok=True)

# Ищем во всех подпапках файлы, оканчивающиеся на '_sro_results.json'
for json_file in base_dir.rglob("*_fugacity_results.txt"):
    # пропускаем файлы, которые уже лежат в целевой папке
    if json_file.parent.resolve() == target_dir.resolve():
        continue

    dest = target_dir / json_file.name
    try:
        shutil.copy2(json_file, dest)
        print(f"Скопирован: {json_file} → {dest}")
    except SameFileError:
        # на всякий случай — если пути совпадают, просто пропустим
        print(f"Пропущен (уже на месте): {json_file}")

print("Готово. Все файлы собраны в", target_dir)
