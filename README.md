# Solid-state thermal gradients control chemical short-range order evolution in complex concentrated alloys

This repository contains the source data, computational input files, and experimental results for the article:  
**"Solid-state thermal gradients control chemical short-range order evolution in complex concentrated alloys"**  
*by Kirill Osintsev, Yuce Zhu, Vishnu Raghuraman, and Xizhang Chen.*

---

## Overview
This study investigates how solid-state cooling rates (achieved via Jominy end-quenching) influence the formation of Chemical Short-Range Order (SRO) in single-phase FCC complex concentrated alloys (CCAs). By generating a continuous spectrum of cooling rates within a single specimen, we spatially decouple the SRO contribution to electron scattering and macroscopic yield strength from conventional microstructural defects (grain boundaries, vacancies, and dislocations).

The repository provides all necessary data to reproduce the analytical modeling (NIMM), first-principles electronic structure calculations (MuST), atomistic simulations (LAMMPS), and experimental validations (electrical resistivity, micro-tensile tests, HRTEM, and XRD).

### Investigated Alloys (at.%)
*   **Fe60Ni20Cr20** (Low Ni/Cr concentration, highest relative SRO change due to thermal gradients)
*   **Fe34Ni33Cr33** (Moderate Ni/Cr concentration, moderate relative SRO change due to thermal gradients)
*   **Fe20Ni50Cr30** (High Ni/Cr concentration, lowest relative SRO change due to thermal gradients but transformation of SRO $\rightarrow$ to modulated structure)

---

## 📂 Repository Structure

All input files, raw data, and processing scripts are organized as follows:

### `01_Experimental_Data/`
Contains raw and processed experimental data organized by characterization method:
*   **Thermocouples/**: Contains `Cooling_curves.xlsx` with time-temperature data from K-type thermocouples positioned at 2.5 mm (Bottom), 45 mm (Middle), and 75 mm (Top) from the quenched end.
*   **XRD/**: Contains raw XRD patterns (`.txt`, `.xy`) and GSAS-II project files (`.gpx`) used for Rietveld refinement, organized by alloy and region (as-cast, top, middle, bottom).
*   **TEM/**: Contains TEM files for the Fe20Ni50Cr30 alloy (bottom and top regions) used for dislocation density caluclations which are saved in
the 'dislocation_density.xlsx' file.
*   **Electrical_Resistivity/**: Four-point probe measurements for all three alloys across the thermal gradient.
*   **Mechanical_Tests/**: Raw engineering stress-strain data from micro-tensile tests as well as the calculated mechanical properties.

### `02_Analytical_NIMM/`
Contains data from thermodynamic SRO predictions using Non-interacting molecule method.
*   For the standalone automated Python calculator used in this study, please visit:* [KirillOsintsev/SRO-parameters-calculator](https://github.com/KirillOsintsev/SRO-parameters-calculator)

### `03_Computational_MuST/`
Contains input files and outputs for first-principles **Multiple Scattering Theory (MuST)** calculations to ensure full reproducibility:
*   **KKR-CPA/**: Input files (`.inp`) for the random solid solution (RSS) baseline calculations.
*   **CA-CPA/**: Input files incorporating the specific SRO parameters obtained from the NIMM model.
*   **Magnetic_States/**: Total-energy minimization comparisons between Paramagnetic (PM) and Disordered Local Moment (DLM) states.
*   **DOS_Data/**: Calculated Density of States (DOS) at the Fermi level and Kubo-Greenwood residual resistivity data.

### `04_Media/`
*   **End_Quench_Videos/**: Video documentation of the water-jet quenching process.

### `05_Atomistic simulations/`
*   **Misfit volume calculations/**: Input and output files for the misfit volumes calculations obtained by atomistic simulations using
the Embedded-Atom-Method (EAM) and universal PET-MAD potentials.
---

## Software Requirements and Reproducibility

To ensure compliance with computational reproducibility standards, the following software packages and versions were used in this study. Input files for these programs are provided in their respective directories.

*   **MuST (Multiple Scattering Theory):** Ab initio electronic structure calculations and Kubo-Greenwood resistivity. [GitHub Repository](https://github.com/mstsuite/MuST).
*   **LAMMPS:** Used for molecular dynamics energy minimization to extract equilibrium lattice parameters, elastic constants, and misfit volumes.
*   **sqsgenerator:** Used to generate the SQS supercells for atomistic simulations. [sqsgenerator’s documentation](https://sqsgenerator.readthedocs.io/en/latest/)
*   **pySSpredict:** Open-source Python toolkit used for baseline solid-solution yield strength predictions. [GitHub Repository](https://github.com/Dongsheng-Wen/pySSpredict)
*   **GSAS-II:** Used for Rietveld refinement of the XRD patterns.
*   **Data Analysis & Plotting:** Python 3.8+ (`numpy`, `pandas`, `scipy`, `matplotlib`).
*   **ImageJ 1.53a:** Dislocation density calculations.

---

## 📖 Citation

If you use the data, models, or scripts provided in this repository, please cite our manuscript:

> Osintsev, K., Zhu, Y., Raghuraman, V., & Chen, X. (2026). *Solid-state thermal gradients control chemical short-range order evolution in complex concentrated alloys*. (Under Review).

---

## 📄 License
The data and custom scripts in this repository are licensed under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) license.
