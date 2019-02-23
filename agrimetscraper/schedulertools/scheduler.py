import crontab
from agrimetscraper.utils.decorators import scheduler_decorator

class Scheduler:

	def __init__(self, cwd, pypath, file2run, cfg_path):

		self._crontab = crontab.CronTab(user=True)
		self.cfg_path = cfg_path
		self.job = None

	def Addjob(self):

		change_dir = "cd {}".format(self.cwd)

		self.job = self._crontab.new(
			command = '{} && {} {}'.format(change_dir, self.pypath, self.file2run)
		)


		return self

	@scheduler_decorator(self.cfg_path)
	def SetJob(self, **kwargs):

		if all( k in kwargs for k in ('min','hour', 'dom', 'mon', 'dow')):

			minute =kwargs['min']
			hour = kwargs['hour']
			dom = kwargs['dom']
			mon = kwargs['mon']
			dow = kwargs['dow']

		else:
			raise ValueError('key argument does not have all the keys')


		self.job.setall(minute, hour, dom, mon, dow)
		self._crontab.write()







