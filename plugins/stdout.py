import json

from distutils.util import strtobool

class Plugin:

	__NAME__ = 'stdout'
	
	def __init__(self, args):
		self.args = args

		# Print JSON objects?
		try:
			self.json = strtobool(args.get('json'))
		except (ValueError, AttributeError) as e:
			self.json = False

	def analyze(self, afile):
		'''Print the analysis object to stdout.

		This is useful for debugging and for basic logging.

		Args:
			afile (FileAnalysis): The file to be analyzed.

		Returns:
			None
		'''

		if self.json:
			attrs = afile.__dict__
			#or attr in attrs:
			#	attrs[attr] = str(attrs[attr]).encode('utf-8', errors='replace')
			print(json.dumps(attrs))
		else:
			attrs = vars(afile)
			print('----------------------------------------------')
			print('\n'.join('%s: %s' % item for item in attrs.items()))
