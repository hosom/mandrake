import inotify.adapters as inotify

import json
import traceback

from argparse import ArgumentParser
from ConfigParser import ConfigParser

class FileAnalysis:
	'''Class representing a file and its analysis results.
	'''
	def __init__(self, path):
		'''Initialize a new File object.

		Args:
			path (str): The file path to the file.
		'''
		self.path = path
		self.plugin_output = {}
		self.suspicious = False
		self.alert = False

def parse_config(config_path):
	'''Parse a configuration file and return a dictionary of the sections.

	Args:
		config_path (str): The path of the configuration file to be parsed.

	Returns:
		dict: The parsed configuration file.
	'''
	config = ConfigParser()
	config.read(config_path)
	parsed_config = {}
	for section in config.sections():
		parsed_config[section] = {}
		for key, val in config.items(section):
			parsed_config[section][key] = val
	return parsed_config

def order_plugins(config):
	'''Load and return a list of Plugins in the order that they should be 
	run against a file.

	Args:
		config (dict): A dictionary representation of a parsed configuration.

	Returns:
		list: An ordered list of plugins
	'''

	plugins = [[], [], [], [], [], [], [], [], [], []]
	for section in config:
		# Determine if a plugin has been enabled
		enabled = config[section].get('enabled')
		if enabled is not None and enabled == 'true':
			enabled = True
		elif enabled is None:
			enabled = True
		else:
			enabled = False

		if not enabled:
			next

		# Collect plugin arguments from the configuration file
		args = config[section].get('args')
		if args is not None:
			args = json.loads(args)
		else:
			args = {}

		priority = config[section].get('priority')
		if priority is not None:
			priority = int(priority)
		else:
			priority = 8

		plugins[priority] = plugins[priority] + [(section, args)]

	return plugins

def load_plugin(plugin):
	return __import__('plugins.%s' % (plugin), 
			globals(), 
			locals(), 
			['Plugin'], 
			-1)

def init_plugins(plugins):
	'''Accepts a list formatted by order_plugins and returns a list of open
	plugins ready for use by analyze.

	Args:
		plugins (list): Should be formatted as a list of lists (order_plugins)

	Returns:
		list: a list of plugin objects open and ready to use
	'''
	open_plugins = []
	for plugin_group in plugins:
		open_group = []
		for plugin in plugin_group:
			x = load_plugin(plugin[0])
			open_group = open_group + [x.Plugin(plugin[1])]
		open_plugins = open_plugins + [open_group]
	return open_plugins

def analyze(analyzers, file_object):
	'''Runs all of the analyzers on a file.

	Args:
		analyzers (list): The formatted list of analyzers to execute against.
		file_object (FileAnalysis): The object to work with and write to.

	Returns:
		FileAnalysis: Object with the results from all analysis.
	'''
	for analyzer_group in analyzers:
		for analyzer in analyzer_group:
			try:
				analyzer.analyze(file_object)
			except Exception as err:
				## TODO: This neeeds to be expanded to provide better
				## error feedback so that plugin authors can troubleshoot
				## their code
				print('An error occurred during plugin execution in plugin %s.' % analyzer.__NAME__)

	return file_object

def main():
	p = ArgumentParser(description='Monitor a directory for new files.')
	p.add_argument('directory', 
		help='Directory to monitor.')
	p.add_argument('-c', '--config',
		default='mandrake.conf',
		help='Configuration file path.')
	args = p.parse_args()

	parsed_config = parse_config(args.config)
	ordered_plugins = order_plugins(parsed_config)

	modules = init_plugins(ordered_plugins)

	i = inotify.Inotify()
	i.add_watch(args.directory)
	
	try:
		for event in i.event_gen():
			if event is not None and event[1] == ['IN_CLOSE_WRITE']:
				fpath = '%s/%s' % (event[2], event[3])
				f = FileAnalysis(fpath)
				analyze(modules, f)
	finally:
		i.remove_watch(args.directory)

if __name__ == '__main__':
	main()