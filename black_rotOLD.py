#!/usr/bin/python2.7
import weatherevent
import pdb,math



class black_rot(object):
	'''TODO: FIND REFERENCES SUPPORTING THIS MODEL.'''

	labels = ['Low','High']
	thresholds = [0.1]
	assert len(labels) == len(thresholds)+1
	parameters = (6.6116027,-0.0358765,0.0920909,-21.0556,-0.0039294)
	precision = 5

	@staticmethod
	def classifyindex(y):
		'''Classify the risk associated with the disease index
		y < 0		-> Low Risk
		0 <= y		-> High Risk
		'''
		if y == 'NULL':return 'No-Read'
		x = 0
		while x < len(black_rot.thresholds):
			if y < black_rot.thresholds[x]:break
			else:x += 1
		return black_rot.labels[x]

	@staticmethod
	def diseaseindex(WD,T):
		'''
		If T < 10 then RiskBR = low
		If T > 10 then
		y = a + b * T + c * ( T + rho)^2 + e * ( T + d)^3
		If WD > y then RiskBR = high
		Else if RiskBR = low
		'''
		if T < 10:r = 0.0
		else:
			a,b,c,d,e = black_rot.parameters 
			y = a + b*T + c*(T + d)**2.0 + e*(T + d)**3.0
			r = WD/y - 1.0 + 0.1
			r = min(1,max(0.0,r))
		return round(r,black_rot.precision)

	@staticmethod
	def eventrisk(event):
		'''Compute the black_rot index,classification from event'''
		WD = event.wet_time()
		T = event.temperature()
		if WD is None or T is None:
			y,r = 'NULL','No-Read'
		else:
			y = black_rot.diseaseindex(WD,T)
			r = black_rot.classifyindex(y)
		return y,r

	@staticmethod
	def model(datapoints):
		'''return a piecewise calculation of black rot risk
		xs: will contain datetime objects where risk value changes
		ys: will contain disease indices versus xs 
		cs: will contain index classifications of ys 
		'''
		'''
		First create wet events as prescribed.
		NOTE: COPYING CLASSIFICATION FROM BOTRYTIS MODEL FOR NOW.
		'''
		events = weatherevent.serialize(datapoints)
		xs,ys,cs = [],[],[]
		for e in events:
			fdp,ldp = e.datapoints[0],e.datapoints[-1]
			if e.variety == 'wet':
				y,r = black_rot.eventrisk(e)
			elif e.variety == 'dry':
				y,r = black_rot.eventrisk(e)
			else:y,r = 'NULL','No-Read'
			xs.extend([dp['begintime'] for dp in e.datapoints])
			ys.extend([y for j in range(len(e.datapoints))])
			cs.extend([r for j in range(len(e.datapoints))])
		return xs,ys,cs



