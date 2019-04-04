"""
this module used to provide basic converstions
"""


def StringToList(string, sep = ','):
	return string.split(sep)


def TemperatureConverter(temperature, direction=1):
	"""
	direction 1: from fahrenheit to celsius
	direction 2: from celsius to fahrenheit
	"""


	temp = float(temperature)

	if direction == 1:
		print("Convert Fahrenheit to Celsius")
		result = (temp - 32)*5/9

	elif direction == 2:
		print("COnvert Celsius to Fahrenheit")
		result = 9*temp/5 + 32

	else:
		raise ValueError('Direction is type of integer in 1 or 2')

	return round(result, 1)




def LengthConverter(num, formats = "inch2mm"):
	"""
	Convert length

	inch2mm: inch to mm
	inch2cm: inch to cm
	mm2inch: mm to inch
	cm2inch: cm to inch
	cm2mm: cm to mm
	mm2cm: mm to cm
	"""

	num = float(num)

	if formats == "inch2mm":
		out = num*25.4
	elif formats == "inch2cm":
		out = num*2.54
	elif formats == "mm2inch":
		out = num/25.4
	elif formats == "cm2inch":
		out = num/2.54
	elif formats == "cm2mm":
		out = num*10
	elif formats == "mm2cm":
		out = num/10

	return round(out, 2)


