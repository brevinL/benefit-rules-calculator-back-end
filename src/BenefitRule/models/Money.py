from math import floor
from django.db import models
from .Utilities import currency
from decimal import Decimal

class Money(models.Model):
	amount = models.DecimalField(max_digits=11, decimal_places=2)

	def __add__(self, other):
		if type(other) == int:
			return Money(amount=self.amount + other)
		elif type(other) == float:
			return Money(amount=Decimal(float(self.amount) + other))
		else:
			return Money(amount=(self.amount + other.amount))

	def __radd__(self, other):
		return Money.__add__(self, other)

	def __sub__(self, other):
		if type(other) == int:
			return Money(amount=self.amount - other)
		elif type(other) == float:
			return Money(amount=Decimal(float(self.amount) - other))
		else:
			return Money(amount=(self.amount - other.amount))

	def __rsub__(self, other):
		if type(self.amount) == float:
			return Money(amount=Decimal(other - float(self.amount)))
		else:
			return Money(amount=other - self.amount)

	def __mul__(self, other):
		if type(other) == int:
			return Money(amount=self.amount * other)
		elif type(other) == float:
			return Money(amount=Decimal(float(self.amount) * other))
		else:
			return Money(amount=(self.amount * other.amount))

	def __rmul__(self, other):
		return Money.__mul__(self, other)

	def __truediv__(self, other):
		if type(other) == int:
			return Money(amount=self.amount / other)
		elif type(other) == float:
			return Money(amount=Decimal(float(self.amount) / other))
		else:
			return Money(amount=(self.amount / other.amount))

	def __rtruediv__(self, other):
		if type(self.amount) == float:
			return Money(amount=Decimal(other / float(self.amount)))
		else:
			return Money(amount=other / self.amount)

	def __gt__(self, other):
		if type(other) == int or type(other) == float:
			return self.amount > other
		else:
			return self.amount > other.amount

	def __lt__(self, other):
		if type(other) == int or type(other) == float:
			return self.amount < other
		else:
			return self.amount < other.amount

	def __ge__(self, other):
		if type(other) == int or type(other) == float:
			return self.amount >= other
		else:
			return self.amount >= other.amount

	def __le__(self, other):
		if type(other) == int or type(other) == float:
			return self.amount <= other
		else:
			return self.amount <= other.amount

	def __eq__(self, other):
		if type(other) == int or type(other) == float:
			return self.amount == other
		else:
			return self.amount == other.amount

	def __ne__(self, other):
		if type(other) == int or type(other) == float:
			return self.amount != other
		else:
			return self.amount != other.amount

	def __floor__(self):
		if type(self.amount) == int:
			return Money(amount=Decimal(self.amount).quantize(Decimal('1')))
		return Money(amount=self.amount.quantize(Decimal('1')))

	def __abs__(self):
		return abs(self.amount)
		
	def __repr__(self):
		return currency(self.amount)

	def __format__(self, format_spec):
		return currency(self.amount)

	def __str__(self):
		return currency(self.amount)