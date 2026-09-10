#!/bin/bash

# Имя выходного файла для сохранения таблицы
OUTPUT_FILE="final_minimization_summary_v4.txt"

echo "--- Сбор данных из файлов *.final.log (Версия 4: Добавлен Volume) ---"
# Обновленный заголовок таблицы: добавлено Volume
echo "----------------------------------------------------------------------------------------------------------------------------------------------------" | tee "$OUTPUT_FILE"
printf "| %-30s | %-12s | %-12s | %-12s | %-25s | %-28s | %-24s |\n" \
    "File Name (.in)" "Final Press" "Final Fmax" "Final Volume" "Lattice parameter (A)" "Total Potential Energy (eV)" "Cohesive Energy (eV/atom)" | tee -a "$OUTPUT_FILE"
echo "----------------------------------------------------------------------------------------------------------------------------------------------------" | tee -a "$OUTPUT_FILE"

# Итерация только по файлам, содержащим 'final' в имени
for LOG_FILE in *.log; do
    if [ -f "$LOG_FILE" ]; then
        
        IN_FILE=${LOG_FILE%.log}.in

        # 1. Извлечение финальных значений Press, Fmax и Volume (Термовывод)
        
        # Ищем последнюю строку термовывода (содержит step, lx, ly, lz, pe, press, fmax, vol)
        FINAL_THERMO_LINE=$(grep -E '^\s*[0-9]+\s+[0-9]' "$LOG_FILE" | tail -n 1) 

        if [ ! -z "$FINAL_THERMO_LINE" ]; then
            # Разделяем строку по пробелам и берем столбцы:
            # $6 (Press), $7 (Fmax), $8 (Volume)
            PRESS=$(echo "$FINAL_THERMO_LINE" | awk '{print $6}')
            FMAX=$(echo "$FINAL_THERMO_LINE" | awk '{print $7}')
            VOLUME=$(echo "$FINAL_THERMO_LINE" | awk '{print $8}') # <--- НОВЫЙ СТОЛБЕЦ
        else
            PRESS="N/A"
            FMAX="N/A"
            VOLUME="N/A"
        fi

        # 2. ИСПРАВЛЕННОЕ ИЗВЛЕЧЕНИЕ ПЕРЕМЕННЫХ (Lattice parameter, PE, Cohesive energy)
        # Используем $(NF-1) для получения предпоследнего столбца (числового значения)
        
        # Lattice parameter
        LAT_PARAM=$(grep "Lattice parameter (lx/5) =" "$LOG_FILE" | grep -E 'A$' | tail -n 1 | awk '{print $(NF-1)}')
        
        # Total Potential Energy
        PE_TOTAL=$(grep "Total Potential Energy (PE) =" "$LOG_FILE" | grep -E 'eV$' | tail -n 1 | awk '{print $(NF-1)}')
        
        # Cohesive energy
        PE_COHESIVE=$(grep "Cohesive energy (PE/N) =" "$LOG_FILE" | grep -E 'eV$' | tail -n 1 | awk '{print $(NF-1)}')
        
        # Проверяем на пустые значения
        if [ -z "$LAT_PARAM" ]; then LAT_PARAM="N/A"; fi
        if [ -z "$PE_TOTAL" ]; then PE_TOTAL="N/A"; fi
        if [ -z "$PE_COHESIVE" ]; then PE_COHESIVE="N/A"; fi


        # 3. Вывод результата (Обновленный формат)
        printf "| %-30s | %-12s | %-12s | %-12s | %-25s | %-28s | %-24s |\n" \
            "$IN_FILE" "$PRESS" "$FMAX" "$VOLUME" "$LAT_PARAM" "$PE_TOTAL" "$PE_COHESIVE" | tee -a "$OUTPUT_FILE"
    fi
done

echo "----------------------------------------------------------------------------------------------------------------------------------------------------" | tee -a "$OUTPUT_FILE"
echo ""
echo "✅ Сбор данных завершен. Результаты сохранены в файле '$OUTPUT_FILE'."
