#!/usr/bin/python2.7
import fungal_risk_model
import pdb,math


class black_rot(fungal_risk_model.model):
	'''TODO: FIND REFERENCES SUPPORTING THIS MODEL.'''

	labels = ['Low','High']
	thresholds = [0.1]
	assert len(labels) == len(thresholds)+1
	parameters = (6.6116027,-0.0358765,0.0920909,-21.0556,-0.0039294)

	@classmethod
	def diseaseindex(cls,WD,T):
		'''
		If T < 10 then RiskBR = low
		If T > 10 then
		y = a + b * T + c * ( T + rho)^2 + e * ( T + d)^3
		If WD > y then RiskBR = high
		Else if RiskBR = low
		'''
		if T < 10:r = 0.0
		else:
			a,b,c,d,e = cls.parameters 
			y = a + b*T + c*(T + d)**2.0 + e*(T + d)**3.0
			r = WD/y - 1.0 + 0.1
			r = min(1,max(0.0,r))
		return round(r,cls.precision)


