#!/usr/bin/python2.7
import pdb,fnmatch,os,csv,json,time,numpy,argparse,datetime,collections
from six.moves import urllib
import convert


def urlfetch(origin,outpath):
    '''If "outpath" is nonexistent, download data from "origin" to "outpath".
    Return True if a download was performed, False otherwise.'''
    if not os.path.exists(outpath):
        print('... downloading data from %s ...' % origin)
        urllib.request.urlretrieve(origin,outpath)
        print('... downloaded data from %s ...' % origin)
        return True
    else:print('... already cached data from %s ...' % origin)
    return False


#def gather(cache,apikey,apidelay,state,city,startdate,enddate,lastcall):
def gather(cache,apikey,apidelay,state,city,startdate,enddate,lastcall):
    '''Download weather underground data for a "state","city" pair covering 
    the dates from "startdate" to "enddate".
    NOTE: "lastcall" is used to prevent abuse of weather undergrounds
    limitations on frequency of api usage (10 requests / minute).
    '''
    if not os.path.exists(cache):os.mkdir(cache)
    currentdate,ndays,nday = startdate,(enddate-startdate).days,0
    datafiles = []
    while nday < ndays:
        if currentdate == enddate:break
        sleep = apidelay-(time.time()-lastcall)
        if sleep < 0:
            currentdate = startdate+datetime.timedelta(nday)
            date = currentdate.strftime('%Y%m%d')
            if state == 'PWS':url = make_url_date_station(apikey,city,date)
            else:url = make_url_date_state_city(apikey,state,city,date)
            outpath = make_outpath(cache,state,city,date)
            if urlfetch(url,outpath):lastcall = time.time()
            datafiles.append(outpath)
            nday += 1
        else:
            print('... sleeping for %.2f seconds ...' % sleep)
            time.sleep(sleep)
    return datafiles,lastcall


def convert_json(cfg,writer,data):
    '''Given the configuration namespace "cfg", a csv writer "writer", 
    and json data "data", write converted data into the file.'''
    for o in data['history']['observations']:
        d = o['date']
        t = (d['year'],d['mon'],d['mday'],d['hour'],d['min'],'00')
        p = '0' if '-' in o['precipm'] else o['precipm']
        r = [cfg.timestamp_format % t,o['tempm'],o['hum'],p]
        writer.writerow(r)


def convert(cfg,datafiles):
    '''Given a list of json files, generate a csv data file'''
    if not datafiles:
        print('cannot generate loggernet-like data without json files!')
        raise ValueError
    diter = datafiles.__iter__()
    dfile = next(diter)
    with open(dfile) as f:data = json.load(f)
    if fnmatch.fnmatch(dfile,'*PWS_*'):
        state = 'PWS'
        city = data['location']['nearby_weather_stations']['pws']['station'][0]['id']
    else:
        state = data['location']['state']
        city = data['location']['city']
    loggernet_identifier = 'WeatherUnderground'
    hydrocode = '%s_%s_%s' % (loggernet_identifier,state,city)
    if not os.path.exists(cfg.output):os.mkdir(cfg.output)
    ofile = os.path.join(cfg.output,'%s_Min%s.dat' % (hydrocode,cfg.interval))
    outheader = not os.path.exists(ofile) or cfg.overwrite
    with open(ofile,'w' if outheader else 'a') as ofh:
        writer = csv.writer(ofh,delimiter = ',')
        if outheader:
            headers = [
                [hydrocode,loggernet_identifier],
                #['begintime','airTC_avg','relav_humid','rain_mm_tot'],
                ['begintime','tempm','hum','precipm'],
                ['TS','Deg C','%','mm'],
                ['--','Avg','Smp','Tot'],
                    ]
            for h in headers:writer.writerow(h)
        convert_json(cfg,writer,data)
        for dfile in diter:
            with open(dfile) as df:
                convert_json(cfg,writer,json.load(df))


def parse_config(cfg):
    '''Given a namespace cfg, fill in extra attributes based on a configuration file.
    NOTE: This requires that the default options all evaluate to False.'''
    with open(cfg.configfile,'r') as cfh:
        entries = cfh.read().split(os.linesep)
        for entry in entries:
            if not entry.strip() or entry.startswith('#'):continue
            elif '=' in entry:
                l,r = entry.split('=')
                l,r = l.strip(),r.strip()
                if not (hasattr(cfg,l) and cfg.__getattribute__(l)):
                    cfg.__setattr__(l,r)
            else:print('unknown wu config line format: \'%s\'' % entry)
    return cfg


#         'https://www.wunderground.com/personal-weather-station/dashboard?ID=KVAWINCH48#history'
#baseurl_data_station = 'https://api.wunderground.com/api/%s/geolookup/history_%s/q/pws:KVAWINCH48.json'
baseurl_data_station = 'https://api.wunderground.com/api/%s/geolookup/history_%s/q/pws:%s.json'
baseurl_date_state_city = 'http://api.wunderground.com/api/%s/geolookup/history_%s/q/%s/%s.json'
make_outpath = lambda p,s,c,d : os.path.join(p,s+'_'+c+'_'+d+'.json')
make_url_date_state_city = lambda u,s,c,d : baseurl_date_state_city % (u,d,s,c)
make_url_date_station = lambda u,s,d : baseurl_data_station % (u,d,s)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument('configfile',
        help = 'specify a parsing configuration file')
    parser.add_argument('-u','--apikey',
        help = 'specify a user api key for weather underground')
    parser.add_argument('-d','--cache',
        help = 'specify a directory to store raw weather underground data')
    parser.add_argument('-l','--locations',
        help = 'specify locations to gather data for')
    parser.add_argument('-w','--overwrite',action = 'store_true',
        help = 'discard existing data if output file already exists')
    parser.add_argument('-s','--startdate',
        help = 'specify a starting time stamp for relevant new data points')
    parser.add_argument('-e','--enddate',
        help = 'specify an ending time stamp for relevant new data points')
    cfg = parse_config(parser.parse_args())

    ts_format = '%Y-%m-%d %H:%M:%S'
    startdate = datetime.datetime.strptime(cfg.startdate,ts_format)
    enddate = datetime.datetime.strptime(cfg.enddate,ts_format)

    datafiles = collections.OrderedDict()
    lastcall = time.time()
    for statecities in cfg.locations.split('|'):
        state,cities = statecities.split(':')
        datafiles[state] = collections.OrderedDict()
        for city in cities.split(','):
            gargs = (
                cfg.cache,cfg.apikey,float(cfg.apidelay),
                state,city,startdate,enddate,lastcall,
                    )
            datafiles[state][city],lastcall = gather(*gargs)
            convert(cfg,datafiles[state][city])


