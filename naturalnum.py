import re

lhsValidatorRegex = r"[0-9a-zA-Z]+"
rhsValidatorRegex = r"[0-9a-zA-Z\(\),\$]+"  ## Only alphanumerics or these chars: (),$
ruleValidatorRegex = r".+=.+"               ## At least one char each side of '=' delimiter

def validateAndParseRule(rule):
	"""Validates and parses entire rule.  Any characters after '#' are ignored.
		If any characters remain, the remainder must have a '=' delimiter, surrounded by
		a valid LHS and RHS (which will be validated by the corresponding functions).

		Return values:
		- If entire rule is valid, a tuple containing LHS and RHS will be returned
		- If rule is invalid, None will be returned
		- If rule was only a comment, an empty tuple will be returned
	"""

	# Get rule without comments, return () if rule is only a comment
	commentCharPos = rule.find('#')
	if commentCharPos != -1:
		ruleWithoutComment = rule[:commentCharPos].rstrip()
	else:
		ruleWithoutComment = rule.rstrip()

	if len(ruleWithoutComment) == 0:
		return ()
	
	# Check that rule without comment is some chars, delimited by '='
	if (re.match(ruleValidatorRegex, ruleWithoutComment) == None):
		return None	

	# Split rule into LHS and RHS and validate those separately
	parts = ruleWithoutComment.split('=')
	lhs = parts[0]
	rhs = parts[1]
	if validateLhs(lhs):
		if validateRhs(rhs):
			return (lhs, rhs)
		else:	
			return None
	else:
		return None

def validateLhs(lhs):
	"""Validates string in LHS of a rule.  All of the following must be true:
        - not empty or null
        - alphanumeric chars only i.e. [0-9a-Z]
        - if alpha chars are present they must all be unique, as they will be
          used as identifiers
	"""	
	if (lhs == None or lhs == ""):
		return False

	if (re.match(lhsValidatorRegex, lhs) == None):
		return False
	
	if(lhs.isdigit()): return True
	else:
		alphas = [x for x in lhs if not x.isdigit()]
		return len(set(alphas)) == len(alphas)

def validateRhs(rhs):
	"""Validates string in RHS of a rule.  All of the following must be true:
		- Not empty or null
		- Only alphanumeric chars, or any of: (),$
		- Brackets must be balanced
	"""
	# Check rhs is present
	if (rhs == None or rhs == ""):
		return False

	# Check only allowed chars present
	if (re.match(rhsValidatorRegex, rhs) == None):
		return False

	# Check brackets are balanced
	depth = 0
	brackets = [x for x in rhs if x in ('(', ')')]
	for x in brackets:
		if x == '(':
			depth = depth + 1
		else:
			depth = depth - 1
	if depth != 0:
		return False

	# Check '$' only precedes an alpha character
	checkNextIsAlpha = False
	for x in rhs:
		if x == '$':	
			checkNextIsAlpha = True
		else:
			if checkNextIsAlpha:
				if not x.isalpha():
					return False
				checkNextIsAlpha = False 
	return True

def validateLhsWithRhs(lhs, rhs):
	# Check all placeholders on RHS appear on LHS
	# 1. Find set of all LHS placeholders
	lhsPlaceholders = set([x for x in lhs if not x.isdigit()])

	# 2. Find set of all RHS placeholders
	placeholderDetected = False
	rhsPlaceholdersList = []	
	for x in rhs:
		if x == '$':
			placeholderDetected = True
		else:
			if placeholderDetected:
				rhsPlaceholdersList.append(x)
				placeholderDetected = False
	rhsPlaceholders = set(rhsPlaceholdersList)
	
	# 3. Check RHS placeholders is a subset of LHS placeholders (not necessarily vice-versa)
	if not rhsPlaceholders <= lhsPlaceholders:
		return False
	return True
