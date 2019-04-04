from configparser import RawConfigParser


class Configtuner(RawConfigParser):

    def __init__(self, cfg_path):
        self.cfg_path = cfg_path

    def setconfig(self, section, key, val):
        config = RawConfigParser()
        config.read(self.cfg_path)
        config.set(section, key, val)
        with open(self.cfg_path, 'w') as config_handle:
            config.write(config_handle)

    def getconfig(self, section, key):

        config = RawConfigParser()
        config.read(self.cfg_path)

        return config[section][key]


    def __str__(self):
        return f"Configtuner Class path is at {self.cfg_path}"