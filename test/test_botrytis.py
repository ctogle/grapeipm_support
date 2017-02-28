#!/usr/bin/python2.7

import unittest,sys,os,pdb

class test_idata(unittest.TestCase):

	def test_classifyindex(self):
		cf = botrytis.botrytis.classifyindex
		self.assertEqual(cf(0.0),'None')
		self.assertEqual(cf(0.001),'None')
		self.assertEqual(cf(0.01),'Low')
		self.assertEqual(cf(0.02),'Low')
		self.assertEqual(cf(0.5),'Moderate')
		self.assertEqual(cf(0.6),'Moderate')
		self.assertEqual(cf(1.0),'High')
		self.assertEqual(cf(1.1),'High')

if __name__ == '__main__':
	p = os.path.join(os.getcwd(),'../')
	sys.path.insert(0,p)
	botrytis = __import__('botrytis')
	sys.path.pop(0)
   	unittest.main()



