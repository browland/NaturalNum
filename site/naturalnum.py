import re
import logging

lhsValidatorRegex = r"[0-9a-zA-Z]+"
rhsValidatorRegex = r"[0-9a-zA-Z\(\),\$-]+"  ## Only alphanumerics (inc. hyphen) or these chars: (),$
ruleValidatorRegex = r".+=.+"               ## At least one char each side of '=' delimiter
rhsPlaceholderRegex = r"\$[A-Za-z]"         ## A '$' followed by an alpha char

## Set up logging (users will set up their own handlers)
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
        
logger = logging.getLogger("naturalnum")
logger.setLevel(logging.DEBUG)
h = NullHandler()
logger.addHandler(h)

class Rule:
	"""Holds all attributes of a Rule, 
		including matching and translation logic.
	"""

	def __init__(self, lhs=None, rhs=None):
		self.lhs = lhs
		self.rhs = rhs

	def init(self):
		self.validateLhs()
		self.validateRhs()
		self.validateLhsWithRhs()
		self.buildLhsRegex()
		self.buildLhsGroupDict()
		self.buildRhsWithBackrefs()
		self.splitRhsTokens()
		self.validateRhsTokenList()
		self.initd = True

	def validateLhs(self):
		"""Validates string in LHS of the rule.  All of the following must be true:
				- not empty or null
				- alphanumeric chars only i.e. [0-9a-Z]
				- if alpha chars are present they must all be unique, as they will be
				  used as identifiers
		"""	
		# Ensure lhs is present
		if (self.lhs == None or self.lhs == ""):
			raise RuleValidationException("Could not validate lhs of Rule: [" + 
				"" if self.lhs is None else self.lhs + "] because it is empty.")

		# Ensure lhs is alphanumeric only
		if (re.match(lhsValidatorRegex, self.lhs) == None):
			raise RuleValidationException("Could not validate lhs of Rule: [" + 
				self.lhs + "].  Only alpha/digits allowed.")
	
		# If alpha chars present, ensure they are unique
		if(not self.lhs.isdigit()):
			alphas = [x for x in self.lhs if not x.isdigit()]
			if len(set(alphas)) != len(alphas):
				raise RuleValidationException("Could not validate lhs of Rule: [" + 
					self.lhs + "].  Alpha characters must be unique.")

	def splitRhsTokens(self):
		"""Splits rhs string into a list of tokens, separated by ',' delimiter"""
		self.rhsTokenList = self.rhsWithBackrefs.split(',')

	def validateRhs(self):
		"""Validates string in RHS of a rule.  All of the following must be true:
			- Not empty or null
			- Only alphanumeric chars, or any of: (),$
			- Brackets must be balanced
			- Anything within brackets should resolve to digits
		"""
		# Check rhs is present
		if (self.rhs == None or self.rhs == ""):
			raise RuleValidationException("Could not validate rhs of Rule: [" +
				"" if self.rhs is None else self.rhs + "] because it is empty.")
	   
		logger.debug("Validating rhs: " + self.rhs)
	
		# Check only allowed chars present
		if (re.match(rhsValidatorRegex, self.rhs) == None):
			raise RuleValidationException("Could not validate rhs of Rule: [" + 
				self.rhs + "].  Only alpha/digits or the following chars allowed: (),$")
	
		# Check '$' only precedes an alpha character
		checkNextIsAlpha = False
		for x in self.rhs:
			if x == '$':	
				checkNextIsAlpha = True
			else:
				if checkNextIsAlpha:
					if not x.isalpha():
						raise RuleValidationException("Could not validate rhs of Rule: [" + 
							self.rhs + "].  '$' must always be folowed by an alpha char.")
					checkNextIsAlpha = False
					
		# Ensure everything within brackets is either digits or digivars
		withinBracketsSearchPatt = re.compile("\\(.*?\\)")  # todo move to constant
		for match in re.finditer(withinBracketsSearchPatt, self.rhs):
			matchedVal = self.rhs[match.start()+1:match.end()-1]
			logger.debug("Checking rhs token within brackets [" + matchedVal + "] is digits or digivars")
			digitsOrDigivarsPatt = re.compile("^(\\$[a-zA-Z]|[0-9])+$")  # todo move to constant
			if digitsOrDigivarsPatt.match(matchedVal) == None:
				raise RuleValidationException \
					("Bracketed terms must contain only digits or digivars")

	def validateRhsTokenList(self):
		""""""
		# Check that if brackets exist, they are at the start/end positions
		
		for token in self.rhsTokenList:
			pos = 0
			for x in token:
				if x == '(' and not pos == 0: 				
					raise RuleValidationException("Could not validate rhs token: [" + 
						token + "] - can only start recursion at beginning of token.")
				elif x == ')' and not pos == len(token)-1:
					raise RuleValidationException("Could not validate rhs token: [" + 
						token + "] - can only end recursion at end of token.")
				pos = pos + 1

	def validateLhsWithRhs(self):
		# Check all placeholders on RHS appear on LHS
		# 1. Find set of all LHS placeholders
		lhsPlaceholders = set([x for x in self.lhs if not x.isdigit()])

		# 2. Find set of all RHS placeholders
		placeholderDetected = False
		rhsPlaceholdersList = []	
		for x in self.rhs:
			if x == '$':
				placeholderDetected = True
			else:
				if placeholderDetected:
					rhsPlaceholdersList.append(x)
					placeholderDetected = False
		rhsPlaceholders = set(rhsPlaceholdersList)
	
		# 3. Check RHS placeholders is a subset of LHS placeholders 
		# (not necessarily vice-versa)
		if not rhsPlaceholders <= lhsPlaceholders:
			raise RuleValidationException("Could not validate Rule lhs [" + 
				self.lhs + "] with rhs: [" + self.rhs + 
				"] - placeholder(s) on rhs do not appear on lhs.")
		
	def buildLhsRegex(self):
		lhsRegex = "^"
		for x in self.lhs:
			if x.isdigit():
				lhsRegex = lhsRegex + x
			else:
				lhsRegex = lhsRegex + "(.)"
		lhsRegex = lhsRegex + "$"
		self.lhsRegex = lhsRegex
		self.lhsRegexPattern = re.compile(lhsRegex)

	def buildLhsGroupDict(self):
		"""Builds a dictionary of placeholder character to group number.
		"""
		self.lhsGroupDict = {}
		alphas = [x for x in self.lhs if not x.isdigit()]
		count = 1
		for x in alphas:
			self.lhsGroupDict[x] = count
			count = count + 1

	def buildRhsWithBackrefs(self):
		"""Builds the pattern for the resulting output string for this rule.
			This can either be a single token, e.g.:
			1=one
			or a list of tokens (just a comma-separated string at this stage),
			e.g.:
			21=twenty,one
			In more complex cases (when we want to capture digits from the lhs
			and feed them back into the rule engine), we will replace instances
			of $<digivar> on the rhs with the appropriate regex backreference.
			E.g. for:
			tu=$t0,u
			The resulting rhs expression will be: \\g<1>0,\\g<2>
			So '21' would be replaced with 20,1.  Note the use of g<num> format
			for regex backreferences, this is to disambiguate cases such as 
			\\10 - which should be interpreted as backreference to group number 1,
			followed by a literal 0, not as a backreference to group number 10.
			 
			Additionally, when recursion is to be used upon a token (the resulting 
			rhs token should be fed back into the rule engine), the rhs expression 
			is enclosed in parentheses, e.g.:
			tu=($t0),($u)
			would result in each of the two rhs tokens being fed back through the
			rule engine, and being replaced with the result.  This strategy allows
			reuse among rules.
		"""
		## Replace all instances of "$<char>" in rhs expression with a 
		## backreference to the group number matching that char in the LHS regex.
		rhsWithBackrefs = self.rhs
		rhsPlaceholderSearchPatt = re.compile(rhsPlaceholderRegex)

		for match in re.finditer(rhsPlaceholderSearchPatt, self.rhs):
			matchedVal = self.rhs[match.start():match.end()]
			backref = "\\g<" + str(self.lhsGroupDict[matchedVal[1:]]) + ">"
			rhsWithBackrefs = rhsWithBackrefs.replace(matchedVal, backref)
		self.rhsWithBackrefs = rhsWithBackrefs

	def matches(self, value):
		"""Returns True if the whole of 'value' matches this rule, else False"""
		return self.lhsRegexPattern.match(value)

	def resolve(self, value):
		if not self.matches(value):
			raise RuleUsageException("Rule does not match value, cannot resolve")
		tokenList = []
		for rhsToken in self.rhsTokenList:
			logger.debug("replacing [" + value + "] with [" + rhsToken + \
				"] in context of match regex [" + self.lhsRegex + "]")
			resolvedRhsToken = self.lhsRegexPattern.sub(rhsToken, value)
			tokenList.append(resolvedRhsToken)
		return tokenList
		
	def __str__(self):
		return "[" + self.lhs + "=" + self.rhs + "], [" + self.lhsRegex + "=" + self.rhsWithBackrefs + "]"

