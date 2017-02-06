#!/bin/bash

input_data_directory="./idata"
output_data_file="./odata/out.dat"
configuration_file="./grapeipm.cfg"

first=true
for filename in "$input_data_directory"/*.dat; do
    if [ "$first" = true ] ; then
    	time ./convert.py "$filename" "$output_data_file" "$configuration_file" -o "$@"
        first=false
    else
        time ./convert.py "$filename" "$output_data_file" "$configuration_file" "$@"
    fi
done

