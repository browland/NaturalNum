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

	def testValidateRhs(self):
		## Ensure only alphanumerics, '(', ')', ',', '$' allowed
		self.assertEqual(False, naturalnum.validateRhs(""))
		self.assertEqual(False, naturalnum.validateRhs(None))
		self.assertEqual(False, naturalnum.validateRhs("."))
		self.assertEqual(False, naturalnum.validateRhs(" "))
		self.assertEqual(True, naturalnum.validateRhs("Aa1(),$"))	

		## Ensure only balanced brackets allowed
		self.assertEqual(False, naturalnum.validateRhs("(("))
		self.assertEqual(False, naturalnum.validateRhs("()("))
		self.assertEqual(True, naturalnum.validateRhs("()()"))

		## Ensure '$' only used in correct context (followed by alpha character)
		self.assertEqual(False, naturalnum.validateRhs("$1"))
		self.assertEqual(False, naturalnum.validateRhs("$("))
		self.assertEqual(True, naturalnum.validateRhs("$a"))

	#def testValidateLhsAndRhs(self):
	
if __name__ == '__main__':
	unittest.main()
