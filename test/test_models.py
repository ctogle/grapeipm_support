#!/usr/bin/python2.7

import unittest,sys,os,pdb

class test_idata(unittest.TestCase):

	def test_botrytis(self):
		cf = botrytis.botrytis.classifyindex
		self.assertEqual(cf(0.0),'None')
		self.assertEqual(cf(0.001),'None')
		self.assertEqual(cf(0.01),'Low')
		self.assertEqual(cf(0.02),'Low')
		self.assertEqual(cf(0.5),'Moderate')
		self.assertEqual(cf(0.6),'Moderate')
		self.assertEqual(cf(1.0),'High')
		self.assertEqual(cf(1.1),'High')

	def test_black_rot(self):
		cf = black_rot.black_rot.classifyindex
		self.assertEqual(cf(0.0),'Low')
		self.assertEqual(cf(0.01),'Low')
		self.assertEqual(cf(0.1),'High')
		self.assertEqual(cf(0.2),'High')
		self.assertEqual(cf(1.0),'High')

if __name__ == '__main__':
	p = os.path.join(os.getcwd(),'../')
	sys.path.insert(0,p)
	botrytis = __import__('botrytis')
	black_rot = __import__('black_rot')
	sys.path.pop(0)
   	unittest.main()



