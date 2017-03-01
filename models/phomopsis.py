#!/usr/bin/python2.7
import fungal_risk_model


class phomopsis(fungal_risk_model.model):
	'''TODO: FIND REFERENCES SUPPORTING THIS MODEL.'''

	labels = ['Low','Moderate','High']
	thresholds = [0.07,0.15]
	assert len(labels) == len(thresholds)+1
	parameters = (2.04,3.47,4.86,1.6,5,35)

	@staticmethod
	def diseaseindex(parameters,WD,T):
		'''
		t = (T - e)/(f - e)
		y = a*(t**b)*((1 - t)**c)*(WD**d)
					Cane	Cane
		Equation	Pooled	mean
		a		2.04	1.58
		b		3.47	2.73
		c		4.86	3.68
		d		1.6		1.05
		e 5
		f 35
		Use "pooled" value.
			y < 0.07	-> Low Risk
		0.07 <= y < 0.15	-> Moderate Risk
		0.15 <= y 		-> High Risk
		'''
		if T <= 5 or T >= 35:r = 0
		else: 
			a,b,c,d,e,f = parameters
			t = (T - e)/(f - e)
			r = a*(t**b)*((1 - t)**c)*(WD**d)
			r = min(1,max(0,r))
		return r


