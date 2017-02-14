#!/bin/bash

script="../convert.py"
input_data_directory="./idata"
output_data_file="./odata/out.dat"
configuration_file="./grapeipm.cfg"

inputfiles=("$input_data_directory"/*.dat)
#inputfiles=(
#	'./idata/AHSPP_Min15.dat'
#	'./idata/AHSENV_Min15.dat'
#		)

first=true
for filename in "${inputfiles[@]}"; do
    if [ "$first" = true ] ; then
    	time "$script" "$configuration_file" -i "$filename" -o "$output_data_file" -w "$@"
        first=false
    else
    	time "$script" "$configuration_file" -i "$filename" -o "$output_data_file" "$@"
    fi
done

