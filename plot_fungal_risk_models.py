#!/usr/bin/python2.7
import fungal_risk_model
import convert

import pdb,os,argparse,numpy,datetime
import matplotlib
matplotlib.use('Agg')
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


#def plot_axes_xy(x = 5,o = (0,0),f = None,aspect = None):
def plot_axes_xy(x = (-5,5),y = (-5,5),f = None,aspect = None):
	if f is None:ax = plt.figure().add_subplot(111)
	else:ax = f.add_subplot(111)
	ax.set_xlim(*x)
	ax.set_ylim(*y)
	if aspect == 'equal':ax.set_aspect('equal')
	return ax


def plot_sensor(path,sensor,data,x_l = 'X',y_l = 'Y',f = None):
	if f is None:f = plt.figure()
	# data is a list of risk datapoints
	# ts,r1i,r1c,...,hc
	timestamp_format = fungal_risk_model.timestamp_format
	epoch = datetime.datetime.utcfromtimestamp(0)
	begintime = data[0]['begintime'].strftime(timestamp_format)
	endtime = data[-1]['endtime'].strftime(timestamp_format)
	xs,yss = [],[[] for j in range(len(data[0].keys())-3)]
	diseases = data[0].keys()
	diseases.remove('begintime')
	diseases.remove('endtime')
	diseases.remove('hydrocode')
	labels = ['Negligible','Low','Moderate','High']
	for dp in data:
    		st = (dp['begintime'] - epoch).total_seconds()
    		et = (dp['endtime'] - epoch).total_seconds()
		xs.append(st);xs.append(et)
		for j,d in enumerate(diseases):
			y = dp[d] if not dp[d] == 'NULL' else -1.0
			if type(y) == type(''):y = labels.index(y)
			yss[j].append(y);yss[j].append(y)
	x = numpy.array(xs)
	ys = numpy.array(yss)

	ax2d = plot_axes_xy(f = f,x = (x.min(),x.max()),y = (-1,3))
	for y,d in zip(ys,diseases):
		line = matplotlib.lines.Line2D(x,y,label = d)
		ax2d.add_line(line)
	ax2d.legend()
		
	ax2d.set_title('%s Disease Risks' % sensor)
	ax2d.set_xlabel(x_l)
	ax2d.set_ylabel(y_l)

	#print('xbounds',(X.min(),X.max()))
	#print('ybounds',(Y.min(),Y.max()))

	#ax2d = plot_axes_xy(x = 5,o = (0,0),f = f,aspect = None)

	fn = os.path.join(path,'%s.png' % sensor)
	f.savefig(fn,dpi = 100)


def plot_measured(datapoints):
	pngpath = os.path.join(os.getcwd(),'measured_model_values')
	if not os.path.exists(pngpath):os.mkdir(pngpath)
	for hydrocode in datapoints:
		plot_sensor(pngpath,hydrocode,datapoints[hydrocode])


def plot_axes(f = None,x = (-5,5),y = (-5,5),z = (-5,5)):
	if f is None:ax = plt.figure().add_subplot(111,projection = '3d')
	else:ax = f.add_subplot(111,projection = '3d')
	ax.set_xlim(*x)
	ax.set_ylim(*y)
	ax.set_zlim(*z)
	#ax.set_zlim([-(9.0/16.0)*x,(9.0/16.0)*x])
	return ax


def plot_model(path,model,x,y,zf,x_l = 'X',y_l = 'Y',z_l = 'Z',f = None):
	X,Y = numpy.meshgrid(x,y)
	z = numpy.array([zf(x,y) for x,y in zip(numpy.ravel(X),numpy.ravel(Y))])
	Z = z.reshape(X.shape)

	if f is None:f = plt.figure()
	ax3d = plot_axes(f = f,
		x = (X.min(),X.max()),
		y = (Y.min(),Y.max()),
		z = (Z.min(),Z.max()))
	ax3d.plot_surface(X,Y,Z,rstride = 1,cstride = 1)
	ax3d.set_xlabel(x_l)
	ax3d.set_ylabel(y_l)
	ax3d.set_zlabel(z_l)

	print('xbounds',(X.min(),X.max()))
	print('ybounds',(Y.min(),Y.max()))
	print('zbounds',(Z.min(),Z.max()))

	for a in xrange(0,360,15):
		ax3d.view_init(elev = 20,azim = a)
		fn = os.path.join(path,'%s_%d.png' % (model,a))
		f.savefig(fn,dpi = 100)


def plot_theoreticals():
	models = fungal_risk_model.models

	wd = numpy.linspace(4,20,17)
	t = numpy.linspace(12,30,19)
	wd_l = 'Wetness Duration (hrs)'
	t_l = 'Temperature (C)'
	z_l = 'Botrytis Disease Index'

	pngpath = os.path.join(os.getcwd(),'theoretical_model_values')
	if not os.path.exists(pngpath):os.mkdir(pngpath)

	for disease,model in models.items():
		mf = models['botrytis'].diseaseindex
		plot_model(pngpath,disease,wd,t,mf,wd_l,t_l,z_l)


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

	cfg,hcfg = convert.parse_config(args.configfile)

	plot_theoreticals()

	datapoints = {}
	ifiles = args.inputfiles.split(',')
	for ifile in ifiles:fungal_risk_model.load_data(ifile,datapoints,hcfg,args)

	plot_measured(datapoints)



