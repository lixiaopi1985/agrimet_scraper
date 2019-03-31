import requests
import os
import sys



class Validator:


	@staticmethod
	def url_validator(url):

		try:
			response = requests.get(url)
			response.raise_for_status()
		except requests.exceptions.HTTPError as errh:
			print('Http Error in Url Validation: {}'.format(errh))
		except requests.exceptions.ConnectionError as errc:
			print('Connection Error in Url Validation: {}'.format(errc))
		except requests.exceptions.Timeout as errt:
			print('Timeout Error in Url Validation: {}'.format(errt))
		except requests.exceptions.RequestException as err:
			print('Unknown Error in Url Validation: {}'.format(err))
			sys.exit(1)

		return True

	@staticmethod
	def path_checker(path):
		if not os.path.exists(path):
			raise os.error('No such path in current directory')
			sys.exit(1)
