from mod_python import apache
from mod_python import util
from naturalnum import *

def index(req):
   """ Services requests via apache.  Requests would usually be submitted
       by the AJAX form handler."""
   docRoot = req.document_root()
   form = util.FieldStorage(req,keep_blank_values=1)
   lang = form.get("lang", None)
   value = form.get("number", None)
   json = callNaturalNum(docRoot, lang, value)
   
   return json

def callNaturalNum(docRoot, lang, value):
   """ Delegates look-up of natural language represention of digits entered,
       by calling NaturalNum. """
	configFileName = docRoot + "/naturalnum/config/" + lang + ".lang"
	eng = RuleEngine.fromLangFilename(configFileName)
	
	return tokensToJson(eng.resolve(value))

def tokensToJson(tokens):
   """ Converts the list of strings returned by NaturalNum to JSON."""
	json = '{"tokens": ['

	for token in tokens:
		json = json + '"' + token + '", '

	# Append trailing closing array bracket and closing outer curly bracket
	# We strip off the last 2 chars of the json because it will contain an
	# extra unnecessary trailing comma and space.
	json = json[0:-2] + ']}'
	return json
