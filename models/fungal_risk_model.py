#!/usr/bin/python2.7
import weatherevent
import pdb,math


class model(object):
	'''"model" is the base class for a fungal risk model.
	It must contain a list of risk classifications ("labels"), a list of 
	threshold values of risk index ("thresholds") with one fewer elements
	than the list of risk classifications.
	The tuple "parameters" is passed to the method "diseaseindex".
	The disease risk index is rounded to the integer "precision" digits before
	risk classification is performed (via the method "classifyindex").
	'''

	labels = ['None']
	thresholds = []
	assert len(labels) == len(thresholds)+1
	parameters = tuple()
	precision = 5

	@staticmethod
	def diseaseindex(parameters,WD,T):
		'''Return the disease index given a wetness duration and temperature
		NOTE: This method should be overloaded in subclasses'''
		return 0.0

	@classmethod
	def classifyindex(cls,y):
		'''Classify the risk associated with the disease index'''
		if y == 'NULL':return 'No-Read'
		else:y = round(y,cls.precision)
		x = 0
		while x < len(cls.thresholds):
			if y < cls.thresholds[x]:break
			else:x += 1
		return cls.labels[x]

	@classmethod
	def eventrisk(cls,event):
		'''Compute the disease index,classification from event'''
		WD = event.wet_time()
		T = event.temperature()
		if WD is None or T is None:
			y,r = 'NULL','No-Read'
		else:
			y = cls.diseaseindex(cls.parameters,WD,T)
			r = cls.classifyindex(y)
		return y,r

	@classmethod
	def model(cls,datapoints):
		'''return a piecewise calculation of disease risk
		xs: will contain datetime objects where risk value changes
		ys: will contain disease indices versus xs 
		cs: will contain index classifications of ys 

		First create wet events as prescribed.
		'''
		events = weatherevent.serialize(datapoints)
		xs,ys,cs = [],[],[]
		for e in events:
			fdp,ldp = e.datapoints[0],e.datapoints[-1]
			if e.variety == 'wet':
				y,r = cls.eventrisk(e)
			elif e.variety == 'dry':
				y,r = cls.eventrisk(e)
			else:y,r = 'NULL','No-Read'
			xs.extend([dp['begintime'] for dp in e.datapoints])
			ys.extend([y for j in range(len(e.datapoints))])
			cs.extend([r for j in range(len(e.datapoints))])
		return xs,ys,cs


