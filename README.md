# grapeipm_support
support scripts for grapeipm website

-------------------------------------------------------------------------------

convert.py is a script used to parse time series weather data from loggernet files into a unified format specified in a configuration file.
In addition to modifying the general format of this data, it permits merging of such data into a single output file given any number of input files.

"convert.py -h" will display usage

-------------------------------------------------------------------------------

"convert.cfg" is an example configuration file sufficient for example data in idata/

The first line of such a configuration file specifies the headers of the output data file.
The second line specifies the headers of the entries in the configuration file, where each additional line is an entry specifying how to parse all sensors of a given weather station.

Stations output loggernet files containing time series data for one or more sensors.
Loggernet files begin with four header lines, where the second column of the first line uniquely identifies the format 
with respect to the configuration file. Time series loggernet data includes a timestamp for each data point.
The configuration file is responsible for associating the unique format label of a station with information 
necessary to parse its data points from its loggernet file, including the format of the timestamps, 
a beginning and ending timestamp indicating a window of time considered "relevant", and a string encoding the mapping of
input loggernet data points associated with a sensor to the correct output data point.

The mappings for each sensor of a given station are seperated by pipe characters in this long encoding string.
Each mapping corresponding to exactly one sensor of one station is a colon seperated list of entries.
The first entry of such a mapping is an identifier to associate with the relevant sensor (becomes a suffix on the hydrocode in the output data).
The remaining entries must be integers, corresponding one to one with the output headers; these specify the columns of the input to map to the columns of the output.
These integers can fall within the range of 0-M where there are M-1 headers used in the output, with the exception that -1 is mapped to a "NULL" value placeholder.
