{\rtf1\ansi\ansicpg1251\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 This draft for your `README.md` is designed to be professional, clean, and useful for other researchers who want to reproduce your work or cite your data.\
\
***\
\
# Tailoring Short-Range Order in Fe-Cr-Ni Alloys by End-Quenching\
\
This repository contains the supplementary data, computational inputs, and experimental results for the study: \
**"Tailoring Short-Range Order in Fe-Cr-Ni Alloys by End-Quenching"** by Osintsev et al.\
\
## Project Overview\
This study investigates how different cooling rates (achieved via end-quenching) influence the formation of Short-Range Order (SRO) in complex concentrated alloys. We combine analytical modeling (NIMM), first-principles electronic structure calculations (MuST), and experimental validation (electrical resistivity, micro-tensile tests, and electron microscopy).\
\
### Studied Alloys (at.%)\
*   **Fe60Ni20Cr20** (Low SRO effect)\
*   **Fe34Ni33Cr33** (Moderate SRO effect)\
*   **Fe20Ni50Cr30** (High SRO effect)\
\
---\
\
## Repository Structure\
\
### `01_Experimental_Data/`\
*   **Cooling_Rates/**: CSV files containing time-temperature data from K-type thermocouples positioned at 2.5 mm (Bottom), 45 mm (Middle), and 75 mm (Top) from the quenched end.\
*   **Mechanical_Tests/**: Raw stress-strain data for as-cast and quenched samples used to generate Figure 7.\
*   **Electrical_Resistivity/**: Measurements for all three alloys at different positions, including standard deviation calculations.\
*   **XRD_EBSD/**: Raw XRD patterns (.ascii) and EBSD grain size distribution data.\
\
### `02_Computational_MuST/`\
Inputs and outputs for the **MuST (Multiple Scattering Theory)** code:\
*   **KKR-CPA/**: Inputs for the random solid solution state calculations.\
*   **CA-CPA/**: Inputs incorporating SRO parameters obtained from NIMM.\
*   **DOS_Data/**: Calculated Density of States (DOS) at the Fermi level ($E_F$) used to explain resistivity changes.\
\
### `03_Analytical_NIMM/`\
*   **SRO_Parameters/**: Warren-Cowley parameters ($\\alpha_1$) calculated for 841 compositions in the Fe-Ni-Cr space (350 K to 1500 K).\
*   **Strengthening_Model/**: Implementation of the solute strengthening theory used to predict the yield strength changes.\
*   *Note: For the standalone calculator code, see: [KirillOsintsev/SRO-parameters-calculator](https://github.com/KirillOsintsev/SRO-parameters-calculator)*\
\
### `04_Media/`\
*   **End_Quench_Videos/**: High-speed video documentation of the water-jet quenching process.\
*   **Sample_Photos/**: Images of the rod specimens, the Jominy-style holder, and the machined micro-tensile specimens.\
*   **Microscopy_HighRes/**: High-resolution SEM and EBSD maps showing single-phase stability and grain morphologies.\
\
### `05_Manuscript/`\
*   Pre-print version of the article and the formatted Supplementary Information PDF.\
\
---\
\
## Key Experimental Conditions\
| Parameter | Value |\
| :--- | :--- |\
| Homogenization Temp | 950 \'b0C (1223 K) |\
| Holding Time | 1 Hour |\
| Quench Medium | Water Jet |\
| Cooling Rates | 27.3 K/s (Bottom) to 0.6 K/s (Top) |\
| Tensile Strain Rate | $1 \\times 10^\{-3\} \\text\{ s\}^\{-1\}$ |\
\
## Software Requirements\
*   **MuST Code:** [GitHub Link](https://github.com/mstsuite/MuST) for electronic structure calculations.\
*   **GSAS-II:** Used for Rietveld refinement of XRD patterns.\
*   **Analysis Scripts:** Python 3.8+ (libraries: `numpy`, `pandas`, `matplotlib`).\
\
## Citation\
If you use this data or the models provided, please cite our work:\
> Osintsev, K., Yuce, Z., Raghuraman, V., & Chen, X.-Z. (2025). Tailoring Short-Range Order in Fe-Cr-Ni Alloys by End-Quenching. *Journal Name / Preprint DOI*.\
\
## License\
The data in this repository is licensed under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) license. Any code is provided under the MIT License.}