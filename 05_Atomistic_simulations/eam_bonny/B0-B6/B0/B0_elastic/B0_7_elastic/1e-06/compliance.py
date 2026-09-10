import numpy as np
from numpy.linalg import inv
import sys

# Search for the lines printed by LAMMPS
nvals = 9
valpos = 4
valstr = 'Elastic Constant C'
cindices = [(0,0),(1,1),(2,2),(0,1),(0,2),(1,2),(3,3),(4,4),(5,5)]

c = np.zeros((6,6))
found_count = 0

try:
    with open("log.lammps",'r') as f:
        for line in f:
            if valstr in line:
                words = line.split()
                # Expected format: Elastic Constant C11all = Value GPa
                if len(words) >= 6:
                    i1, i2 = cindices[found_count]
                    c[i1, i2] = float(words[4])
                    c[i2, i1] = c[i1, i2]
                    found_count += 1
                if found_count == nvals: break
    
    if found_count < nvals:
        print(f"Warning: Only found {found_count} constants.")

    print("\n--- C Tensor [GPa] ---")
    for row in c:
        print(" ".join([f"{x:10.4f}" for x in row]))

    # Compliance calculation (Voigt)
    c_v = np.copy(c)
    for i in range(6):
        for j in range(3,6): c_v[i,j] *= 2.0
    
    s = inv(c_v)
    for i in range(6):
        for j in range(3,6): s[i,j] *= 0.5
    
    print("\n--- S Tensor [1/GPa] ---")
    for row in s:
        print(" ".join([f"{x:12.6e}" for x in row]))
        
except Exception as e:
    print(f"Error: {e}")
