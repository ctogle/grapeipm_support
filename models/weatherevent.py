#!/usr/bin/python2.7
import pdb



class event(object):
	'''Events hold batches of weather data points considered contiguous 
	based on some auxiliary condition (applied during event creation).
	An event must be able to classify a datapoint (e.g. "wet", "dry", or "NULL").
	Abutting points with equivalent classification are "contiguous".

	An event must be able to compute useful numbers from its data points:
		wet_time : the total number of hours with detected leaf wetness
		temperature : the average temperature in degrees C 
	'''

	#rh_threshold = 0.95
	lw_threshold = 0.0

	@staticmethod
	def mean(seq):return sum(seq)/len(seq)

	@staticmethod
	def classify(datapoint):
		'''Event condition for classifying a datapoint'''
		if datapoint['LWMwet_tot'] == 'NULL':return
		lw_above = datapoint['LWMwet_tot'] > event.lw_threshold
		return 'wet' if lw_above else 'dry'
		#if datapoint['relav_humid'] == 'NULL':return
		#rh_above = datapoint['relav_humid'] >= event.rh_threshold
		#return 'wet' if rh_above else 'dry'

	def wet_time(self):
		'''Return the total time that leaves are considered wet (hours)'''
		return sum([d['LWMwet_tot'] for d in self.datapoints])/60.0

	def temperature(self):
		'''Return the average temperature (degrees C)'''
		dps = []
		for d in self.datapoints:
			if 'NULL' == d['airTC_avg']:
				#print('DATA GAP FLAG')	
				pass
			else:dps.append(d['airTC_avg'])
		return event.mean(dps) if dps else None

	def __init__(self,first_datapoint,variety):
		self.datapoints = [first_datapoint]
		self.variety = variety


def validate(events):
	'''Validate a set of weather event objects to confirm they represent
	classifications of nonoverlapping but adjacent periods of time.'''
	if len(events) > 1:
		eiter = events.__iter__()
		levent = next(eiter)
		while True:
			try:nevent = next(eiter)
			except StopIteration:break
			ltb = levent.datapoints[-1]['endtime']
			ntb = nevent.datapoints[0]['begintime']
			if not ltb == ntb:return False
			if levent.variety == nevent.variety:return False
			levent = nevent
	return True


def serialize(datapoints):
	'''Given a set of datapoints, generate a serial list of appropriate
	weather events, where abutting events differ in classification.'''
	if len(datapoints) == 0:
		print('cannot serialize empty set of data points')
		return []
	dpiter = datapoints.__iter__()
	dp = next(dpiter)
	events = [event(dp,event.classify(dp))]
	#interval = float(cfg[0])
	interval = (dp['endtime']-dp['begintime']).total_seconds()/60.0
	drythreshold = 4.0*60.0
	dryperiod = 0.0
	for dp in dpiter: 
		lastvariety = events[-1].variety
		nextvariety = event.classify(dp)
		if nextvariety == 'dry':dryperiod += interval
		if lastvariety == nextvariety:
			#print('variety match %s' % lastvariety)
			events[-1].datapoints.append(dp)
		elif nextvariety == 'NULL':
			#print('variety to NULL from %s' % lastvariety)
			dryperiod = 0.0
			events.append(event(dp,nextvariety))
		elif nextvariety == 'wet':
			#print('variety to wet from %s' % lastvariety)
			dryperiod = 0.0
			events.append(event(dp,nextvariety))
		elif nextvariety == 'dry':
			#print('variety to dry from %s' % lastvariety)
			if lastvariety == 'NULL':
				dryperiod = 0.0
				events.append(event(dp,variety))
			elif lastvariety == 'wet':
				if dryperiod >= drythreshold:
					ne = event(dp,nextvariety)
					events.append(ne)
				else:events[-1].datapoints.append(dp)
	if validate(events):return events
	else:
		print('event serialization failure')
		raise ValueError



