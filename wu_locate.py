#!/usr/bin/python2.7
import argparse,contextlib,io,sys,os,json,time,pdb
import matplotlib.pyplot as plt
import wu_gather


baseurl_lonlat = 'http://api.wunderground.com/api/%s/geolookup/q/%s,%s.json'
make_url_lonlat = lambda u,x,y : baseurl_lonlat % (u,x,y)
# added this function cause it looks like Wunderground defies convention and has lat first
# Converts params given as x,y to y,x
make_url_latlon = lambda u,x,y : baseurl_lonlat % (u,x,y)

baseurl_state = 'http://api.wunderground.com/api/%s/geolookup/q/%s.json'
make_url_state = lambda u,s : baseurl_state % (u,s)

locstring = lambda slocs : '|'.join([k+':'+','.join(slocs[k]) for k in slocs])


def plot_stationpoints(pts,lon,lat,bndf = 10.0):
    print('Calling fn plot_stationpoints()')
    '''Useful function for plotting the locations of stations around a lon,lat point.'''
    print('... found %d nearby stations to lon,lat %s,%s ...' % (len(pts),lon,lat))
    xs,ys = zip(*pts)
    xmin,xmax = min(xs),max(xs)
    ymin,ymax = min(ys),max(ys)
    xrng,yrng = xmax-xmin,ymax-ymin
    plt.xlim((min(xs)-xrng/bndf,max(xs)+xrng/bndf))
    plt.ylim((min(ys)-yrng/bndf,max(ys)+yrng/bndf))
    plt.plot([lon],[lat],marker = '*',color = 'red')
    for p in pts[1:]:plt.plot([p[0]],[p[1]],marker = 'o',color = 'g')
    plt.show()


@contextlib.contextmanager
def nostdout():
    print('Calling fn nostdout()')
    '''Context manager that supresses stdout.'''
    save_stdout = sys.stdout
    sys.stdout = io.BytesIO()
    yield
    sys.stdout = save_stdout


def query(url,outpath):
    print('Calling fn query(%s, %s)' % (url, outpath))
    '''Download json file from url, save at output, and return associated data.'''
    if wu_gather.urlfetch(url,outpath):lastcall = time.time()
    with open(outpath) as f:data = json.load(f)
    return data


def lonlat(cache,apikey,lon,lat):
    print('Calling fn lonlat()')
    '''Fetch list of up to 50 station locations within 40 km of a longitude,latitude.
    "The nearby Personal Weather Stations returned in the feed represent the closest 
    stations within a 40km radius, with a max number of stations returned of 50."'''
    outpath = wu_gather.make_outpath(cache,'LonLat_'+str(lon),str(lat),'X')
    url = make_url_latlon(apikey,lat,lon)
    data = query(url,outpath)
    pts = []
    stationlocs = {}
    nearby = data['location']['nearby_weather_stations']
    for stationtype in nearby:
        nearbystations = nearby[stationtype]['station']
        for station in nearbystations:
            # lon and lat are switched, as wunderground seems to be in err...
            #pts.append((float(station['lon']),float(station['lat'])))
            pts.append((float(station['lat']),float(station['lon'])))
            if stationtype == 'airport':sloc = station['state'],station['city']
            elif stationtype == 'pws':sloc = 'PWS',station['id']
            else:
                emsg = '... stationtype %s is not supported ...'
                # this wont print on stdout with nostdout()...
                raise ValueError(emsg % stationtype)
            if sloc[0] in stationlocs:stationlocs[sloc[0]].append(sloc[1])
            else:stationlocs[sloc[0]] = [sloc[1]]
    #plot_stationpoints(pts,float(lon),float(lat))
    return stationlocs


def state(cache,apikey,state):
    print('Calling fn state()')
    '''Fetch state wide list of station locations (one per city).'''
    outpath = wu_gather.make_outpath(cache,state,'X','X')
    url = make_url_state(apikey,state)
    print('... Searching %s with key %s, final URL: %s' % (state,apikey,url))
    data = query(url,outpath)
    stationlocs = {}
    print(data)
    for r in data['response']['results']:
        state,city = r['state'],r['city']
        if state in stationlocs:stationlocs[state].append(city)
        else:stationlocs[state] = [city]
    return stationlocs


if __name__ == '__main__':
    '''
    This can be used with wu_gather.py:
    
    ./wu_gather.py [wu_gather.py OPTIONS] -l "`./wu_locate.py [wu_locate.py OPTIONS]`"

    stdout is supressed aside from the resulting valid -l option for wu_gather.py.
    NOTE: This generally includes errors consequent of invalid input to wu_locate.py ...
    '''
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument('configfile',
        help = 'specify a parsing configuration file')
    parser.add_argument('--state',default = None,
        help = 'specify a state')
    parser.add_argument('--longitude',default = None,
        help = 'specify a longitude coordinate')
    parser.add_argument('--latitude',default = None,
        help = 'specify a latitude coordinate')
    parser.add_argument('-u','--apikey',
        help = 'specify a user api key for weather underground')
    parser.add_argument('-d','--cache',
        help = 'specify a directory to store raw weather underground data')
    cfg = wu_gather.parse_config(parser.parse_args())

    if not os.path.exists(cfg.cache):os.mkdir(cfg.cache)

    if cfg.state:
        #with nostdout():
            stationlocs = state(cfg.cache,cfg.apikey,cfg.state)
    elif cfg.longitude and cfg.latitude:
        #with nostdout():
            stationlocs = lonlat(cfg.cache,cfg.apikey,cfg.longitude,cfg.latitude)
    else:
        emsg = '... need either --state option or --longitude and --latitude options ...'
        raise ValueError(emsg)

    print(locstring(stationlocs))


