"""
SRO Domain Reconstruction and FFT Averaging Script
--------------------------------------------------
This script processes a series of high-resolution TEM images (.dm3 format) to 
reconstruct Short-Range Order (SRO) domains using Fourier-filtering techniques. 

Workflow:
1. Applies a Tukey window to raw images to minimize spectral leakage.
2. Aligns all images in the frequency domain using matrix Bragg reflections.
3. Computes the ensemble-averaged Fast Fourier Transform (FFT) to enhance SNR.
4. Suppresses high-intensity matrix streaks to avoid imaging artifacts.
5. Applies a smooth Butterworth band-pass filter to isolate diffuse SRO peaks / satellite reflections.
6. Performs Inverse Fast Fourier Transform (IFFT) to visualize masked structure.

Required inputs: 
- A set of .dm3 files in the working directory.
- matrix.csv: Coordinates (Y, X) of the primary matrix Bragg reflections.
- *_peaks.csv: Coordinates (Y, X) of the diffuse SRO reflections / satellite_peaks to be filtered.
"""

import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import cv2
import pandas as pd
import hyperspy.api as hs
from scipy.signal import windows

# --- FILTERING PARAMETERS ---

#HALF_LONG_AXIS and HALF_SHORT_AXIS can be adjusted to get either circle or oval
#For the satellite peaks the radius is 9.36 px
"""
HALF_LONG_AXIS = 9.36       # Filter radius along the diffuse/satellite peaks (pixels)
HALF_SHORT_AXIS = 9.36      # Filter radius perpendicular to the peak (pixels)
"""
#For the diffuse peaks the radius is 20 px
HALF_LONG_AXIS = 20       # Filter radius along the diffuse/satellite peaks (pixels)
HALF_SHORT_AXIS = 20 

BUTTERWORTH_ORDER = 2       # Order of the Butterworth filter

# Artifact suppression parameters
STREAK_WIDTH = 4            # Width of the matrix streak mask (pixels)
# -----------------------------

# Output control flags
SAVE_ENSEMBLE_FFT = True    # Save the averaged FFT image
ANALYZE_SRO_PROFILE = False # Generate a 1D intensity profile across the SRO peak
# -----------------------------

