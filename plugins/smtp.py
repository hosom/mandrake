import smtplib
import sys

from distutils.util import strtobool
from email.mime.text import MIMEText

class Plugin:

	__NAME__ = 'smtp'

	def __init__(self, args):
		
		# Determine whether or not to email on errors, alerts, 
		# or suspicious files
		try:
			self.email_on_alert = strtobool(args.get('email_on_alert'))
		except ValueError, AttributeError:
			self.email_on_alert = False
		try: 
			self.email_on_suspicious = strtobool(args.get('email_on_suspicious'))
		except ValueError, AttributeError:
			self.email_on_suspicious = False
		try:
			self.email_on_errors = strtobool(args.get('email_on_errors'))
		except ValueError, AttributeError:
			self.email_on_errors = False

		# Mail configuration
		self.mailserver = args.get('mailserver')
		if self.mailserver is None:
			sys.exit('smtp plugin loaded, but no mailserver found in config')
		self.mailfrom = 'mandrake@localhost'
		if args.get('mailfrom') is not None:
			self.mailfrom = args.get('mailfrom')
		self.rcptto = args.get('rcptto')
		if self.rcptto is None:
			sys.exit('smtp plugin loaded, but no rcptto found in config')

	def analyze(self, afile):
		'''Send emails related to files based on the flags that have been set.

		Args:
			afile (FileAnalysis): The file being analyzed.

		Returns:
			None
		'''
		send_email = False
		subject = 'Mandrake file detection'
		if self.email_on_alert and afile.alert:
			send_email = True
			subject = '[Alert] %s' % (subject)
		if self.email_on_suspicious and afile.suspicious:
			send_email = True
			subject = '[Suspicious] %s' % (subject)
		if self.email_on_errors and len(afile.errors) > 0:
			send_email = True
			subject = '[Error] %s' % (subject)

		if send_email:
			s = smtplib.SMTP(self.mailserver)
			attrs = vars(afile)
			body = '\n'.join('%s: %s' % item for item in attrs.items())
			msg = MIMEText(body)
			msg['Subject'] = subject
			msg['From'] = self.mailfrom
			msg['To'] = ','.join(self.rcptto)
			s.sendmail(self.mailfrom, self.rcptto, msg.as_string())