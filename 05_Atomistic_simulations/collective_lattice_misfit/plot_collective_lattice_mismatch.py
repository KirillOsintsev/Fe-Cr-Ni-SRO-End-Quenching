import matplotlib.pyplot as plt
import numpy as np

# Data from the provided image
alloys = ['Fe60Ni20Cr20', 'Fe34Ni33Cr33', 'Fe20Ni50Cr30']
methods = ["Vegard's Law", "EAM potential", "PET-MAD potential"]

# Data values (Collective Lattice Mismatch %)
data = {
    "Vegard's Law": [1.3532, 1.6552, 1.8172],
    "EAM potential": [1.3907, 1.5263, 1.3484],
    "PET-MAD potential": [1.7144, 1.9123, 1.6443]
}

# Plot configuration
x = np.arange(len(alloys))  # Label locations
width = 0.2               # Width of the bars
hatch_patterns = ['//', '\\\\', '..']  # Different hatching for each method

fig, ax = plt.subplots(figsize=(10, 6))

# Create bars for each method
for i, method in enumerate(methods):
    offset = (i - 1) * width  # Centers the group of bars
    ax.bar(x + offset, data[method], width, 
           label=method, 
           color='white',       # No color
           edgecolor='black',   # Black borders
           hatch=hatch_patterns[i], 
           linewidth=1.2)

# Customizing the axes
ax.set_ylabel('δ-parameter (%)', fontsize=16)
#ax.set_xlabel('Alloy Composition', fontsize=16)

# Заголовок смещаем чуть выше с помощью pad=35
#ax.set_title('The collective effect of the misfit volumes of all the elements in the alloy', fontsize=14, pad=35)
ax.set_xticks(x)
ax.set_xticklabels(alloys, fontsize=14)

# --- ЛЕГЕНДА НАВЕРХУ НАД ГРАФИКОМ ---
ax.legend(
    loc='lower center', 
    bbox_to_anchor=(0.5, 1.02),  # Помещает легенду сразу над осями графика
    ncols=3,                     # Располагает элементы в один ряд (для старых версий matplotlib: ncol=3)
    frameon=False,               # Убирает рамку легенды (по желанию)
    fontsize=14
)

# Add grid for better readability (optional, subtle)
ax.yaxis.grid(True, linestyle='--', alpha=0.6)

# Tight layout to ensure no clipping
plt.tight_layout()

# Saving the plots in the requested formats
plt.savefig('lattice_mismatch_chart.png', dpi=600)  # 600 DPI PNG
plt.savefig('lattice_mismatch_chart.svg')          # Vector SVG format

print("Plots saved successfully: 'lattice_mismatch_chart.png' and 'lattice_mismatch_chart.svg'")
plt.show()