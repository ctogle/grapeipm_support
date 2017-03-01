#!/usr/bin/python2.7
import fungal_risk_model


class powdery_mildew(fungal_risk_model.model):
	'''TODO: FIND REFERENCES SUPPORTING THIS MODEL.'''

	labels = ['Low','Moderate','High']
	thresholds = [0.2,0.5]
	assert len(labels) == len(thresholds)+1
	parameters = (0.000241,2.06737,35.0,0.72859)

	@staticmethod
	def diseaseindex(parameters,WD,T):
		'''
		T <= 10	or T >= 35	-> Low Risk
		y = a*(T**b)*((c - T)**d)
		0.0 <= y < 0.2		-> Low Risk
		0.2 <= y < 0.5		-> Moderate Risk
		0.5 <= y 		-> High Risk
		'''
		if T <= 10 or T >= 35:r = 0.0
		else:
			a,b,c,d = parameters 
			y = a*(T**b)*((c - T)**d)
			r = min(1,max(0,y))
		return r