class RuleValidationException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class RuleUsageException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)
		
class RuleEvaluationException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class RuleList:
	def __init__(self):
		self.rules = []
		
	def __len__(self):
		return len(self.rules)

	def add(self, rule):
		self.rules.append(rule)

	def search(self, value):
		for rule in self.rules:
			if rule.matches(value):
				return rule			

class RuleEngine:
	def __init__(self, ruleList):
		self.ruleList = ruleList

	@classmethod
	def fromLangFilename(cls, fileName):
		logger.debug("fromLangFilename()")
		f = open(fileName, 'r')
		logger.debug("opened config file [" + fileName + "]")
		ruleList = RuleList()
		for line in f:
			logger.debug("read line: [" + line[0:-1] + "]")
			rule = validateAndParseRule(line)
			if rule != None:
				logger.debug("Adding Rule to RuleList")
				ruleList.add(rule)
			else:
				logger.debug("No rule found, skipping this line")
		re = RuleEngine(ruleList)
		logger.debug("finished loading RuleEngine")
		return re

	def resolve(self, value):
		logger.debug("resolve() value=[" + value + "]")
		matchedRule = self.ruleList.search(value)
		if not matchedRule == None:
			logger.debug("found matched rule: " + str(matchedRule))
			rhsTokens = matchedRule.resolve(value)
			rhsTokensFollowingRecursion = []
			for rhsToken in rhsTokens:
				## If current rhs token is enclosed in brackets, replace it with
				## the result of feeding the value (without brackets) back through
				## the rule engine.
				if rhsToken[0:1] == '(' and rhsToken[-1:] == ')':
					rhsTokenToRecurse = rhsToken[1:-1]
					logger.debug("Recursing value [" + rhsTokenToRecurse + "] back through rule engine")
					resultAfterRecursion = self.resolve(rhsTokenToRecurse)
					if resultAfterRecursion == None:
						raise RuleEvaluationException("Could not match fragment of result [" + \
							rhsTokenToRecurse + "] to a rule")	
					rhsTokensFollowingRecursion = rhsTokensFollowingRecursion + \
						resultAfterRecursion
				else:
					rhsTokensFollowingRecursion.append(rhsToken)					
			return rhsTokensFollowingRecursion
		else:
			logger.debug("could not find matching rule")
			return None

def validateAndParseRule(rule):
	"""Validates and parses entire rule string, returning it as a Rule object.  
		Any characters after '#' in the rule string are ignored.
		The rule string must have a '=' delimiter, surrounded by a valid LHS and 
		RHS.

		Return values:
		- If entire rule is valid, a Rule object
		- If rule is invalid, a RuleValidationException will be raised
		- If rule was only a comment, None will be returned
	"""
	logger.debug("validateAndParseRule()")

	# Get rule without comments, return None if rule is only a comment
	commentCharPos = rule.find('#')
	if commentCharPos != -1:
		ruleWithoutComment = rule[:commentCharPos].rstrip()
	else:
		ruleWithoutComment = rule.rstrip()
	if len(ruleWithoutComment) == 0:
		return None
	
	# Check that rule without comment is some chars, delimited by '='
	if (re.match(ruleValidatorRegex, ruleWithoutComment) == None):
		raise RuleValidationException("Could not validate rule: [" + 
			rule + "].  Format should be: <lhs>=<rhs>")

	# Split rule into LHS and RHS, create Rule object and run its validations
	parts = ruleWithoutComment.split('=')
	lhs = parts[0]
	rhs = parts[1]
	rule = Rule(lhs, rhs)
	rule.init()
	return rule

