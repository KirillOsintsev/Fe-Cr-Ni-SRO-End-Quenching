#!/bin/bash

# Define the output file name
OUTPUT="elastic_results.csv"

# Write the header to the CSV file
echo "File_Name,Deformation,C11,C22,C33,C12,C13,C23,C44,C55,C66,C14,C15,C16,C24,C25,C26,C34,C35,C36,C45,C46,C56,Bulk_Modulus,Shear_Modulus,Young_Modulus,Poisson_Ratio" > $OUTPUT

echo "Starting extraction..."

# Find all folders ending in _elastic
for ELASTIC_DIR in *_elastic; do
    # Check if the directory exists
    [ -d "$ELASTIC_DIR" ] || continue
    
    # Get the system name (e.g., A0_10)
    SYS_NAME="${ELASTIC_DIR%_elastic}"

    # Loop through the strain subfolders
    for STRAIN_DIR in $(ls -d "$ELASTIC_DIR"/*/ 2>/dev/null); do
        # Extract the strain value (folder name)
        DEFORMATION=$(basename "$STRAIN_DIR")
        LOG_FILE="${STRAIN_DIR}lammps_out.log"

        if [ -f "$LOG_FILE" ]; then
            echo "Processing $ELASTIC_DIR folder $DEFORMATION..."

            # Function to extract numeric value after the '=' sign
            get_val() {
                grep "$1" "$LOG_FILE" | tail -1 | awk -F'=' '{print $2}' | awk '{print $1}'
            }

            # Extracting Cij constants
            C11=$(get_val "C11all")
            C22=$(get_val "C22all")
            C33=$(get_val "C33all")
            C12=$(get_val "C12all")
            C13=$(get_val "C13all")
            C23=$(get_val "C23all")
            C44=$(get_val "C44all")
            C55=$(get_val "C55all")
            C66=$(get_val "C66all")
            C14=$(get_val "C14all")
            C15=$(get_val "C15all")
            C16=$(get_val "C16all")
            C24=$(get_val "C24all")
            C25=$(get_val "C25all")
            C26=$(get_val "C26all")
            C34=$(get_val "C34all")
            C35=$(get_val "C35all")
            C36=$(get_val "C36all")
            C45=$(get_val "C45all")
            C46=$(get_val "C46all")
            C56=$(get_val "C56all")

            # Extracting Averaged Properties
            # These match the specific strings in your log file
            B=$(get_val "Bulk Modulus (B)")
            G=$(get_val "Shear Modulus (Voigt) (G)")
            E=$(get_val "Young Modulus (E)")
            NU=$(get_val "Poisson Ratio (nu)")

            # Append the data row to the CSV
            echo "$SYS_NAME,$DEFORMATION,$C11,$C22,$C33,$C12,$C13,$C23,$C44,$C55,$C66,$C14,$C15,$C16,$C24,$C25,$C26,$C34,$C35,$C36,$C45,$C46,$C56,$B,$G,$E,$NU" >> $OUTPUT
        else
            echo "Warning: No lammps_out.log found in $STRAIN_DIR"
        fi
    done
done

echo "Extraction complete! Results saved in $OUTPUT"