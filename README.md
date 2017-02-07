# grapeipm_support
This repository contains support scripts for merging file formats generated by Campbell Scientific remote weather sensors. 

-------------------------------------------------------------------------------

"convert.py" is a Python script used to parse time series weather data from loggernet files generated by 
Campbell Scientific remote weather sensors into a unified format specified in a configuration file.
In addition to modifying the general format of this data, it permits merging of such data into a single output file given a set of input files.
"convert.py -h" will display detailed usage. 

The more specific aspects of parsing data from a given sensor are specified in a required configuration file.
The configuration file specifies the target format of the processed data as well as the specific handling of data from any sensor.

"parse.sh" is provided an example of more broad usage. It iterates over files in "/idata/" which carry the ".dat" file extension, 
processing each and storing the results in a single output file "/odata/out.dat" relying on the specifications of the example configuration file "grapeipm.cfg".
"parse.sh" will create a new output file containing the results of all input files by specifying the "-o" option for the first input file parsed. 
Additional options which affect how "convert.py" is run can also be specified to "parse.sh" such as the start and end times to consider relevant to parsing. 

-------------------------------------------------------------------------------

"grapeipm.cfg" is an example configuration file sufficient for all example data in "/idata/".

The first line of such a configuration file specifies the headers of the output data file.
The second line specifies the headers of the entries in the configuration file, 
where each additional line is an entry specifying how to parse all sensors of a given weather station.

Weather stations output loggernet data files containing time series data for one or more Campbell Scientific remote sensors.
Loggernet files begin with four header lines, where the second column of the first line uniquely identifies the format with respect to the configuration file. 
Time series loggernet data includes a timestamp for each data point.
The configuration file is responsible for associating the unique format label of a station with information 
necessary to parse its data points from its loggernet file, including the sampling rate of the time series data, 
the format of the timestamps, a beginning and ending timestamp indicating a window of time considered relevant, 
and a string encoding the mapping of input loggernet data points associated with a sensor to the correct output data point.

The mappings of each the sensors of a given remote weather station are seperated by pipe characters in this long encoding string.
Each mapping corresponding to exactly one sensor of one station is a colon seperated list of entries.
The first entry of such a mapping is an identifier to associate with the relevant sensor (becomes a suffix on the hydrocode in the output data).
The remaining entries must be or begin with integers, corresponding one to one with the output headers; these specify the columns of the input to map to the columns of the output.
These integers can fall within the range of 0 to M-1 where there are M headers used in the output, with the exception that -1 is mapped to a "NULL" value placeholder.
One additional possibility is supported for arbitrarily processing each value of a given column, 
where the entry consists of an integer between 0 and M-1 followed by a ">" character, followed by a string specifying an operation on "x", where "x" refers to an entry of that column.
For a given row of data found in an input data file, the resulting output data row will represent this mapping followed by 
two columns containing the sampling rate of the input data as well as the unique hydrocode associated with the sensor responsible for the input data row.

There are thus three valid specifications for mapping an input column data entry to an output column data entry:
1) The entry "-1" means the column entry of the output will be filled with "NULL". 
2) The entry "j" where j is an integer between 0 and M-1 will be filled with the jth column data value of the input row. 
3) The entry "j>5.0*(x-32.0)/9.0" will operate on the jth column data value of the input row, 
subtracting 32, and multiplaying 5.0/9.0 (converting temperature from degrees fahrenheit to celsius as an example).



