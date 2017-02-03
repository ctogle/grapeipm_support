#!/usr/bin/python2.7
import pdb,os,csv,argparse,datetime,collections

# perform merging on a single loggernet file
def translate(args):
	# ifile should be a loggernet file, corresponding to one station and some number of sensors
	# ofile is the destination file for parsed data (sometimes overwritten, sometimes appended to)
	ifile,ofile = args.inputfile,args.outputfile
	# cfg is a dictionary of information used in parsing, 
	#	carrying station/sensor specific information about how to handle all known loggernet formats
	cfg = parse_config(args.configfile)
	# outheader decides if outputting outputs in ofile is necessary
	outheader = not os.path.exists(args.outputfile) or args.overwrite

	# open ifile for parsing - multiple passes required for multiple sensors
	with open(ifile,'r') as ifh:
		reader = csv.reader(ifh)

		# extract some header information from ifile and discard the rest
		# it is assumed that each loggernet file has exactly 4 header lines
		formatting = next(reader)
		next(reader),next(reader),next(reader)
		ifh.seek(0)

		# extract the identify of the station from the first of the header lines
		station = formatting[1]
		# extract the timestamp format associated with ifile from the config file
		timestamp_format = cfg[station][0]
		# extract the opening timestamp for the window of relevance
		if args.startdate:opentimestamp = args.startdate
		else:opentimestamp = cfg[station][1]
		opentime = datetime.datetime.strptime(opentimestamp,timestamp_format)
		# extract the closing timestamp for the window of relevance
		if args.startdate:closetimestamp = args.enddate
		else:closetimestamp = cfg[station][2]
		closetime = datetime.datetime.strptime(closetimestamp,timestamp_format)
		# extract mapping necessary for sensor specific handling of ifile
		translatekeys = cfg[station][3].split('|')

		# if a hydrocode prefix was not given as an argument, use the name of the station
		if args.hydrocode:hydrocodeprefix = args.hydrocode 
		else:hydrocodeprefix = station 

		# open the output file
		with open(ofile,'w' if args.overwrite else 'a') as ofh:
			writer = csv.writer(ofh,delimiter = args.delimiter)

			# write the header line if the file is new, or not being overwritten
			if outheader:writer.writerow(cfg['OUTPUTINFO'][0])

			# iterate over sensor key mappings, outputting data to ofile for each sensor
			# the sensor mappings are specified by the config file
			for tkeys in translatekeys:
				# extract the index mapping from ifile to ofile data points
				# assume the first entry is always the hydrocode suffix
				# construct the station and sensor unique hydrcode
				tkey = tkeys.split(':')
				hydrocodesuffix = tkey.pop(0)
				tkey = [int(j) for j in tkey] 
				hydrocode = hydrocodeprefix+hydrocodesuffix

				# return to the 5th line of the input file (after headers)
				ifh.seek(0)
				next(reader),next(reader),next(reader),next(reader)

				# iterate over the input data points using the given sensor index mapping
				for irow in reader: 
					# skip this data point if the timestamp is insufficently recent
					itime = datetime.datetime.strptime(irow[0],timestamp_format)
					if itime <= opentime or itime >= closetime:continue
					# construct and record the output data point 'orow' based on the relevant sensor
					orow = []
					for x in tkey:
						if x < 0:orow.append('NULL')
						else:orow.append(irow[x])
					orow.insert(2,'0')
					orow.append(hydrocode)
					writer.writerow(orow)

			# update the config file to reflect to newest processed data point
			cfg[station][1] = itime.strftime(cfg[station][0])

	# note the successful processing of ifile to ofile on stdout
	print('translated file \'%s\' to \'%s\'' % (ifile,ofile))
	# update the config file with any changes to cfg dictionary that occurred 
	if args.updateconfig:save_config(args.configfile,cfg)

# given the path to a configuration file, return a dict of specified options to use
def parse_config(config):
	specs = collections.OrderedDict()
	with open(config,'r') as cfh:
		reader = csv.reader(cfh)
		outputheaders = next(reader)
		configheaders = next(reader)
		specs['OUTPUTINFO'] = (outputheaders,configheaders)
		for irow in reader:
			specs[irow[0]] = irow[1:] 
	return specs

# update the config file based on what data was processed 
# changes should be represented by changes in specs (no changes to specs -> identical cfg file) 
def save_config(config,specs):
	with open(config,'w') as cfh:
		writer = csv.writer(cfh)
		for speckey in specs.keys():
			if speckey == 'OUTPUTINFO':
				writer.writerow(specs[speckey][0])
				writer.writerow(specs[speckey][1])
			else:
				stationcfg = [speckey]+specs[speckey]
				writer.writerow(stationcfg)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter)
	parser.add_argument('inputfile',help = 'specify an input data file')
	parser.add_argument('outputfile',help = 'specify an output data file')
	parser.add_argument('configfile',help = 'specify a parsing configuration file')
	parser.add_argument('-s','--startdate',
		help = 'specify a starting time stamp for relevant new data points')
	parser.add_argument('-e','--enddate',
		help = 'specify an ending time stamp for relevant new data points')
	parser.add_argument('-o','--overwrite',action = 'store_true',
		help = 'discard existing data if output file already exists')
	parser.add_argument('-d','--delimiter',default = ',',
		help = 'specify a delimiter for all new data points being processed\nNote: use $\'\\t\' for tab character')
	parser.add_argument('-i','--hydrocode',
		help = 'specify a hydrocode prefix for all new data points being processed')
	parser.add_argument('-u','--updateconfig',action = 'store_true',
		help = 'update the config file after parsing new data')
	args = parser.parse_args()
	translate(args)

