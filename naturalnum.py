import re

lhsValidatorRegex = r"[0-9a-zA-Z]+"

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
