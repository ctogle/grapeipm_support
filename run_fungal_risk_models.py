#!/usr/bin/python2.7
import pdb,os,re,csv,argparse,math,datetime,collections
import convert,models


generic_timestamp_format = '%Y-%m-%d %H:%M:%S'
alpha = re.compile(r"^[+-]?\d*[.,]?\d*[e]?[-+]?\d*$")
models = collections.OrderedDict([
    ('Botrytis',models.botrytis.botrytis()),
    ('Black Rot',models.black_rot.black_rot()),
    ('Powdery Mildew',models.powdery_mildew.powdery_mildew()),
    ('Phomopsis',models.phomopsis.phomopsis()),
        ])


# return a function that returns False for irrelevant data
# or returns a transformed datapoint ready for futher computation otherwise
def define_relevant(ot,ct,hcs,headers,hcfg):
    if hcs:hc_relev = lambda hc : hc in hcs
    else:hc_relev = lambda hc : True
    ot_relev = lambda dpot : dpot >= ot 
    ct_relev = lambda dpct : dpct <= ct 
    def relevant(dp):
        dphydrocode = dp[-1]
        if not hc_relev(dphydrocode):return False
        timestamp_format = hcfg[dphydrocode][1]
        dptimestamp = dp[0]
        dpotime = datetime.datetime.strptime(dptimestamp,timestamp_format)
        if not ot_relev(dpotime):return False
        dpinterval = float(hcfg[dphydrocode][0])
        dpctime = dpotime + datetime.timedelta(minutes = dpinterval)
        if not ct_relev(dpctime):return False
        newdp = collections.OrderedDict()
        for j,h in enumerate(headers):
            if h == 'begintime':
                newdp[h] = dpotime
                newdp['endtime'] = dpctime
            elif h == 'records':newdp[h] = int(dp[j]) 
            elif alpha.match(dp[j]):newdp[h] = float(dp[j])
            elif dp[j] in ('NAN','NULL'):newdp[h] = 'NULL'
            else:newdp[h] = dp[j]
        return newdp 
    return relevant


# extract a set of sets of relevant data points
# return a dict of relevant, transformed datapoints organized per sensor
def load_data(ifile,datapoints,hcfg,args):
    if args.hydrocodes:hydrocodes = args.hydrocodes.split(',')
    else:hydrocodes = None
    opentimestamp = args.startdate
    opentime = datetime.datetime.strptime(opentimestamp,generic_timestamp_format)
    closetimestamp = args.enddate
    closetime = datetime.datetime.strptime(closetimestamp,generic_timestamp_format)
    with open(ifile,'r') as ifh:
        reader = csv.reader(ifh)
        headers = next(reader)
        relevant = define_relevant(opentime,closetime,hydrocodes,headers,hcfg)
        for datapoint in reader:
            newdp = relevant(datapoint)
            if not newdp:continue
            newdphc = newdp['hydrocode']
            if newdphc in datapoints:datapoints[newdphc].append(newdp)
            else:datapoints[newdphc] = [newdp]


# output the calculated risk data for relevant data
def save_data(ofile,models,risks,hcfg,args):
    opentimestamp = args.startdate
    opentime = datetime.datetime.strptime(opentimestamp,generic_timestamp_format)
    closetimestamp = args.enddate
    closetime = datetime.datetime.strptime(closetimestamp,generic_timestamp_format)
    outheader = not os.path.exists(ofile) or args.overwrite
    with open(ofile,'w' if args.overwrite else 'a') as ofh:
        writer = csv.writer(ofh,delimiter = args.delimiter)
        if outheader:
            headers = ['begintime']
            for disease in models:
                headers.append(disease+' Index')    
                headers.append(disease+' Risk')    
            headers.append('hydrocode')
            writer.writerow(headers)
        for hydrocode in risks:
            interval = float(hcfg[hydrocode][0])
            timestamp_format = hcfg[hydrocode][1]
            orow = [opentime.strftime(timestamp_format)]
            dptime = opentime + datetime.timedelta(minutes = 0)
            while dptime < closetime:
                for disease in models:
                    dts,dis,drs = risks[hydrocode][disease]
                    if dptime in dts: 
                        dj = dts.index(dptime)
                        orow.append(dis[dj])
                        orow.append(drs[dj])
                    else:
                        orow.append('NULL')
                        orow.append('No-Read')
                orow.append(hydrocode)
                writer.writerow(orow)
                dptime += datetime.timedelta(minutes = interval)
                orow = [dptime.strftime(timestamp_format)]
            print('constructed risk output for hydrocode \'%s\'' % hydrocode)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument('configfile',
        help = 'specify a parsing configuration file')
    parser.add_argument('-i','--inputfiles',
        help = 'optionally specify an input data file')
    parser.add_argument('-o','--outputfile',
        help = 'optionally specify an output data file')
    parser.add_argument('-s','--startdate',default = '2010-01-01 00:00:00',
        help = 'specify a starting time stamp for relevant new data points')
    parser.add_argument('-e','--enddate',default = '2020-01-01 00:00:00',
        help = 'specify an ending time stamp for relevant new data points')
    parser.add_argument('-c','--hydrocodes',
        help = 'specify a hydrocode for all new data points being processed')
    parser.add_argument('-d','--delimiter',default = ',',
        help = 'specify a delimiter for outputting data points\nNote: use $\'\\t\' for tab character')
    parser.add_argument('-w','--overwrite',action = 'store_true',
        help = 'discard existing data if output file already exists')
    args = parser.parse_args()

    if not args.inputfiles:print('no input files provided!');quit()
    elif not args.outputfile:print('no output file provided!');quit()
    cfg,hcfg = convert.parse_config(args.configfile)

    datapoints = collections.OrderedDict()
    ifiles = args.inputfiles.split(',')
    for ifile in ifiles:load_data(ifile,datapoints,hcfg,args)

    risks = {}
    for hydrocode in datapoints:
        risks[hydrocode] = {}
        for threat,model in models.items():
            frisk = model.model(datapoints[hydrocode])
            risks[hydrocode][threat] = frisk 

    save_data(args.outputfile,models,risks,hcfg,args)


