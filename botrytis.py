#!/usr/bin/python2.7
import weatherevent
import pdb,math



class botrytis(object):
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

	labels = ['Negligible','Low','Moderate','High']
	thresholds = [0.01,0.5,1.0]
	parameters = (-2.647866,-0.374927,0.061601,-0.001511)
	assert len(labels) == len(thresholds)+1

	@staticmethod
	def classifyindex(y):
		'''Classify the risk associated with the disease index
		y < 0.01 	-> No Risk
		0.01 < y < 0.5 	-> Low Risk
		0.5 < y < 1.0 	-> Moderate Risk
		1.0 < y 	-> High Risk
		'''
		if y == 'NULL':return 'NULL'
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
		'''
		#Logit(Y)= alpha-(beta*LWobs)+(gamma*Tobs*LWobs)-(rho*LWobs*(Tobs^2))
		#Then y =100* (EXP(logit(Y))/(1+EXP(logit(Y))))
		a,b,c,d = botrytis.parameters 
		z = a+WD*((b)+(c*T)+(d*T**2))
		# map y to 0 to 1 with sigmoid filter
		r = ((math.e**z)/(1+math.e**z))
		return r

	@staticmethod
	def model(datapoints,cfg):
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
		dpiter = datapoints.__iter__()
		dp = next(dpiter)
		events = [weatherevent.event(dp,weatherevent.event.classify(dp))]
		interval = float(cfg[0])
		drytheshold = 4.0*60.0
		dryperiod = 0.0
		for dp in dpiter: 
			lastvariety = events[-1].variety
			nextvariety = weatherevent.event.classify(dp)
			if nextvariety == 'dry':dryperiod += interval
			if lastvariety == nextvariety:
				events[-1].datapoints.append(dp)
			elif nextvariety == 'NULL':
				dryperiod = 0.0
				events.append(weatherevent.event(dp,nextvariety))
			elif nextvariety == 'wet':
				dryperiod = 0.0
				events.append(weatherevent.event(dp,nextvariety))
			elif nextvariety == 'dry':
				if lastvariety == 'NULL':
					dryperiod = 0.0
					events.append(weatherevent.event(dp,variety))
				elif lastvariety == 'wet':
					if dryperiod >= drythreshold:
						ne = weatherevent.event(dp,lastvariety)
						events.append(ne)
					else:events[-1].datapoints.append(dp)
		xs,ys,cs = [],[],[]
		for e in events:
			fdp,ldp = e.datapoints[0],e.datapoints[-1]
			if e.variety == 'wet':
				WD = e.wet_time()
				T = e.temperature()
				if WD is None or T is None:
					y,r = 'NULL','NULL'
				else:
					y = botrytis.diseaseindex(WD,T)
					r = botrytis.classifyindex(y)
			else:y,r = 'NULL','NULL'
			xs.extend([dp['begintime'] for dp in e.datapoints])
			ys.extend([y for j in range(len(e.datapoints))])
			cs.extend([r for j in range(len(e.datapoints))])
		return xs,ys,cs



