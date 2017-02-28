#!/usr/bin/python2.7
#import fungal_risk_model
import weatherevent
import pdb,math



class botrytis(object):
#class botrytis(fungal_risk_model.model):
	'''"Development of an Infection Model for Botrytis Bunch Rot of Grapes 
		Based on Wetness Duration and Temperature"
	
	Botrytis model 2 (Broom et al 1995), added 2013
	Requires: 
		temperature, hours of free moisture, rainfall, relative humidity		
		(Model implemented in paper took hourly averages of 15-min datapoints.)	

	"The Botrytis model initiated calculation of a 
	disease index whenever leaf wetness was detected."
	"The calculation of a logit value was stopped if a 
	dry period of greater than 4 h was recorded."

	"A spray was advised as soon as either a moderate or high risk
	was indicated, even if the wet period continued."	
	'''

	labels = ['None','Low','Moderate','High']
	thresholds = [0.01,0.5,1.0]
	assert len(labels) == len(thresholds)+1
	parameters = (-2.647866,-0.374927,0.061601,-0.001511)
	precision = 5

	@staticmethod
	def classifyindex(y):
		'''Classify the risk associated with the disease index
		y < 0.01 	-> No Risk
		0.01 <= y < 0.5 -> Low Risk
		0.5 <= y < 1.0 	-> Moderate Risk
		1.0 <= y 	-> High Risk
		'''
		if y == 'NULL':return 'No-Read'
		x = 0
		while x < len(botrytis.thresholds):
			if y < botrytis.thresholds[x]:break
			else:x += 1
		return botrytis.labels[x]

	@staticmethod
	def diseaseindex(WD,T):
		'''Compute the botrytis index (value between 0 and 1)
		WD 	: Wetness duration
		T	: Temperature

		Per Broom et. al. 1995/2003 - 
			-> logit(r) = a + WD*(b + c*T + d*T**2) = z = ln(r/(1 - r))
			-> r = e**z/(1 + e**z)
		'''
		if WD == 0.0:r = 0.0
		else:
			# map a,b,c,d,WD,T to logit(r) = z
			a,b,c,d = botrytis.parameters 
			z = a+WD*((b)+(c*T)+(d*T**2))
			# map y to 0 to 1 with sigmoid filter
			r = ((math.e**z)/(1+math.e**z))
		return round(r,botrytis.precision)

	@staticmethod
	def eventrisk(event):
		'''Compute the botrytis index,classification from event'''
		WD = event.wet_time()
		T = event.temperature()
		if WD is None or T is None:
			y,r = 'NULL','No-Read'
		else:
			y = botrytis.diseaseindex(WD,T)
			r = botrytis.classifyindex(y)
		return y,r

	@staticmethod
	def model(datapoints):
		'''return a piecewise calculation of botrytis risk
		xs: will contain datetime objects where risk value changes
		ys: will contain disease indices versus xs 
		cs: will contain index classifications of ys 
		'''
		'''
		First create wet events as prescribed.
		Model implemented in paper took hourly averages of 15-min datapoints.
		"The Botrytis model initiated calculation of a 
		disease index whenever leaf wetness was detected."
		"The calculation of a logit value was stopped if a 
		dry period of greater than 4 h was recorded."
		'''
		events = weatherevent.serialize(datapoints)
		xs,ys,cs = [],[],[]
		for e in events:
			fdp,ldp = e.datapoints[0],e.datapoints[-1]
			if e.variety == 'wet':
				y,r = botrytis.eventrisk(e)
			elif e.variety == 'dry':
				y,r = botrytis.eventrisk(e)
			else:y,r = 'NULL','No-Read'
			xs.extend([dp['begintime'] for dp in e.datapoints])
			ys.extend([y for j in range(len(e.datapoints))])
			cs.extend([r for j in range(len(e.datapoints))])
		return xs,ys,cs



