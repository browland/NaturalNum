import cgi
import os
import glob

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from naturalnum import *

## Rule Engines, by locale code (e.g. 'en_GB')
engines = {}

## Build the Rule Engines by scanning the config file directory
path = 'config/'
for infile in glob.glob( os.path.join(path, '*.lang') ):
    lang = infile.split('.')[0].split('\\')[1]
    eng = RuleEngine.fromLangFilename(infile)
    engines[lang] = eng

def callNaturalNum(docRoot, lang, value):
   """ Delegates look-up of natural language represention of digits entered,
       by calling NaturalNum. """

   eng = engines[lang]
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

# Handles requests for JSON representing a list of natural language tokens, 
# based on a numeric value
class JsonHandler (webapp.RequestHandler):
	def get(self):
		lang = self.request.get('lang')
		value = self.request.get('value')
		docRoot = '.'
		json = callNaturalNum(docRoot, lang, value)
		self.response.out.write(json)

application = webapp.WSGIApplication(
	[('/nnjson.py', JsonHandler)],
	debug=True)
	
def main():
	run_wsgi_app(application)
	
if __name__ == "__main__":
	main()


