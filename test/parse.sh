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
    	time "$script" "$filename" "$output_data_file" "$configuration_file" -o "$@"
        first=false
    else
        time "$script" "$filename" "$output_data_file" "$configuration_file" "$@"
    fi
done

