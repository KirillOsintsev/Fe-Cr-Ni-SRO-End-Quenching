variable up equal 8e-06
variable atomjiggle equal 1.0e-5
units metal
variable cfac equal 1.0e-4
variable cunits string GPa
variable etol equal 1.0e-8     
variable ftol equal 1.0e-12     
variable maxiter equal 0.0     
variable maxeval equal 50000    
variable dmax equal 1.0e-2
boundary p p p
read_data A0_9_pet_minimized.data
mass 1 58.6934 # Ni 
mass 2 55.845  # Fe
mass 3 51.9961 # Cr
