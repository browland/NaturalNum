import cgi

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from naturalnum import *

def callNaturalNum(docRoot, lang, value):
   """ Delegates look-up of natural language represention of digits entered,
       by calling NaturalNum. """
   configFileName = docRoot + "/config/" + lang + ".lang"
   
   // todo: Fix so NaturalNum can be bootstrapped one time.
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

class JsonHandler (webapp.RequestHandler):
	def get(self):
		lang = self.request.get('lang')
		value = self.request.get('value')
		docRoot = '.'
		json = callNaturalNum(docRoot, lang, value)
		self.response.out.write(json)

application = webapp.WSGIApplication(
	[('/nn-json.py', JsonHandler)],
	debug=True)
	
def main():
	run_wsgi_app(application)
	
if __name__ == "__main__":
	main()


