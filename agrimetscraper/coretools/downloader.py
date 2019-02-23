import requests
from agrimetscraper.utils.converters import StringToList
from agrimetscraper.utils.validations import Validator


class Downloader:

	def __init__(self, url):
		self.url = url

	@classmethod
	def  download(cls, url):


		Validator.url_validator(url)

		response = requests.get(url)

		text_r = response.text.strip()

		data_string = StringToList(text_r, '\n')[1:]
		description = StringToList(text_r, '\n')[0]

		return data_string, description



