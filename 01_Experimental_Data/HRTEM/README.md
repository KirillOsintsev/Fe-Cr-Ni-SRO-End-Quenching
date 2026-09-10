# TEM Image Processing and SRO Domain Reconstruction Pipeline

This directory contains high-resolution transmission electron microscopy (HRTEM) raw data (`.dm3` format) and the automated Python analysis pipeline used to study Short-Range Order (SRO) and structural modulations in the $\text{Fe}_{20}\text{Ni}_{50}\text{Cr}_{30}$ alloy across different zone axes.

---

## 📂 Directory Structure

The data is organized by specimen region and crystallographic zone axis:

```text
├── plot_ensemble_fft.py          # Main automated processing script
├── Fe20Ni50Cr30_bottom/
│   ├── 112_zone_axis/            # HRTEM images, matrix.csv, diffuse_peaks.csv, outputs
│   └── 111_zone_axis/            # HRTEM images, matrix.csv, SAED patterns
└── Fe20Ni50Cr30_top/
    ├── 112_zone_axis/            # HRTEM images, matrix.csv, satellite_peaks.csv, outputs
    └── 001_zone_axis/            # HRTEM images, matrix.csv, SAED patterns
```

* **`112_zone_axis`:** Used for detailed SRO domain extraction (bottom) and long-range modulated structure visualization (top) via Inverse Fast Fourier Transform (IFFT).
* **`111` and `001` zone axes:** Used for ensemble-averaged FFT analysis to verify the presence or absence of diffuse SRO scattering along alternative crystallographic projections.

---

## 🛠️ Software Prerequisites & Installation

To run the analysis script, you need Python 3.8+ and several scientific/image-processing libraries. We recommend setting up a dedicated conda environment:

1. **Create and activate a virtual environment:**
   ```bash
   conda create -n tem_analysis python=3.9
   conda activate tem_analysis
   ```

2. **Install required dependencies:**
   ```bash
   pip install numpy matplotlib opencv-python pandas scipy hyperspy
   ```
   *(Note: `hyperspy` is required for reading `.dm3` microscope files).*

---

## 🔬 Script Workflow (`plot_ensemble_fft.py`)

Due to the weak nature of SRO signals, individual HRTEM micrographs often suffer from a low Signal-to-Noise Ratio (SNR). This script overcomes this limitation through an ensemble-averaging and Fourier-filtering pipeline:

* **Tukey Windowing:** Applies a 2D Tukey window to raw `.dm3` images to minimize spectral leakage during Fourier transformation.
* **Crystallographic Alignment:** Automatically aligns all images in the frequency domain using reference matrix Bragg reflections (`matrix.csv`) via Enhanced Correlation Coefficient (ECC) maximization, preserving image phase.
* **Ensemble Averaging:** Computes the average Fast Fourier Transform (FFT) across multiple independent images to drastically enhance the signal-to-noise ratio of diffuse SRO features.
* **Streak Suppression:** Numerically suppresses high-intensity vertical and horizontal streaks originating from the central beam and matrix spots to prevent artifacts in real-space reconstructions.
* **Butterworth Band-Pass Filtering:** Applies a smooth 2D elliptical/circular Butterworth filter to isolate specific diffuse SRO peaks or satellite reflections (`*_peaks.csv`).
* **Inverse FFT (IFFT):** Reconstructs real-space images to visualize nanoscale SRO domains and modulated structures.

---

## 🚀 How to Run the Script

1. Navigate to the specific zone axis folder containing your `.dm3` files, `matrix.csv`, and the corresponding peak coordinate file (`*_peaks.csv`):
   ```bash
   cd Fe20Ni50Cr30_bottom/112_zone_axis/
   ```

2. Run the script using your python environment:
   ```bash
   python /path/to/plot_ensemble_fft.py
   ```

### Outputs Generated:
* `ensemble_fft_clean.jpg`: The noise-reduced, ensemble-averaged FFT pattern.
* `*_SRO_filtered.jpg`: Real-space IFFT reconstructions showing isolated SRO domains or modulated structures for each input image.
* `ensemble_fft_masked_for_paper.jpg`: Control image showing the Butterworth filter masks overlaid on the averaged FFT.