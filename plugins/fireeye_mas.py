import requests
requests.packages.urllib3.disable_warnings()

class Plugin:

	__NAME__ = 'fireeye_mas'

	def __init__(self, args):

		self.analysistype = '1'
		self.priority = '0'
		self.profiles = 'win7-sp1'
		self.force = 'true'
		self.application = '2'
		self.prefetch = '0'
		self.timeout = '500'


		self.host = args.get('host')
		self.user = args.get('user')
		self.password = args.get('password')

		self.validate_tls = False

		self._options = {'options':'''
			{"analysistype" : "1",
			"priority" : "0",
			"profiles" : ["win7-sp1"],
			"force" : "true", 
			"application" : "2",
			"prefetch" : "0",
			"timeout" : "500"}
		'''}

	def authenticate(self):
		'''Handle the basic auth for the fireeye api. Sigh.
		'''
		r = requests.post('https://%s/wsapis/v1.1.0/auth/login' % (self.host),
				auth=(self.user, self.password),
				verify=self.validate_tls)

		if r.status_code == 200:
			self.xfeapitoken = r.headers['x-feapi-token']

	def submit(self, afile):
		r = requests.post('https://%s/wsapis/v1.1.0/submissions' % (self.host),
				headers={'x-feapi-token' : self.xfeapitoken},
				data=self._options,
				files={afile.path: open(afile.path, 'rb')},
				verify=self.validate_tls)
		if r.status_code == 200:
			return True
		else:
			return False

	def analyze(self, afile):
		'''Upload the file to the fireeye appliance for analysis.
		'''
		if hasattr(afile, 'sandbox') and afile.sandbox:
			if hasattr(self, 'xfeapitoken'):
				submit_success = self.submit(afile)
				if submit_success == True:
					afile.fireeeye_status = 'Success'
				else:
					self.authenticate()
					submit_success = self.submit(afile)
					if submit_success == True:
						afile.fireeeye_status = 'Success'
					else:
						afile.fireeeye_status = 'Fail'
			else:
				self.authenticate()
				submit_success = self.submit(afile)
				if submit_success == True:
					afile.fireeeye_status = 'Success'
				else:
					afile.fireeeye_status = 'Fail'
		
