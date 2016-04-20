import smtplib
import sys

from email.mime.text import MIMEText

class Plugin:

	__NAME__ = 'smtp'

	def __init__(self, args):
		
		self.email_on_alert = args.get('email_on_alert')
		self.email_on_suspicious = args.get('email_on_suspicious')
		
		if self.email_on_alert is None:
			self.email_on_alert = True
		if self.email_on_suspicious is None:
			self.email_on_suspicious = True

		self.email_on_errors = args.get('email_on_errors')
		if self.email_on_errors is None:
			self.email_on_errors = True

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