def align_complex_fft(ref_mag, tgt_mag, tgt_complex):
    """
    Aligns the target FFT image to the reference FFT image using matrix reflections.
    Applies the resulting transformation to the complex array (preserving phase).
    """
    warp_mode = cv2.MOTION_EUCLIDEAN
    warp_matrix = np.eye(2, 3, dtype=np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6)
    
    ref_norm = cv2.normalize(ref_mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    tgt_norm = cv2.normalize(tgt_mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    ref_blur = cv2.GaussianBlur(ref_norm, (5, 5), 0)
    tgt_blur = cv2.GaussianBlur(tgt_norm, (5, 5), 0)
    
    try:
        _, warp_matrix = cv2.findTransformECC(ref_blur, tgt_blur, warp_matrix, warp_mode, criteria, inputMask=None, gaussFiltSize=5)
        
        real_part = np.real(tgt_complex)
        imag_part = np.imag(tgt_complex)
        
        h, w = ref_mag.shape
        aligned_real = cv2.warpAffine(real_part, warp_matrix, (w, h), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
        aligned_imag = cv2.warpAffine(imag_part, warp_matrix, (w, h), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
        
        aligned_complex = aligned_real + 1j * aligned_imag
        return aligned_complex, True
        
    except cv2.error:
        print(" Warning: Perfect FFT alignment failed. Using the original unaligned image.")
        return tgt_complex, False

def get_rotation_angle(center_data, spot_pos):
    cy, cx = center_data
    sy, sx = spot_pos
    dy, dx = sy - cy, sx - cx
    return np.arctan2(dy, dx) + np.pi / 2

def create_butterworth_elliptical_mask(shape, center_idx, angle, long_ax, short_ax, order=2):
    """ Generates a smooth 2D Butterworth band-pass filter mask. """
    h, w = shape
    cy, cx = int(center_idx[0]), int(center_idx[1])
    y_indices, x_indices = np.ogrid[:h, :w]
    dy, dx = y_indices - cy, x_indices - cx
    
    cos_a, sin_a = np.cos(-angle), np.sin(-angle)
    rot_x = dx * cos_a - dy * sin_a
    rot_y = dx * sin_a + dy * cos_a
    
    scaled_distance = np.sqrt((rot_x / long_ax)**2 + (rot_y / short_ax)**2)
    butterworth_mask = 1.0 / (1.0 + (scaled_distance)**(2 * order))
    return butterworth_mask.astype(np.float32)

def remove_matrix_streaks(fft_complex, matrix_spots, streak_width=4):
    """
    Numerically suppresses vertical and horizontal streaks originating from
    the central beam and primary matrix reflections to prevent IFFT artifacts.
    """
    h, w = fft_complex.shape
    streak_mask = np.ones((h, w), dtype=np.float32)
    half_w = streak_width // 2
    
    # Suppress central beam streaks
    cy, cx = h // 2, w // 2
    streak_mask[max(0, cy - half_w):min(h, cy + half_w + 1), :] = 0
    streak_mask[:, max(0, cx - half_w):min(w, cx + half_w + 1)] = 0
    
    # Suppress streaks from defined matrix reflections
    for sy, sx in matrix_spots:
        sy, sx = int(sy), int(sx)
        streak_mask[max(0, sy - half_w):min(h, sy + half_w + 1), :] = 0
        streak_mask[:, max(0, sx - half_w):min(w, sx + half_w + 1)] = 0
        
    return fft_complex * streak_mask, streak_mask

# =====================================================================
# MAIN EXECUTION
# =====================================================================

dm3_files = sorted(glob.glob("*.dm3"))
if not dm3_files:
    print("Error: No .dm3 files found in the directory."); exit()

if not os.path.exists("matrix.csv"):
    print("Error: matrix.csv not found."); exit()

sro_csv_candidates = glob.glob("*_peaks.csv")
if not sro_csv_candidates:
    print("Error: SRO diffuse peaks CSV not found."); exit()

sro_csv_path = sro_csv_candidates[0]
df_matrix = pd.read_csv("matrix.csv")
df_sro = pd.read_csv(sro_csv_path)

matrix_spots = [(row['Y'], row['X']) for _, row in df_matrix.iterrows()]

print(f"Found {len(dm3_files)} images. Initiating alignment and filtering pipeline...")

# 1. Load images and apply Tukey window
raw_complex_ffts = []
raw_mag_logs = []

for path in dm3_files:
    s = hs.load(path)
    img_data = s[0].data.astype(np.float32) if isinstance(s, list) else s.data.astype(np.float32)
    h, w = img_data.shape
    
    win_y = windows.tukey(h, alpha=0.1)
    win_x = windows.tukey(w, alpha=0.1)
    window_2d = np.outer(win_y, win_x)
    
    fft_shifted = np.fft.fftshift(np.fft.fft2(img_data * window_2d))
    mag_log = np.log(1 + np.abs(fft_shifted))
    
    raw_complex_ffts.append(fft_shifted)
    raw_mag_logs.append(mag_log)

# 2. Crystallographic Alignment
aligned_complex_ffts = [raw_complex_ffts[0]]
ref_mag_log = raw_mag_logs[0]
img_center = (h // 2, w // 2)

print("Aligning FFT patterns based on matrix reflections...")
for i in range(1, len(raw_complex_ffts)):
    aligned_complex, success = align_complex_fft(ref_mag_log, raw_mag_logs[i], raw_complex_ffts[i])
    aligned_complex_ffts.append(aligned_complex)

# 3. Calculate Ensemble-Averaged FFT
aligned_modules = [np.abs(c_fft) for c_fft in aligned_complex_ffts]
fft_amplitude_average = np.mean(aligned_modules, axis=0)
fft_mag_log = np.log(1 + fft_amplitude_average)

if SAVE_ENSEMBLE_FFT:
    plt.imsave("ensemble_fft_clean.jpg", fft_mag_log, cmap='gray')
    print(" -> [DONE] Averaged FFT saved as: ensemble_fft_clean.jpg")

# --- OPTIONAL: 1D SRO Intensity Profile Analysis ---
if ANALYZE_SRO_PROFILE and not df_sro.empty:
    print("Extracting 1D intensity profile across the SRO peak...")
    spot_y, spot_x = int(df_sro.iloc[0]['Y']), int(df_sro.iloc[0]['X'])
    cy, cx = img_center
    vector_y, vector_x = spot_y - cy, spot_x - cx
    length = np.sqrt(vector_y**2 + vector_x**2)
    dy, dx = vector_y / length, vector_x / length
    distances = np.arange(max(0, int(length - 30)), min(h//2, int(length + 30)))
    profile_intensities = [fft_amplitude_average[int(cy + d * dy), int(cx + d * dx)] for d in distances]
    
    plt.figure(figsize=(7, 3.5))
    plt.plot(distances, profile_intensities, 'r-+', label='SRO Intensity Profile')
    plt.axvline(x=length, color='blue', linestyle='--', label='Peak center (from CSV)')
    plt.title("1D Profile across SRO Diffuse Peak")
    plt.xlabel("Distance from central beam (pixels)")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.savefig("SRO_peak_profile_analysis.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(" -> [DONE] Profile plot saved as: SRO_peak_profile_analysis.png")

# 4. Generate Butterworth Masks
print("Generating Butterworth band-pass masks for SRO reflections...")
final_sro_mask = np.zeros((h, w), dtype=np.float32)

for _, row in df_sro.iterrows():
    spot_pos = (row['Y'], row['X'])
    if matrix_spots:
        distances = [np.sqrt((m[0]-spot_pos[0])**2 + (m[1]-spot_pos[1])**2) for m in matrix_spots]
        angle = get_rotation_angle(img_center, matrix_spots[np.argmin(distances)])
    else:
        angle = 0.0
        
    mask_ellipse = create_butterworth_elliptical_mask(
        fft_mag_log.shape, spot_pos, angle, 
        HALF_LONG_AXIS, HALF_SHORT_AXIS, order=BUTTERWORTH_ORDER
    )
    final_sro_mask = np.maximum(final_sro_mask, mask_ellipse)

# 5. Apply Masks and perform IFFT
print("Suppressing matrix streaks and computing local IFFTs...")
for idx, aligned_fft in enumerate(aligned_complex_ffts):
    fft_cleaned_streaks, streak_mask = remove_matrix_streaks(aligned_fft, matrix_spots, streak_width=STREAK_WIDTH)
    fft_final_filtered = fft_cleaned_streaks * final_sro_mask
    ifft_extracted = np.abs(np.fft.ifft2(np.fft.ifftshift(fft_final_filtered)))
    
    base_name = os.path.splitext(os.path.basename(dm3_files[idx]))[0]
    out_name = f"{base_name}_SRO_filtered.jpg"
    plt.imsave(out_name, ifft_extracted, cmap='gray')

# 6. Save Mask Visualization for manuscript/supplementary
fig, ax = plt.subplots(figsize=(6, 6))
ax.imshow(fft_mag_log, cmap='gray')
combined_viz = np.copy(final_sro_mask)
ax.imshow(combined_viz, cmap='jet', alpha=0.3)
ax.axis('off')
plt.savefig("ensemble_fft_masked_for_paper.jpg", dpi=600, bbox_inches='tight')
plt.close()

print("\n[SUCCESS] Image processing pipeline completed successfully.")