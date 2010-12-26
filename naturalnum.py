import re

lhsValidatorRegex = r"[0-9a-zA-Z]+"
rhsValidatorRegex = r"[0-9a-zA-Z\(\),\$]+"  ## Only alphanumerics or these chars: (),$

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
