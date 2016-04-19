class Plugin:
	
	def __init__(self, args):
		self.args = args

	def analyze(self, afile):
		attrs = vars(afile)
		print('----------------------------------------------')
		print('\n'.join('%s: %s' % item for item in attrs.items()))
