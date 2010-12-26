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

	def testValidateLhsWithRhs(self):
		## Ensure all chars on RHS preceded by $ appear on LHS
		self.assertEqual(False, naturalnum.validateLhsWithRhs("a", "$d"))
		self.assertEqual(False, naturalnum.validateLhsWithRhs("abc", "$a$b$d"))
		self.assertEqual(True, naturalnum.validateLhsWithRhs("abc", "$a$b$c"))

	def testValidateAndParseRule(self):
		## These tests should always have a valid LHS and RHS, we're not testing LHS/RHS
		## validations here

		## Ensure commented lines validate OK
		self.assertEqual((), naturalnum.validateAndParseRule("#this is a comment"))
		self.assertEqual(("abc", "123"), naturalnum.validateAndParseRule("abc=123 #this is a comment"))

		## Ensure only 2 sets of characters, delimited by '=' is allowed
		self.assertEqual(None, naturalnum.validateAndParseRule("abcabc"))
		self.assertEqual(("123a", "$a"), naturalnum.validateAndParseRule("123a=$a"))
	
if __name__ == '__main__':
	unittest.main()
