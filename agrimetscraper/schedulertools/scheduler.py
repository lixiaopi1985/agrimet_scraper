import crontab


class Scheduler:

	def __init__(self, cwd, pypath, file2run):

		self._crontab = crontab.CronTab(user=True)
		self.pypath = pypath
		self.cwd = cwd
		self.file2run = file2run
		self.job = None

	def Addjob(self, *args):

		change_dir = "cd {}".format(self.cwd)

		if len(args) > 0:
			self.job = self._crontab.new(
				command = '{} && {} {} {}'.format(change_dir, self.pypath, self.file2run, args[0])
			)
		else:
    			self.job = self._crontab.new(
				command = '{} && {} {}'.format(change_dir, self.pypath, self.file2run)
			)
    			
		return self

	def SetJob(self,**kwargs):

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







