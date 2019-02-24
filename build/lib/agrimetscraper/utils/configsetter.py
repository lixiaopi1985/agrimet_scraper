from configparser import RawConfigParser



class MyConfig(RawConfigParser):
	pass



class Configger:

	def __init__(self, cfg_path):
		self.cfg_path = cfg_path


	def Setcfg(self, section, keys, values):

		config = MyConfig()
		config.read(self.cfg_path)

		config.set(section, keys, values)

		with open(self.cfg_path, 'w') as config_handle:
			config.write(config_handle)
			
	def Getcfg(self, section, keys):

		config = MyConfig()
		config.read(self.cfg_path)
		
		return config[section][keys]