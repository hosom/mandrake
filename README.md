# mandrake
file processing stuff

Mandrake keeps an eye on a directory and processes new files using plugins.

Want to add some special monitoring? That's easy! Plugins should be added to the **plugins** directory.

Support for custom plugin locations has not been added yet.

```python
from hashlib import md5

class Plugin:
  '''Each plugin must have a class named Plugin.'''
  
  __NAME__ = 'md5'
  '''It's polite to give your plugin a name'''
  
  def __init__(self, args):
    '''Every plugin must implement __init__ and accept two arguments.
    
    Args:
      self (self): this is a reference to the Plugin's 'self'.
      args (dict): this is a dictionary of arguments to be received by the plugin.
      
    Returns:
      None
    '''
	self.chunk_size = args.get('chunk_size')
	if self.chunk_size == None:
		self.chunk_size = 4096
	
	def analyze(self, afile):
	  '''Every plugin must also implement analyze, which must accept two arguments.
	  
	  Args:
	    self (self): this is the reference to the Plugin's 'self'.
	    afile (FileAnalysis): this is the common object to be used to store analysis information.
	  Returns:
	    None
	  '''
	  hasher = md5()
  		with open(afile.path, 'rb') as f:
  			for chunk in iter(lambda: f.read(self.chunk_size), b""):
  				hasher.update(chunk)
  
  			afile.md5 = hasher.hexdigest()
  			afile.plugin_output[self.__NAME__] = afile.md5
```

Now all that is left is to register your plugin. Open up your **mandrake.conf** and add the following:

```
[md5]
enabled = true
priority = 1
chunk_size = 2048
```

This will register your plugin for use within Mandrake.
