#!/usr/bin/python2.7
import run_fungal_risk_models
import convert

import pdb,os,argparse,numpy,datetime,collections
import matplotlib
matplotlib.use('Agg')
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


def plot_axes_xy(x = (-5,5),y = (-5,5),f = None,loc = '111',aspect = 'auto'):
	if f is None:ax = plt.figure().add_subplot(loc)
	else:ax = f.add_subplot(loc)
	ax.set_xlim(*x)
	ax.set_ylim(*y)
	if aspect == 'equal':ax.set_aspect('equal')
	return ax


def plot_sensor(path,sensor,data,x_l = 'Time (Days)',y_l = 'Y',f = None):
	timestamp_format = run_fungal_risk_models.timestamp_format
	epoch = datetime.datetime.utcfromtimestamp(0)
	begintime = data[0]['begintime'].strftime(timestamp_format)
	endtime = data[-1]['endtime'].strftime(timestamp_format)
	xs,yss = [],[[] for j in range(len(data[0].keys())-3)]
	diseases = data[0].keys()
	diseases.remove('begintime')
	diseases.remove('endtime')
	diseases.remove('hydrocode')
	labels = ['None','Low','Moderate','High']
	for dp in data:
    		st = (dp['begintime'] - epoch).total_seconds()
    		et = (dp['endtime'] - epoch).total_seconds()
		xs.append(st);xs.append(et)
		for j,d in enumerate(diseases):
			y = dp[d] if not dp[d] in ('NULL','No-Read') else -1.0
			if type(y) == type(''):y = labels.index(y)
			yss[j].append(y);yss[j].append(y)
	x = numpy.array(xs)/24.0*60.0*60.0;ys = numpy.array(yss)
	x -= x.min()
	diseasecount = ys.shape[0]//2
	#my = (ys[1::2,:].min()-0.1,ys[1::2,:].max()+0.1)
	my = (-1.1,1.1)
	if f is None:f = plt.figure(figsize = (8,8))
	else:f.clear()
	ax2dl = plot_axes_xy(f = f,x = (x.min(),x.max()),y = my,loc = '211')
	ax2dr = plot_axes_xy(f = f,x = (x.min(),x.max()),y = (-1.1,3.1),loc = '212')
	colors = [matplotlib.cm.jet(k) for k in numpy.linspace(0,1,diseasecount)]
	colors = [a for b in zip(colors,colors) for a in b]
	for y,d,c in zip(ys,diseases,colors):
		line = matplotlib.lines.Line2D(x,y,color = c,lw = 1)
		if d.endswith('Index'):
			line.set_label(d[:d.rfind(' Index')])
			ax2dl.add_line(line)
		elif d.endswith('Risk'):
			line.set_label(d[:d.rfind(' Risk')])
			ax2dr.add_line(line)
		else:raise ValueError
	mx = [x.min(),x.max()]
	ax2dl.plot(mx,[0,0],ls = '--',lw = 1,color = 'black')
	ax2dl.plot(mx,[0.01,0.01],ls = '--',lw = 1,color = 'black')
	ax2dl.plot(mx,[0.5,0.5],ls = '--',lw = 1,color = 'black')
	ax2dl.plot(mx,[1,1],ls = '--',lw = 1,color = 'black')
	ax2dr.plot(mx,[-1,-1],ls = '--',lw = 1,color = 'black')
	ax2dr.plot(mx,[ 0, 0],ls = '--',lw = 1,color = 'brown')
	ax2dr.plot(mx,[ 1, 1],ls = '--',lw = 1,color = 'blue')
	ax2dr.plot(mx,[ 2, 2],ls = '--',lw = 1,color = 'green')
	ax2dr.plot(mx,[ 3, 3],ls = '--',lw = 1,color = 'red')
	ax2dr.yaxis.set_label_position('right')
	#ax2dr.yaxis.tick_right()
	ax2dr.set_yticks([-1,0,1,2,3])
	ax2dr.set_yticklabels(['No-Read']+labels)
	ax2dl.legend();ax2dr.legend()
	ax2dl.set_title('%s Disease Indices' % sensor)
	ax2dr.set_title('%s Disease Risks' % sensor)
	ax2dl.set_xlabel(x_l);ax2dr.set_xlabel(x_l)
	ax2dl.set_ylabel('Index');ax2dr.set_ylabel('Risk')
	fn = os.path.join(path,'%s.png' % sensor)
        f.subplots_adjust(wspace = 0.2,hspace = 0.3)
        f.subplots_adjust(left = 0.02,right = 0.98,top = 0.98,bottom = 0.2)
	f.savefig(fn,dpi = 100,bbox_inches = 'tight')


def plot_measured(datapoints,f = None):
	pngpath = os.path.join(os.getcwd(),'measured_model_values')
	if not os.path.exists(pngpath):os.mkdir(pngpath)
	for hydrocode in datapoints:
		plot_sensor(pngpath,hydrocode,datapoints[hydrocode],f = f)


def plot_axes(f = None,x = (-5,5),y = (-5,5),z = (-5,5)):
	if f is None:ax = plt.figure().add_subplot(111,projection = '3d')
	else:ax = f.add_subplot(111,projection = '3d')
	ax.set_xlim(*x)
	ax.set_ylim(*y)
	ax.set_zlim(*z)
	#ax.set_zlim([-(9.0/16.0)*x,(9.0/16.0)*x])
	return ax


def plot_model(path,model,x,y,p,zf,x_l = 'X',y_l = 'Y',z_l = 'Z',f = None):
	X,Y = numpy.meshgrid(x,y)
	z = numpy.array([zf(p,x,y) for x,y in zip(numpy.ravel(X),numpy.ravel(Y))])
	Z = z.reshape(X.shape)
	if f is None:f = plt.figure()
	else:f.clear()
	ax3d = plot_axes(f = f,
		x = (X.min(),X.max()),
		y = (Y.min(),Y.max()),
		z = (Z.min(),Z.max()))
	ax3d.plot_surface(X,Y,Z,rstride = 1,cstride = 1)
	ax3d.set_xlabel(x_l)
	ax3d.set_ylabel(y_l)
	ax3d.set_zlabel(z_l)
	#print('xbounds',(X.min(),X.max()))
	#print('ybounds',(Y.min(),Y.max()))
	#print('zbounds',(Z.min(),Z.max()))
	for a in xrange(0,360,15):
		ax3d.view_init(elev = 20,azim = a)
		fn = '%s_%d.png' % (model.replace(' ','_').lower(),a)
		fn = os.path.join(path,fn)
		f.savefig(fn,dpi = 100)


def plot_theoreticals(f = None):
	models = run_fungal_risk_models.models

	wd = numpy.linspace(4,20,17)
	t = numpy.linspace(12,30,19)
	wd_l = 'Wetness Duration (hrs)'
	t_l = 'Temperature (C)'

	pngpath = os.path.join(os.getcwd(),'theoretical_model_values')
	if not os.path.exists(pngpath):os.mkdir(pngpath)

	for disease,model in models.items():
		z_l = '%s Disease Index' % disease.title()
		mf = models[disease].diseaseindex
		p = models[disease].parameters
		plot_model(pngpath,disease,wd,t,p,mf,wd_l,t_l,z_l,f = f)


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

	f = plt.figure(figsize = (8,8))
	plot_theoreticals(f = f)

	datapoints = collections.OrderedDict()
	ifiles = args.inputfiles.split(',')
	for ifile in ifiles:
		run_fungal_risk_models.load_data(ifile,datapoints,hcfg,args)

	f = plt.figure(figsize = (8,8))
	plot_measured(datapoints,f = f)


