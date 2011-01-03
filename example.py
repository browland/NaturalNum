from naturalnum import *
import sys

def example():
	if len(sys.argv) != 3:
		usage()
	else:
		val = sys.argv[1]
		locale = sys.argv[2]
		configFileName = "config/" + locale + ".lang"
		eng = RuleEngine.fromLangFilename(configFileName)
		print eng.resolve(val)

def usage():
	print "Usage: example.py <integer to translate> <locale code>"

if __name__ == '__main__':
	example()
