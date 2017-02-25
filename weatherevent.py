#!/usr/bin/python2.7
import pdb



class event(object):
	'''Events are batches of weather data points considered contiguous 
	based on some auxiliary condition (applied during event creation).
	'''

	rh_threshold = 0.95
	lw_threshold = 0.0

	@staticmethod
	def mean(seq):return sum(seq)/len(seq)

	@staticmethod
	def classify(datapoint):
		'''Event condition for classifying a datapoint'''
		if datapoint['LWMwet_tot'] == 'NULL':return
		lw_above = datapoint['LWMwet_tot'] >= event.lw_threshold
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



