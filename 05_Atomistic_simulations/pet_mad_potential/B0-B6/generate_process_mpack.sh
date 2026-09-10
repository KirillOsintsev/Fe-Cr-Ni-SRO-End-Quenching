#!/bin/bash

# Настройки
ITERATIONS=12
LOG_FILE=".processed_jsons.log"
touch "$LOG_FILE"

echo "--- Запуск комплексной обработки SQS (JSON -> MPACK -> CIF -> DATA) ---"

# Проходим по всем .json файлам в текущей директории
for json_file in *.json; do
    [ -e "$json_file" ] || continue

    # Имя без расширения (например, B0)
    base_name="${json_file%.*}"
    
    # Проверка, обрабатывали ли этот JSON ранее (по желанию)
    if grep -fxq "$base_name" "$LOG_FILE"; then
        echo ">>> Пропуск: $json_file уже был полностью обработан."
        continue
    fi

    echo ">>> Обработка исходного файла: $json_file"
    
    # Создаем рабочую директорию
    mkdir -p "$base_name"
    cp "$json_file" "$base_name/"
    
    # Заходим в папку для генерации
    cd "$base_name" || exit

    for i in $(seq 1 $ITERATIONS); do
        echo "  [Шаг $i/$ITERATIONS] Генерация структуры..."
        
        # 1. Запускаем генерацию sqsgen
        sqsgen run -i "$json_file"

        # Определяем имя созданного mpack (может быть B0.mpack или sqs.mpack)
        mpack_out=""
        if [ -f "${base_name}.mpack" ]; then
            mpack_out="${base_name}.mpack"
        elif [ -f "sqs.mpack" ]; then
            mpack_out="sqs.mpack"
        fi

        if [ -n "$mpack_out" ]; then
            # Финальное имя для текущей итерации
            current_tag="${base_name}_${i}"
            
            # 2. Конвертация MPACK -> CIF
            # Чтобы sqsgen output сработал, файл должен называться sqs.mpack
            mv "$mpack_out" "sqs.mpack"
            sqsgen output structure -f cif
            
            # Переименовываем результат в итоговый mpack и cif
            mv "sqs.mpack" "${current_tag}.mpack"
            if [ -f "sqs-0-0.cif" ]; then
                mv "sqs-0-0.cif" "${current_tag}.cif"
                echo "    - Создан ${current_tag}.cif"
            else
                echo "    [!] Ошибка: CIF не создан для $current_tag"
                continue
            fi

            # 3. Конвертация CIF -> LAMMPS DATA
            echo "    - Запуск cif2cell для ${current_tag}.cif"
            cif2cell "${current_tag}.cif" -p lammps > /dev/null 2>&1

            # Поиск созданного .data файла
            generated_data=$(ls -t *.data 2>/dev/null | head -n 1)
            if [ -n "$generated_data" ]; then
                mv "$generated_data" "${current_tag}.data"
                echo "    [OK] Создан ${current_tag}.data"
            else
                echo "    [!] Ошибка: .data файл не найден для $current_tag"
            fi
            
            # Удаляем промежуточный .cif, если он больше не нужен (опционально)
            # rm "${current_tag}.cif"
            
        else
            echo "    [!] Ошибка: Выходной файл .mpack не найден на итерации $i"
        fi
    done

    # Возвращаемся в корень
    cd ..
    
    # Помечаем JSON как обработанный
    echo "$base_name" >> "$LOG_FILE"
    echo ">>> Завершена обработка $base_name. Результаты в папке ./$base_name"
    echo "------------------------------------------------"
done

echo "Все задачи выполнены!"