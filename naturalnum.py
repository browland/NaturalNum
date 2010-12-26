import re

lhsValidatorRegex = r"[0-9a-zA-Z]+"
rhsValidatorRegex = r"[0-9a-zA-Z\(\),\$]+"  ## Only alphanumerics or these chars: (),$
ruleValidatorRegex = r".+=.+"               ## At least one char each side of '=' delimiter

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

	def validateRhs(self):
		"""Validates string in RHS of a rule.  All of the following must be true:
			- Not empty or null
			- Only alphanumeric chars, or any of: (),$
			- Brackets must be balanced
		"""
		# Check rhs is present
		if (self.rhs == None or self.rhs == ""):
			raise RuleValidationException("Could not validate rhs of Rule: [" + 
				"" if self.rhs is None else self.rhs + "] because it is empty.")
	
		# Check only allowed chars present
		if (re.match(rhsValidatorRegex, self.rhs) == None):
			raise RuleValidationException("Could not validate rhs of Rule: [" + 
				self.rhs + "].  Only alpha/digits or the following chars allowed: (),$")

		# Check brackets are balanced
		depth = 0
		brackets = [x for x in self.rhs if x in ('(', ')')]
		for x in brackets:
			if x == '(':
				depth = depth + 1
			else:
				depth = depth - 1
		if depth != 0:
			raise RuleValidationException("Could not validate rhs of Rule: [" + 
				self.rhs + "] - brackets are unbalanced.")
	
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

class RuleValidationException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

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

