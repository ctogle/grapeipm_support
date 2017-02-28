#!/usr/bin/python2.7

import unittest,os,csv,pdb

class test_idata(unittest.TestCase):

	cfg = os.path.join(os.getcwd(),'grapeipm.cfg')    
	inp = os.path.join(os.getcwd(),'idata')
	oup = os.path.join(os.getcwd(),'odata','out.dat')

	cmd = '../convert.py '+cfg+' -i'+inp+os.path.sep+'%s -o'+oup+' -w -s \'%s\' -e \'%s\''

	# check the following given a run case
	#	there are the correct number of output data points
	#	each row has the correct number of entries
	#	the hydrocodes are valid
	#	the interval entries are correct
	#	the record numbers are valid
	#	based on the hydrocode, NULL appears where it should
	# 	for a few manually specified points, confirm output
	def check_rowcount_rowlength_hydrocode_interval_nulls_records(self,ifile,s,e,rl,hcs,rcs,nulls,i,dc,pcs):
		pointchecks = {}
		for p,cs in pcs:pointchecks[p] = (cs,[False for x in cs])
		recordchecks = [False for x in rcs[1]]
		os.system(self.cmd % (ifile,s,e))
		with open(self.oup,'r') as ofh:
			reader = csv.reader(ofh)
			headers = next(reader)
			j = 1
			for orow in reader:
				self.assertEqual(len(orow),rl)
				self.assertEqual(str(i),orow[-2])
				self.assertTrue(orow[-1] in hcs)
				null = nulls[hcs.index(orow[-1])]
				for n in null:self.assertEqual(orow[n],'NULL')
				record = int(orow[rcs[0]])
				self.assertTrue(record in rcs[1])
				recordchecks[rcs[1].index(record)] = True
				if record in pointchecks:
					try:
						dpoint = ','.join(orow)
						self.assertTrue(dpoint in pointchecks[record][0])
						pointchecks[record][1][pointchecks[record][0].index(dpoint)] = True
					except AssertionError:
						print(','.join(orow))
						print(pointchecks[record])
						raise AssertionError
				j += 1
			try:
				self.assertFalse(False in recordchecks)
			except AssertionError:
				print('missing records:')
				print([x for x,i in zip(rcs[1],recordchecks) if not i])
				raise AssertionError
			self.assertEqual(j,dc)
			for record in pointchecks:
				self.assertFalse(False in pointchecks[record][1])

	def test_SPAREC(self):
		ifile = 'SPAREC_Min15.dat'
		start,end = '2014-9-30 23:59:59','2014-10-5 00:00:00'
		hydrocodes = ('SPAREC_air','SPAREC_canopy')
		nulls = (2,),(2,)
		records = (1,list(range(12699,13082+1)))
		interval = 15
		rowlength = 12
		datapoints = 1+2*4*24*4
		pointchecks = (
			(12699,(
				'2014-10-01 00:00:00,12699,NULL,17.14087,99.998,348.8169,0,0,15,0,15,SPAREC_air',
				'2014-10-01 00:00:00,12699,NULL,16.9258,99.998,434.8222,0,0,15,0,15,SPAREC_canopy',
				)),
				)
		self.check_rowcount_rowlength_hydrocode_interval_nulls_records(
			ifile,start,end,rowlength,hydrocodes,records,nulls,interval,datapoints,pointchecks)

	def test_Gadino(self):
		ifile = 'Gadino_Min15.dat'
		start,end = '2015-07-02 10:59:59','2017-02-01 00:00:00'
		hydrocodes = ('Gadino_air','Gadino_canopy')
		nulls = (2,),(2,)
		records = (1,list(range(35137,35140+1))+list(range(90047,90058+1)))
		interval = 15
		rowlength = 12
		datapoints = 1+2*len(records[1])
		pointchecks = (
			(90051,(
				'2017-01-24 12:15:00,90051,NULL,5.311333,80.93,275.7236,0,15,0,0,15,Gadino_air',
				'2017-01-24 12:15:00,90051,NULL,15.13467,65.253,271.6607,15,0,0,0,15,Gadino_canopy',
				)),
				)
		self.check_rowcount_rowlength_hydrocode_interval_nulls_records(
			ifile,start,end,rowlength,hydrocodes,records,nulls,interval,datapoints,pointchecks)

	def test_AHSPP(self):
		ifile = 'AHSPP_Min15.dat'
		start,end = '2014-9-30 23:59:59','2014-10-5 00:00:00'
		hydrocodes = ('AHSPP_air','AHSPP_canopy')
		nulls = (2,),(2,)
		records = (1,list(range(12508,12891+1)))
		interval = 15
		rowlength = 12
		datapoints = 1+2*4*24*4
		pointchecks = (
			(12508,(
				'2014-10-01 00:00:00,12508,NULL,15.27073,99.998,362.2337,0,0,15,0,15,AHSPP_air',
				'2014-10-01 00:00:00,12508,NULL,15.56787,99.998,306.1296,0,0,15,0,15,AHSPP_canopy',
				)),
				)
		self.check_rowcount_rowlength_hydrocode_interval_nulls_records(
			ifile,start,end,rowlength,hydrocodes,records,nulls,interval,datapoints,pointchecks)

	def test_AHSGPCH(self):
		ifile = 'AHSGP-CH_Min15.dat'
		start,end = '2014-09-30 23:59:59','2014-10-05 00:00:00'
		hydrocodes = ('AHSGP-CH_air','AHSGP-CH_canopy')
		nulls = (2,),(2,)
		records = (1,list(range(12611,12994+1)))
		interval = 15
		rowlength = 12
		datapoints = 1+2*4*24*4
		pointchecks = (
			(12611,(
				'2014-10-01 00:00:00,12611,NULL,15.27893,99.998,377.8919,0,0,15,0,15,AHSGP-CH_air',
				'2014-10-01 00:00:00,12611,NULL,15.20867,99.998,290.9353,0,0,15,0,15,AHSGP-CH_canopy',
				)),
				)
		self.check_rowcount_rowlength_hydrocode_interval_nulls_records(
			ifile,start,end,rowlength,hydrocodes,records,nulls,interval,datapoints,pointchecks)

	def test_AHSENV(self):
		ifile = 'AHSENV_Min15.dat'
		start,end = '2014-9-30 23:59:59','2014-10-5 00:00:00'
		hydrocodes = ('AHSENV_air','AHSENV_canopy')
		nulls = (2,-3),(2,-3)
		records = (1,list(range(13448,13830+1)))
		interval = 15
		rowlength = 12
		# ./idata/AHSENV_Min15.dat is missing the 2014-10-04 00:00:00 data point!!
		datapoints = 1+2*(4*24*4-1)
		pointchecks = (
			(13448,(
				'2014-10-01 00:00:00,13448,NULL,24.97,49.97,267.8,15,0,0,NULL,15,AHSENV_air',
				'2014-10-01 00:00:00,13448,NULL,23.47,53.01,266.5,15,0,0,NULL,15,AHSENV_canopy',
				)),
				)
		self.check_rowcount_rowlength_hydrocode_interval_nulls_records(
			ifile,start,end,rowlength,hydrocodes,records,nulls,interval,datapoints,pointchecks)

	def test_AHSGPO(self):
		ifile = 'AHSGP-O_Min15.dat'
		start,end = '2014-09-30 23:59:59','2014-10-05 00:00:00'
		hydrocodes = ('AHSGP-O_air','AHSGP-O_canopy')
		nulls = (2,),(2,)
		records = (1,list(range(12602,12985+1)))
		interval = 15
		rowlength = 12
		datapoints = 1+2*4*24*4
		pointchecks = (
			(12602,(
				'2014-10-01 00:00:00,12602,NULL,15.5522,99.998,394.6757,0,0,15,0,15,AHSGP-O_air',
				'2014-10-01 00:00:00,12602,NULL,15.28613,99.998,350.9913,0,0,15,0,15,AHSGP-O_canopy',
				)),
				)
		self.check_rowcount_rowlength_hydrocode_interval_nulls_records(
			ifile,start,end,rowlength,hydrocodes,records,nulls,interval,datapoints,pointchecks)

	def test_SC2High(self):
		ifile = 'SC2-High_Min15.dat'
		start,end = '2014-09-30 23:59:59','2014-10-05 00:00:00'
		hydrocodes = ('SC2-High_air','SC2-High_canopy','SC2-High_apple_canopy')
		nulls = (2,6,7),(2,6,7),(2,6,7)
		records = (1,list(range(11368,11751+1)))
		interval = 15
		rowlength = 12
		datapoints = 1+3*4*24*4
		pointchecks = (
			(11368,(
				'2014-10-01 00:00:00,11368,NULL,16.7772,99.812,278.2236,NULL,NULL,0,0,15,SC2-High_air',
				'2014-10-01 00:00:00,11368,NULL,16.99967,98.105,276.8419,NULL,NULL,0,0,15,SC2-High_canopy',
				'2014-10-01 00:00:00,11368,NULL,16.7028,99.998,276.9864,NULL,NULL,0,0,15,SC2-High_apple_canopy',
				)),
				)
		self.check_rowcount_rowlength_hydrocode_interval_nulls_records(
			ifile,start,end,rowlength,hydrocodes,records,nulls,interval,datapoints,pointchecks)

	def test_SC3Low(self):
		ifile = 'SC3-Low_Min15.dat'
		start,end = '2014-09-30 23:59:59','2014-10-05 00:00:00'
		hydrocodes = ('SC3-Low_air','SC3-Low_canopy','SC3-Low_apple_canopy')
		nulls = (2,6,7),(2,6,7),(2,6,7)
		records = (1,list(range(11366,11749+1)))
		interval = 15
		rowlength = 12
		datapoints = 1+3*4*24*4
		pointchecks = (
			(11366,(
				'2014-10-01 00:00:00,11366,NULL,17.8652,98.584,276.5437,NULL,NULL,0,0,15,SC3-Low_air',
				'2014-10-01 00:00:00,11366,NULL,17.86253,98.996,277.2244,NULL,NULL,0,0,15,SC3-Low_canopy',
				'2014-10-01 00:00:00,11366,NULL,18.10533,98.598,276.4847,NULL,NULL,0,0,15,SC3-Low_apple_canopy',
				)),
				)
		self.check_rowcount_rowlength_hydrocode_interval_nulls_records(
			ifile,start,end,rowlength,hydrocodes,records,nulls,interval,datapoints,pointchecks)

	def test_Ingleside(self):
		ifile = 'Ingleside_Min15.dat'
		start,end = '2015-09-30 23:59:59','2015-10-05 00:00:00'
		hydrocodes = ('Ingleside_air','Ingleside_canopy')
		nulls = (2,),(2,)
		records = (1,list(range(78018,78401+1)))
		interval = 15
		rowlength = 12
		datapoints = 1+2*4*24*4
		pointchecks = (
			(78018,(
				'2015-10-01 00:00:00,78018,NULL,18.49233,92.652,283.0395,0,11,4,0,15,Ingleside_air',
				'2015-10-01 00:00:00,78018,NULL,18.881,92.195,275.6361,0,15,0,0,15,Ingleside_canopy',
				)),
				)
		self.check_rowcount_rowlength_hydrocode_interval_nulls_records(
			ifile,start,end,rowlength,hydrocodes,records,nulls,interval,datapoints,pointchecks)

	def test_SC1MiddleBase(self):
		ifile = 'SC1-MiddleBase_Min15.dat'
		start,end = '2014-09-30 23:59:59','2014-10-05 00:00:00'
		hydrocodes = ('SC1-MiddleBase_air','SC1-MiddleBase_canopy','SC1-MiddleBase_apple_canopy')
		nulls = (2,6,7),(2,6,7),(2,6,7)
		records = (1,list(range(12238,12620+1)))
		interval = 15
		rowlength = 12
		# ./idata/SC1-MiddleBase_Min15.dat is missing the 2014-10-04 00:00:00 data point!!
		datapoints = 1+3*(4*24*4-1)
		pointchecks = (
			(12238,(
				'2014-10-01 00:00:00,12238,NULL,17.51,98.3,273.9,NULL,NULL,0,0,15,SC1-MiddleBase_air',
				'2014-10-01 00:00:00,12238,NULL,17.45,99.8,278,NULL,NULL,0,0,15,SC1-MiddleBase_canopy',
				'2014-10-01 00:00:00,12238,NULL,17.68,99,275.3,NULL,NULL,0,0,15,SC1-MiddleBase_apple_canopy',
				)),
				)
		self.check_rowcount_rowlength_hydrocode_interval_nulls_records(
			ifile,start,end,rowlength,hydrocodes,records,nulls,interval,datapoints,pointchecks)

	def test_CR200Barboursville(self):
		ifile = 'BARBCR200_Min60.dat'
		start,end = '2016-12-31 23:59:59','2017-10-05 00:00:00'
		hydrocodes = ('CR200Barboursville_air',)
		nulls = ((4,5,6,7,8,9),)
		records = (1,list(range(14910,15781+1)))
		interval = 60
		rowlength = 12
		datapoints = 1+(1+15781-14910)
		pointchecks = (
			(14910,(
				'2017-01-01 00:00:00,14910,13.22355,'+str(5.0*(42.36921-32.0)/9.0)+',NULL,NULL,NULL,NULL,NULL,NULL,60,CR200Barboursville_air',
				)),
				)
		self.check_rowcount_rowlength_hydrocode_interval_nulls_records(
			ifile,start,end,rowlength,hydrocodes,records,nulls,interval,datapoints,pointchecks)

	def test_CR800Barboursville(self):
		ifile = 'BARBCR800_Min60.dat'
		start,end = '2016-12-31 23:59:59','2017-10-05 00:00:00'
		hydrocodes = ('CR800Barboursville_air',)
		nulls = ((),)
		records = (1,list(range(10250,11121+1)))
		interval = 60
		rowlength = 12
		datapoints = 1+(1+11121-10250)
		pointchecks = (
			(10250,(
				'2017-01-01 00:00:00,10250,11.5,'+str(5.0*(41.74-32.0)/9.0)+',47.27,-987,60,0,0,'+str(25.4*0)+',60,CR800Barboursville_air',
				)),
				)
		self.check_rowcount_rowlength_hydrocode_interval_nulls_records(
			ifile,start,end,rowlength,hydrocodes,records,nulls,interval,datapoints,pointchecks)

if __name__ == '__main__':
    unittest.main()



