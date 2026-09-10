pair_style eam/alloy
pair_coeff * * FeNiCr_bonny.eam.alloy Ni Fe Cr
neighbor 2.0 bin
neigh_modify delay 0 check yes
min_style cg
min_modify dmax ${dmax} line quadratic
thermo 1
thermo_style custom step temp pe press pxx pyy pzz pxy pxz pyz lx ly lz vol
thermo_modify norm no
