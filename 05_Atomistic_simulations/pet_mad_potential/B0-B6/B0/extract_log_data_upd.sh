#!/bin/bash

# Имя выходного файла для сохранения таблицы
OUTPUT_FILE="final_minimization_summary_v6.txt"
TEMP_DATA="temp_stats.tmp" 

echo "--- Сбор данных из файлов *.log (Округление до 6 знаков) ---"

# Настройка ширины колонок для корректного отображения 6 знаков
# Имя файла(25) + 7 колонок по 15 символов каждая
HEADER_LINE="--------------------------------------------------------------------------------------------------------------------------------------------------"
echo "$HEADER_LINE" | tee "$OUTPUT_FILE"
printf "| %-25s | %-15s | %-15s | %-15s | %-15s | %-15s | %-15s | %-15s |\n" \
    "File Name (.in)" "Press" "Fmax" "Volume" "Vol/atom" "Lat Param" "Total PE" "Coh Energy" | tee -a "$OUTPUT_FILE"
echo "$HEADER_LINE" | tee -a "$OUTPUT_FILE"

> "$TEMP_DATA"

for LOG_FILE in *.log; do
    if [ -f "$LOG_FILE" ]; then
        IN_FILE=${LOG_FILE%.log}.in

        FINAL_THERMO_LINE=$(grep -E '^\s*[0-9]+\s+[0-9]' "$LOG_FILE" | tail -n 1) 

        if [ ! -z "$FINAL_THERMO_LINE" ]; then
            PRESS=$(echo "$FINAL_THERMO_LINE" | awk '{print $6}')
            FMAX=$(echo "$FINAL_THERMO_LINE" | awk '{print $7}')
            VOLUME=$(echo "$FINAL_THERMO_LINE" | awk '{print $8}')
            VOL_ATOM=$(awk "BEGIN {printf \"%.10f\", $VOLUME / 500}")
        else
            PRESS="0"; FMAX="0"; VOLUME="0"; VOL_ATOM="0"
        fi

        LAT_PARAM=$(grep "Lattice parameter (lx/5) =" "$LOG_FILE" | grep -E 'A$' | tail -n 1 | awk '{print $(NF-1)}')
        PE_TOTAL=$(grep "Total Potential Energy (PE) =" "$LOG_FILE" | grep -E 'eV$' | tail -n 1 | awk '{print $(NF-1)}')
        PE_COHESIVE=$(grep "Cohesive energy (PE/N) =" "$LOG_FILE" | grep -E 'eV$' | tail -n 1 | awk '{print $(NF-1)}')

        # Проверка на пустоту
        [[ -z "$LAT_PARAM" ]] && LAT_PARAM="0"
        [[ -z "$PE_TOTAL" ]] && PE_TOTAL="0"
        [[ -z "$PE_COHESIVE" ]] && PE_COHESIVE="0"

        # Запись во временный файл
        echo "$PRESS $FMAX $VOLUME $VOL_ATOM $LAT_PARAM $PE_TOTAL $PE_COHESIVE" >> "$TEMP_DATA"

        # Печать строки с точностью 6 знаков
        printf "| %-25s | %-15.6f | %-15.6f | %-15.6f | %-15.6f | %-15.6f | %-15.6f | %-15.6f |\n" \
            "$IN_FILE" "$PRESS" "$FMAX" "$VOLUME" "$VOL_ATOM" "$LAT_PARAM" "$PE_TOTAL" "$PE_COHESIVE" | tee -a "$OUTPUT_FILE"
    fi
done

echo "$HEADER_LINE" | tee -a "$OUTPUT_FILE"

# Расчет статистики с точностью 6 знаков
awk '
{
    for(i=1; i<=NF; i++) {
        sum[i] += $i;
        sumsq[i] += ($i)^2;
    }
    n++;
}
END {
    printf "| %-25s ", "AVERAGE";
    for(i=1; i<=NF; i++) {
        avg = sum[i]/n;
        printf "| %-15.6f ", avg;
    }
    printf "|\n";

    printf "| %-25s ", "STDEV";
    for(i=1; i<=NF; i++) {
        avg = sum[i]/n;
        variance = (sumsq[i]/n) - (avg^2);
        stdev = (variance > 0) ? sqrt(variance) : 0;
        printf "| %-15.6f ", stdev;
    }
    printf "|\n";
}' "$TEMP_DATA" | tee -a "$OUTPUT_FILE"

echo "$HEADER_LINE" | tee -a "$OUTPUT_FILE"

rm "$TEMP_DATA"

echo "✅ Готово. Данные с точностью 6 знаков сохранены в '$OUTPUT_FILE'."