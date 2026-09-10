#!/bin/bash

# Файл для хранения истории обработанных файлов
LOG_FILE=".processed_files.log"

# Создаем лог-файл, если его еще нет
touch "$LOG_FILE"

# Цикл по всем файлам с расширением .mpack в текущей папке
for file in *.mpack; do
    
    # Проверка на случай, если файлов нет
    [ -e "$file" ] || continue

    # Пропускаем файл, если он называется sqs.mpack (наш временный файл)
    if [ "$file" == "sqs.mpack" ]; then
        continue
    fi

    # Проверяем, обрабатывали ли мы этот файл ранее
    if grep -fxq "$file" "$LOG_FILE"; then
        echo "Пропуск: $file уже был обработан."
        continue
    fi

    echo "--- Обработка файла: $file ---"

    # Сохраняем имя без расширения (например, A1_1)
    filename_no_ext="${file%.*}"

    # 1. Переименовываем исходный файл в sqs.mpack
    mv "$file" "sqs.mpack"

    # 2. Запускаем sqsgen
    # Создает файл sqs-0-0.cif
    echo "Запуск sqsgen..."
    sqsgen output structure -f cif

    # 3. Возвращаем имена файлам
    # sqs.mpack -> A1_1.mpack
    # sqs-0-0.cif -> A1_1.cif
    mv "sqs.mpack" "$file"
    if [ -f "sqs-0-0.cif" ]; then
        mv "sqs-0-0.cif" "${filename_no_ext}.cif"
    else
        echo "Ошибка: sqs-0-0.cif не был создан."
        continue
    fi

    # 4. Запускаем cif2cell
    # Генерирует файл lammps (обычно с расширением .data или специфичным именем)
    echo "Запуск cif2cell..."
    cif2cell "${filename_no_ext}.cif" -p lammps

    # 5. Переименовываем результат cif2cell в *.data
    # Ищем самый свежий созданный файл .data (если имя заранее неизвестно)
    # Или, если cif2cell всегда создает файл с конкретным именем, лучше указать его.
    # Большинство версий cif2cell создают файл 'A1_1.data' или 'out.data'
    # Находим созданный .data файл и приводим к нужному имени:
    generated_data=$(ls -t *.data 2>/dev/null | head -n 1)
    if [ -n "$generated_data" ]; then
        mv "$generated_data" "${filename_no_ext}.data"
        echo "Создан файл: ${filename_no_ext}.data"
    fi

    # Записываем файл в лог обработанных
    echo "$file" >> "$LOG_FILE"
    echo "Завершено: $file"
    echo "----------------------------"

done

echo "Все новые файлы обработаны."
