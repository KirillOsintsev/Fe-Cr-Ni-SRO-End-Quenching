#!/bin/bash
# @Xin Liu, xin.liu@epfl.ch

set -o nounset # Treat unset variables as an error

/home/max/miniconda3/envs/lammps-env/bin/mpirun -np 6 python3.7 \
    calculate_1st_S-S_interaction_by_pressure_relaxation.py \
    /media/sf_host/Project/data/input/potentials/average_potentials/Fe51Ni22Cr27.averaged.eam.alloy \
    X Fe Ni 5 3.52 eam/alloy > log12.txt

/home/max/miniconda3/envs/lammps-env/bin/mpirun -np 6 python3.7 \
    calculate_1st_S-S_interaction_by_pressure_relaxation.py \
    /media/sf_host/Project/data/input/potentials/average_potentials/Fe51Ni22Cr27.averaged.eam.alloy \
    X Fe Fe 5 3.52 eam/alloy > log11.txt

/home/max/miniconda3/envs/lammps-env/bin/mpirun -np 6 python3.7 \
    calculate_1st_S-S_interaction_by_pressure_relaxation.py \
    /media/sf_host/Project/data/input/potentials/average_potentials/Fe51Ni22Cr27.averaged.eam.alloy \
    X Ni Ni 5 3.52 eam/alloy > log22.txt
