#!/usr/bin/python2.7
import fungal_risk_model
import math


class botrytis(fungal_risk_model.model):
	'''"Development of an Infection Model for Botrytis Bunch Rot of Grapes 
		Based on Wetness Duration and Temperature"
	
	Botrytis model 2 (Broom et al 1995), added 2013
	Requires: temperature, hours of free moisture, rainfall, relative humidity		
	NOTE: Model implemented in paper took hourly averages of 15-min datapoints.

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
	def diseaseindex(parameters,WD,T):
		'''Compute the botrytis index (value between 0 and 1)
		WD 	: Wetness duration
		T	: Temperature
		Per Broom et. al. 1995/2003 ->
			-> logit(r) = a + WD*(b + c*T + d*T**2) = z = ln(r/(1 - r))
			-> r = e**z/(1 + e**z)
		Classify the risk associated with the disease index ->
			r < 0.01 	-> No Risk
		0.01 <= r < 0.5 	-> Low Risk
		0.5  <= r < 1.0 	-> Moderate Risk
		1.0  <= r 		-> High Risk
		'''
		if WD == 0.0:r = 0.0
		else:
			# map a,b,c,d,WD,T to logit(r) = z
			a,b,c,d = parameters 
			z = a+WD*((b)+(c*T)+(d*T**2))
			# map y to 0 to 1 with sigmoid filter
			r = ((math.e**z)/(1+math.e**z))
		return r


