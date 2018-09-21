# https://docs.djangoproject.com/en/2.1/ref/models/fields/#integerfield
MIN_INTEGER = -2147483648 
MAX_INTEGER = 2147483647 

# https://docs.djangoproject.com/en/2.1/ref/models/fields/#positiveintegerfield
MIN_POSITIVE_INTEGER = 0
MAX_POSITIVE_INTEGER = 2147483647 

SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}
def ordinal(num):
	if 10 <= num % 100 <= 20:
		suffix = 'th'
	else:
		# the second parameter is a default.
		suffix = SUFFIXES.get(num % 10, 'th')
	return str(num) + suffix

# note: currency(money) rounds when it shouldnt. expected $839.19 when it is $839.20 for final pia
def currency(num):
	return "${:,.2f}".format(num)

def percentage(num, places=2):
	return "{number:.{places}%}".format(number=num, places=places)