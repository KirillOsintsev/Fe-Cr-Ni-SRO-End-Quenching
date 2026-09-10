#!/bin/bash

# Проходим по всем .json файлам
for file in *.json; do
    [ -e "$file" ] || continue

    # Имя без расширения (например, B0)
    filename="${file%.*}"
    
    # Создаем папку и копируем файл
    mkdir -p "$filename"
    cp "$file" "$filename/"

    echo "Начинаю обработку: $filename"
    
    # Заходим в папку
    cd "$filename" || exit

    for i in {1..12}; do
        # Запускаем генерацию
        sqsgen run -i "$file"

        # Проверяем, какой файл создался (B0.mpack или sqs.mpack)
        if [ -f "${filename}.mpack" ]; then
            mv "${filename}.mpack" "${filename}_${i}.mpack"
            echo "  [OK] Создан ${filename}_${i}.mpack"
        elif [ -f "sqs.mpack" ]; then
            mv "sqs.mpack" "${filename}_${i}.mpack"
            echo "  [OK] Создан ${filename}_${i}.mpack"
        else
            echo "  [!] Ошибка: Выходной файл не найден для $file на шаге $i"
            # Выведем список файлов, чтобы понять, что пошло не так
            ls -F
        fi
    done

    # Возвращаемся обратно
    cd ..
done

echo "Все задачи выполнены!"