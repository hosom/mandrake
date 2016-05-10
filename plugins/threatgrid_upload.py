import requests
requests.packages.urllib3.disable_warnings()

_HOST = 'panacea.threatgrid.com'

class Plugin:
	
	__NAME__ = 'threatgrid_upload'

	def __init__(self, args):

		self.tags = ''
		self.os = ''
		self.osver = ''
		self.source = ''
		self.vm = 'win7'

		self.api_key = args.get('api_key')

		self.params = {
			'tags' : self.tags,
			'os' : self.os,
			'osver' : self.osver,
			'source' : self.source,
			'vm' : self.vm,
			'api_key' : self.api_key
		}

	def analyze(self, afile):
		if hasattr(afile, 'sandbox') and afile.sandbox:
			fname = afile.path.split('/')[-1]
			self.params['filename'] = fname
			r = requests.post('https://%s/api/v2/samples' % (_HOST), 
								data=self.params,
								files={'sample':open(afile.path, 'rb')})
			if r.status_code == 200:
				afile.threatgrid_status = 'Success'
			else:
				afile.threatgrid_status = 'Fail'
			del self.params['filename']