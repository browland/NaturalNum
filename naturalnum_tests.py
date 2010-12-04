import unittest
import naturalnum

class TestNaturalNum(unittest.TestCase):
	#def setUp(self):
		
	def testValidateLhs(self):
		## Ensure only alphanumerics allowed
		self.assertEqual(False, naturalnum.validateLhs(""))
		self.assertEqual(False, naturalnum.validateLhs(None))

		self.assertEqual(False, naturalnum.validateLhs("."))

		self.assertEqual(True, naturalnum.validateLhs("1"))
		self.assertEqual(True, naturalnum.validateLhs("123"))

		self.assertEqual(True, naturalnum.validateLhs("h"))
		self.assertEqual(True, naturalnum.validateLhs("htu"))

		## Ensure no repetition of alpha chars allowed
		self.assertEqual(False, naturalnum.validateLhs("hh"))
		self.assertEqual(False, naturalnum.validateLhs("h1h"))
	
if __name__ == '__main__':
	unittest.main()
