#!/usr/bin/python2.7
import pdb,os,csv,argparse,datetime,collections

# make a lambda function corresponding to handling of a data column
def make_translatevalue(j):
	if '>' in j:
		i,g = j.split('>')
		i,e = int(i),lambda x : eval(g)
		f = lambda ir : str(e(float(ir[i])))
	else:
		i = int(j)
		if i < 0:f = lambda ir : 'NULL'	
		else:f = lambda ir : ir[i]
	return f

# perform merging on a single loggernet file
def translate(ifile,ofile,cfg,args):
	# outheader decides if outputting outputs in ofile is necessary
	outheader = not os.path.exists(ofile) or args.overwrite
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
		# extract the configuration info for parsing all target sensors
		if station in cfg:
			sensors = cfg[station]
			if args.hydrocode in sensors:
				sensors = ((args.hydrocode,sensors[args.hydrocode]),)
			elif args.hydrocode is None:
				sensors = tuple((s,sensors[s]) for s in sensors.keys())
			else:
				print('sensor \'%s\' not found for station \'%s\' in configuration file \'%s\'' % (args.hydrocode,station,args.configfile))
				return False
		else:
			print('station \'%s\' of input file \'%s\'  not found in configuration file \'%s\'' % (station,ifile,args.configfile))
			return False	

		# open the output file
		with open(ofile,'w' if args.overwrite else 'a') as ofh:
			writer = csv.writer(ofh,delimiter = args.delimiter)
			# write the header line if the file is new, or not being overwritten
			if outheader:writer.writerow(cfg['OUTPUTINFO'][0])

			# iterate over sensor key mappings, outputting data to ofile for each sensor
			# the sensor mappings are specified by the config file
			for hydrocode,sensorcfg in sensors:
				# identify the time interval associated with the data source
				time_interval = sensorcfg[0]
				# extract the timestamp format associated with ifile from the config file
				timestamp_format = sensorcfg[1]
				# extract the opening timestamp for the window of relevance
				if args.startdate:opentimestamp = args.startdate
				else:opentimestamp = sensorcfg[2]
				opentime = datetime.datetime.strptime(opentimestamp,timestamp_format)
				# extract the closing timestamp for the window of relevance
				if args.startdate:closetimestamp = args.enddate
				else:closetimestamp = sensorcfg[3]
				closetime = datetime.datetime.strptime(closetimestamp,timestamp_format)
				# extract the index mapping from ifile to ofile data points
				tkey = sensorcfg[4].split(':')
				tfkey = [make_translatevalue(j) for j in tkey]
				# return to the 5th line of the input file (after headers)
				ifh.seek(0)
				next(reader),next(reader),next(reader),next(reader)
				# iterate over the input data points using the given sensor index mapping
				for irow in reader: 
					# skip this data point if the timestamp is insufficently recent
					itime = datetime.datetime.strptime(irow[0],timestamp_format)
					if itime < opentime or itime >= closetime:continue
					# construct and record the output data point 'orow' based on the relevant sensor
					orow = [tf(irow) for tf in tfkey]
					orow.append(time_interval)
					orow.append(hydrocode)
					writer.writerow(orow)

			# update the config file to reflect to newest processed data point
			if itime < closetime:
				cfg[station][hydrocode][2] = itime.strftime(cfg[station][hydrocode][1])
			else:cfg[station][hydrocode][2] = closetime.strftime(cfg[station][hydrocode][1])

	# note the successful processing of ifile to ofile on stdout
	print('translated file \'%s\' to \'%s\'' % (ifile,ofile))
	# update the config file with any changes to cfg dictionary that occurred 
	if args.updateconfig:save_config(args.configfile,cfg)
	return True

# given the path to a configuration file, return a dict of specified options to use
def parse_config(config):
	specs = collections.OrderedDict()
	with open(config,'r') as cfh:
		reader = csv.reader(cfh)
		outputheaders = next(reader)
		defaultinputfiles = next(reader)
		defaultoutputfile = next(reader)
		configheaders = next(reader)
		specs['OUTPUTINFO'] = (
			outputheaders,
			defaultinputfiles,
			defaultoutputfile,
			configheaders,
				)
		for irow in reader:
			if irow[0].startswith('#'):continue
			configid = irow[0].strip()
			sensorid = irow[1].strip()
			if not configid in specs:
				specs[configid] = collections.OrderedDict()
			specs[configid][sensorid] = irow[2:] 
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
				writer.writerow(specs[speckey][2])
				writer.writerow(specs[speckey][3])
			else:
				for sensorkey in specs[speckey]:
					hydrocfg = [speckey,sensorkey]+specs[speckey][sensorkey]
					writer.writerow(hydrocfg)

def convert_file(ifile,ofile,cfg,args):
	if os.path.exists(ifile):
		didconvert = translate(ifile,ofile,cfg,args)
		if didconvert and args.overwrite:args.overwrite = False
	else:print('input file \'%s\' is missing! - skipping request...' % ifile)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter)
	parser.add_argument('configfile',help = 'specify a parsing configuration file')
	parser.add_argument('-i','--inputfile',help = 'optionally specify an input data file')
	parser.add_argument('-o','--outputfile',help = 'optionally specify an output data file')
	parser.add_argument('-s','--startdate',
		help = 'specify a starting time stamp for relevant new data points')
	parser.add_argument('-e','--enddate',
		help = 'specify an ending time stamp for relevant new data points')
	parser.add_argument('-d','--delimiter',default = ',',
		help = 'specify a delimiter for all new data points being processed\nNote: use $\'\\t\' for tab character')
	parser.add_argument('-c','--hydrocode',
		help = 'specify a hydrocode for all new data points being processed')
	parser.add_argument('-w','--overwrite',action = 'store_true',
		help = 'discard existing data if output file already exists')
	parser.add_argument('-z','--definputs',action = 'store_true',
		help = 'optionally iterate over input files listed on line 2 of config file')
	parser.add_argument('-u','--updateconfig',action = 'store_true',
		help = 'update the config file after parsing new data')
	args = parser.parse_args()

	# cfg is a dictionary of information used in parsing, 
	#	carrying station/sensor specific information about how to handle all known loggernet formats
	cfg = parse_config(args.configfile)
	ifile,ofile = args.inputfile,args.outputfile

	# if no output file was specified, use the default output path from the config file
	if ofile is None:ofile = cfg['OUTPUTINFO'][2][0]

	# the -z option leads to iterating over second line of config file for input files
	if args.definputs:
		for ifile in cfg['OUTPUTINFO'][1]:
			convert_file(ifile,ofile,cfg,args)
	# the -i option was used; ifile is comma seperated list of paths
	elif ifile:
		for ifi in ifile.split(','):	
			convert_file(ifi,ofile,cfg,args)
	# if not using the -z or -i options, iterate over all config entries using their default files
	else:
		autofixhydrocode = not args.hydrocode
		# iterate over config entries for default files
		for stationkey in cfg.keys():
			if stationkey == 'OUTPUTINFO':continue
			for sensorkey in cfg[stationkey]:
				if not autofixhydrocode and not sensorkey == args.hydrocode:
					continue
				defifiles = cfg[stationkey][sensorkey][5:]
				for defifile in defifiles:
					if autofixhydrocode:args.hydrocode = sensorkey
					convert_file(defifile,ofile,cfg,args)

	



