#!/bin/bash

# =================================================================
# НАСТРОЙКИ
# =================================================================
# Так как OMP не установлен, используем MPI для параллелизма
NUM_PROCS=8
LAMMPS_EXEC="lmp" 

# Проверка наличия исполняемого файла
if ! command -v "$LAMMPS_EXEC" &> /dev/null
then
    echo "Ошибка: Исполняемый файл LAMMPS ('$LAMMPS_EXEC') не найден."
    exit 1
fi

FILES=(*.data)
if [ ! -e "${FILES[0]}" ]; then
    echo "Ошибка: Файлы .data не найдены."
    exit 1
fi

echo "--- Начинаем пакетную минимизацию (MPI режим) ---"
echo "Найдено файлов: ${#FILES[@]}"

# =================================================================
# ЦИКЛ ОБРАБОТКИ
# =================================================================
for DATA_FILE in "${FILES[@]}"; do
    
    BASE_NAME=$(basename "$DATA_FILE" .data)
    
    echo ""
    echo "================================================================"
    echo "🛠️ ОБРАБОТКА: $DATA_FILE"
    echo "================================================================"

    IN_FILE="${BASE_NAME}_min.in"
    LOG_FILE="${BASE_NAME}_min.log"
    MIN_DATA="${BASE_NAME}_minimized.data"

    # Создание входного файла (БЕЗ команд OMP)
    cat > "$IN_FILE" << EOF
units metal
dimension 3
boundary p p p
atom_style atomic

log ${LOG_FILE}
read_data ${DATA_FILE}

mass 1 58.6934  # Ni
mass 2 55.845   # Fe
mass 3 51.9961  # Cr

pair_style metatomic pet-mad-latest.pt device cpu 
pair_coeff * * 28 26 24

neighbor 2.0 bin
neigh_modify delay 0 check yes
timestep 0.001

thermo 10
thermo_style custom step lx ly lz pe press fmax vol

# --- ЭТАПЫ МИНИМИЗАЦИИ ---
min_style cg
minimize 1.0e-8 1.0e-9 1000 5000

# Релаксация ячейки aniso
fix 1 all box/relax aniso 0.0 vmax 0.0001
min_style cg
minimize 1.0e-10 1.0e-11 1000 5000
unfix 1

# Промежуточная минимизация атомов
min_style cg
minimize 1.0e-10 1.0e-11 1000 5000

# Релаксация ячейки iso
fix 2 all box/relax iso 0.0 vmax 0.0001
min_style cg
minimize 1.0e-10 1.0e-11 1000 5000
unfix 2

variable lat_const equal "lx/5"
variable eatom equal "pe/count(all)"
variable teng equal "pe"
variable natoms equal "count(all)"

print "Lattice parameter (lx/5) = \${lat_const} A"
print "Total Potential Energy (PE) = \${teng} eV"
print "Number of atoms = \${natoms}"
print "Cohesive energy (PE/N) = \${eatom} eV"
print "Minimization completed."

write_data ${MIN_DATA}
EOF

    echo "   -> Запуск через MPI ($NUM_PROCS процессов)..."
    
    # Запуск через mpirun (так как MPI у вас в порядке)
    OMP_NUM_THREADS=$NUM_PROCS "$LAMMPS_EXEC" -in "$IN_FILE"

    if [ -f "$MIN_DATA" ]; then
        echo "   -> ✅ УСПЕХ: ${MIN_DATA} создан."
    else
        echo "   -> ❌ ОШИБКА в расчете $DATA_FILE"
    fi

done

echo ""
echo "--- Все задачи выполнены! ---"
