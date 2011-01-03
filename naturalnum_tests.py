import unittest
from naturalnum import *
import logging.config

## Set up logging
logging.config.fileConfig("logging.conf")

# create logger for tests
logger = logging.getLogger("naturalnum_tests")

class TestNaturalNum(unittest.TestCase):
	#def setUp(self):

	def testLoadConfig(self):
		logger.info("testLoadConfig()")
		## Trigger load of valid config file and ensure everything is set up
		cfgFilename = "config/en_GB.lang"  # todo create seperate test config file
		ruleEngine = RuleEngine.fromLangFilename(cfgFilename)
		self.assertEquals(44, len(ruleEngine.ruleList))
		
	def testValidateLhs(self):
		logger.info("testValidateLhs()")
		## Ensure only alphanumerics allowed
		self.assertRaises(RuleValidationException, Rule("", None).validateLhs)
		self.assertRaises(RuleValidationException, Rule(None, None).validateLhs)
		self.assertRaises(RuleValidationException, Rule(".", None).validateLhs)
		self.assertRaises(RuleValidationException, Rule("", None).validateLhs)
		try:
			Rule("1", None).validateLhs()
			Rule("123", None).validateLhs()
			Rule("h", None).validateLhs()
			Rule("htu", None).validateLhs()
		except RuleValidationException:
			self.fail("No validation exception should be raised")

		## Ensure no repetition of alpha chars allowed
		self.assertRaises(RuleValidationException, Rule("hh", None).validateLhs)
		self.assertRaises(RuleValidationException, Rule("h1h", None).validateLhs)

	def testSplitRhsTokens(self):
		rule = Rule("123", "one,hundred,and,twenty,three")
		rule.init()
		self.assertEquals(5, len(rule.rhsTokenList))

	def testValidateRhs(self):
		## Ensure only alphanumerics, '(', ')', ',', '$' allowed
		self.assertRaises(RuleValidationException, Rule(None, "").validateRhs)
		self.assertRaises(RuleValidationException, Rule(None, None).validateRhs)
		self.assertRaises(RuleValidationException, Rule(None, ".").validateRhs)
		self.assertRaises(RuleValidationException, Rule(None, " ").validateRhs)

		## Success scenario
		try:
			Rule(None, "123($a$b),123,(123)").validateRhs()
		except RuleValidationException:
			self.fail("Should not raise RuleValidationException")

		## Ensure '$' only used in correct context (followed by alpha character)
		self.assertRaises(RuleValidationException, Rule(None, "$1").validateRhs)
		self.assertRaises(RuleValidationException, Rule(None, "$(").validateRhs)
		try:
			Rule(None, "$a").validateRhs()
		except RuleValidationException:
			self.fail("Should not raise RuleValidationException")
			
		## Ensure we fail if the token to be recursed would not result in digits 
		## only, e.g. missing $ symbol.
		self.assertRaises(RuleValidationException, Rule(None, "($ab)").validateRhs)		

	def testValidateRhsTokenList(self):
		## Ensure brackets only allowed to encompass an entire token
		rule = Rule("htu", "$h,100,test($t$u)")
		self.assertRaises(RuleValidationException, rule.init)

		rule = Rule("htu", "$h,100,($t$u)")
		try:
			rule.init()
		except RuleValidationException:
			self.fail("Should not raise RuleValidationException")
		
	def testValidateLhsWithRhs(self):
		## Ensure all chars on RHS preceded by $ appear on LHS
		self.assertRaises(RuleValidationException, Rule("a", "$d").validateLhsWithRhs)
		self.assertRaises(RuleValidationException, Rule("abc", "$a$b$d").validateLhsWithRhs)
		try:
			Rule("abc", "$a$b$c").validateLhsWithRhs()
		except RuleValidationException:
			self.fail("Should not raise RuleValidationException")

	def testValidateAndParseRule(self):
		## Here we are only testing the function which drives Rule creation from a raw
		## string, not the internals of the Rule creation (validation etc).		
		## Therefore these tests should always have a valid LHS and RHS.

		## Ensure commented lines validate OK
		self.assertEqual(None, validateAndParseRule("#this is a comment"))
		rule = validateAndParseRule("abc=123 #this is a comment")
		self.assertEqual("abc", rule.lhs)
		self.assertEqual("123", rule.rhs)

		## Ensure only 2 sets of characters, delimited by '=' is allowed
		self.assertRaises(RuleValidationException, validateAndParseRule, "abcabc")
		self.assertRaises(RuleValidationException, validateAndParseRule, "abcabc #=comment")
		rule = validateAndParseRule("123a=$a")
		self.assertEqual("123a", rule.lhs)
		self.assertEqual("$a", rule.rhs)

	def testBuildLhsRegex(self):
		rule = Rule("123", "one hundred and twenty three")
		rule.init()
		self.assertEqual("^123$", rule.lhsRegex)
		self.assertFalse(rule.lhsRegexPattern == None)

		rule = Rule("1tu", "one hundred and etc")
		rule.init()
		self.assertEqual("^1(.)(.)$", rule.lhsRegex)		
		self.assertFalse(rule.lhsRegexPattern == None)

	def testBuildLhsGroupDict(self):
		rule = Rule("1tu", "one hundred and etc")
		rule.init()
		self.assertEquals(rule.lhsGroupDict['t'], 1)
		self.assertEquals(rule.lhsGroupDict['u'], 2)

	def testBuildRhsWithBackrefs(self):
		rule = Rule("123", "one, hundred, and, twenty, three")
		rule.init()
		self.assertEqual("one, hundred, and, twenty, three", rule.rhsWithBackrefs)

		rule = Rule("htu", "($h$t$u)")
		rule.init()
		self.assertEqual(r"(\g<1>\g<2>\g<3>)", rule.rhsWithBackrefs)

		rule = Rule("htu", "$h,100,and,($t$u)")
		rule.init()
		self.assertEqual(r"\g<1>,100,and,(\g<2>\g<3>)", rule.rhsWithBackrefs)

	def testRuleMatches(self):
		rule = Rule("htu", "($h$t$u)")
		rule.init()
		self.assertTrue(rule.matches("123"))
		self.assertFalse(rule.matches("12"))

	def testRuleResolve(self):
		rule = Rule("htu", "$h$t$u")
		rule.init()
		rhsTokens = rule.resolve("123")
		self.assertEquals(["123"], rhsTokens)

	def testRuleListSearch(self):
		ruleList = RuleList()
		rule = Rule("h", "test")
		rule.init()
		ruleList.add(rule)
		rule = Rule("ht", "test")
		rule.init()
		ruleList.add(rule)		
		rule = Rule("htu", "test")
		rule.init()
		ruleList.add(rule)
		rule = ruleList.search("123")
		self.assertEquals("htu", rule.lhs)

	def testRuleEngineSearch(self):
		## non-recursive
		ruleList = RuleList()
		rule = Rule("h", "test")
		rule.init()
		ruleList.add(rule)
		rule = Rule("ht", "test")
		rule.init()
		ruleList.add(rule)		
		rule = Rule("htu", "test")
		rule.init()
		ruleList.add(rule)
		ruleEngine = RuleEngine(ruleList)
		result = ruleEngine.resolve("123")
		self.assertEquals(["test"], result)
		
		## recursive
		ruleList = RuleList()
		rule = Rule("tu", "twenty,one")
		rule.init()
		ruleList.add(rule)		
		rule = Rule("htu", "three,hundred,and,($t$u)")
		rule.init()
		ruleList.add(rule)
		ruleEngine = RuleEngine(ruleList)
		result = ruleEngine.resolve("321")
		self.assertEquals(["three","hundred","and","twenty","one"], result)
		
	def testRuleEngineResolve(self):
		eng = RuleEngine.fromLangFilename("config/en_GB.lang")
		self.assertEquals(["one", "thousand", "two", "hundred", "and", "thirty", "four"], eng.resolve("1234"))

if __name__ == '__main__':
	unittest.main()
