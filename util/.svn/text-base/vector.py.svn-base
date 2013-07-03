#!/usr/bin/env python
# 
# A python Vector class
# A. Pletzer 5 Jan 00/11 April 2002
#
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52272

import math
import random

"""
A list based Vector class that supports elementwise mathematical operations

In this version, the Vector call inherits from list; this 
requires Python 2.2 or later.
"""

class Vector(list):
	"""
		A list based Vector class
	"""

	# Cartesian coordinates
	#x = r * cos(theta) * cos(phi)
	#y = r * cos(theta) * sin(phi)
	#z = r * sin(theta)
	
	# Spherical coordinates
	#r = sqrt(x*x + y*y + z*z) = norm([x, y, z])
	#theta = asin(z/r)		-pi/2 <= theta <= pi/2
	#phi = acos(x / (r*cos(theta))) = asin(y / (r*cos(theta))) = atan(y/x)
	
	#pitch
	#yaw
	#roll
	
	#quaternion
	
	
	# Cartesian coordinates

	# x-coordinate
	def __get_x(self): return self[0]
	def __set_x(self, x): self[0] = x
	def __del_x(self): print '__del_x NOT SUPPORTED'
	x = property(__get_x, __set_x, __del_x, "x-coordinate")
	
	# y-coordinate
	def __get_y(self): return self[1]
	def __set_y(self, y): self[1] = y
	def __del_y(self): print '__del_y NOT SUPPORTED'
	y = property(__get_y, __set_y, __del_y, "y-coordinate")
	
	# z-coordinate
	def __get_z(self): return self[2]
	def __set_z(self, z): self[2] = z
	def __del_z(self): print '__del_z NOT SUPPORTED'
	z = property(__get_z, __set_z, __del_z, "z-coordinate")
	
	# Spherical coordinates

	# r-coordinate, distance from center
	def __get_r(self):
		return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
	def __set_r(self, r):
		x = r * math.cos(self.theta) * math.cos(self.phi)
		y = r * math.cos(self.theta) * math.sin(self.phi)
		z = r * math.sin(self.theta)
		self.x, self.y, self.z = x, y, z
	def __del_r(self): print '__del_r NOT SUPPORTED'
	r = property(__get_r, __set_r, __del_r, "r-coordinate")
	
	# theta-coordinate, angle from x-axis in x/y-plane, counterclockwise
	def __get_theta(self):
		if self.r == 0.0:
			return 0.0
		else:
			return math.asin(self.z/self.r)
	def __set_theta(self, theta):
		x = self.r * math.cos(theta) * math.cos(self.phi)
		y = self.r * math.cos(theta) * math.sin(self.phi)
		z = self.r * math.sin(theta)
		self.x, self.y, self.z = x, y, z
	def __del_theta(self): print '__del_theta NOT SUPPORTED'
	theta = property(__get_theta, __set_theta, __del_theta, "theta-coordinate")

	# phi-coordinate, angle from x/y-plane in z/r-plane
	def __get_phi(self):
		if self.r == 0.0:
			return 0.0
		else:
			return math.acos(self.x / (self.r * math.cos(self.theta)))
#		if self.x == 0.0:
#			return math.asin(self.y / (self.r*math.cos(self.theta)))
#		else:
#			return math.atan(self.y / self.x)
			#return math.acos(self.x / (self.r * math.cos(self.theta)))
	def __set_phi(self, phi):
		x = self.r * math.cos(self.theta) * math.cos(phi)
		y = self.r * math.cos(self.theta) * math.sin(phi)
		self.x, self.y = x, y
	def __del_phi(self): print '__del_phi NOT SUPPORTED'
	phi = property(__get_phi, __set_phi, __del_phi, "phi-coordinate")
	
#	============================================================

	def __getslice__(self, i, j):
		try:
			# use the list __getslice__ method and convert
			# result to Vector
			return Vector(super(Vector, self).__getslice__(i,j))
		except:
			raise TypeError, 'Vector::FAILURE in __getslice__'
		
	def __add__(self, other):
		return Vector(map(lambda x,y: x+y, self, other))

	def __neg__(self):
		return Vector(map(lambda x: -x, self))
	
	def __sub__(self, other):
		return Vector(map(lambda x,y: x-y, self, other))

	def __mul__(self, other):
		"""
		Element by element multiplication
		"""
		try:
			return Vector(map(lambda x,y: x*y, self, other))
		except:
			# other is a const
			return Vector(map(lambda x: x*other, self))


	def __rmul__(self, other):
		return (self*other)


	def __div__(self, other):
		"""
		Element by element division.
		"""
		try:
			return Vector(map(lambda x,y: x/y, self, other))
		except:
			return Vector(map(lambda x: x/other, self))

	def __rdiv__(self, other):
		"""
		The same as __div__
		"""
		try:
			return Vector(map(lambda x,y: x/y, other, self))
		except:
			# other is a const
			return Vector(map(lambda x: other/x, self))

	def size(self): return len(self)

	def conjugate(self):
		return Vector(map(lambda x: x.conjugate(), self))

		def ReIm(self):
			"""
			Return the real and imaginary parts
			"""
			return [
				Vector(map(lambda x: x.real, self)),
				Vector(map(lambda x: x.imag, self)),
			]
	
		def AbsArg(self):
			"""
			Return modulus and phase parts
			"""
			return [
				Vector(map(lambda x: abs(x), self)),
				Vector(map(lambda x: math.atan2(x.imag, x.real), self)),
			]


	def out(self):
		"""
		Prints out the Vector.
		"""
		print self

###############################################################################


def isVector(x):
	"""
	Determines if the argument is a Vector class object.
	"""
	return hasattr(x,'__class__') and x.__class__ is Vector

def zeros(n):
	"""
	Returns a zero Vector of length n.
	"""
	return Vector(map(lambda x: 0., range(n)))

def ones(n):
	"""
	Returns a Vector of length n with all ones.
	"""
	return Vector(map(lambda x: 1., range(n)))

def random(n, lmin=0.0, lmax=1.0):
	"""
	Returns a random Vector of length n.
	"""
	new = Vector([])
	return Vector(map(lambda x: random.uniform(lmin, lmax), range(n)))
	
def dot(a, b):
	"""
	dot product of two Vectors.
	"""
	try:
		return reduce(lambda x, y: x+y, a*b, 0.)
	except:
		raise TypeError, 'Vector::FAILURE in dot'
	

def norm(a):
	"""
	Computes the norm of Vector a.
	"""
	try:
		return math.sqrt(abs(dot(a,a)))
	except:
		raise TypeError, 'Vector::FAILURE in norm'

def sum(a):
	"""
	Returns the sum of the elements of a.
	"""
	try:
		return reduce(lambda x, y: x+y, a, 0)
	except:
		raise TypeError, 'Vector::FAILURE in sum'

# elementwise operations
	
def log10(a):
	"""
	log10 of each element of a.
	"""
	try:
		return Vector(map(math.log10, a))
	except:
		raise TypeError, 'Vector::FAILURE in log10'

def log(a):
	"""
	log of each element of a.
	"""
	try:
		return Vector(map(math.log, a))
	except:
		raise TypeError, 'Vector::FAILURE in log'
		
def exp(a):
	"""
	Elementwise exponential.
	"""
	try:
		return Vector(map(math.exp, a))
	except:
		raise TypeError, 'Vector::FAILURE in exp'

def sin(a):
	"""
	Elementwise sine.
	"""
	try:
		return Vector(map(math.sin, a))
	except:
		raise TypeError, 'Vector::FAILURE in sin'
		
def tan(a):
	"""
	Elementwise tangent.
	"""
	try:
		return Vector(map(math.tan, a))
	except:
		raise TypeError, 'Vector::FAILURE in tan'
		
def cos(a):
	"""
	Elementwise cosine.
	"""
	try:
		return Vector(map(math.cos, a))
	except:
		raise TypeError, 'Vector::FAILURE in cos'

def asin(a):
	"""
	Elementwise inverse sine.
	"""
	try:
		return Vector(map(math.asin, a))
	except:
		raise TypeError, 'Vector::FAILURE in asin'

def atan(a):
	"""
	Elementwise inverse tangent.
	"""	
	try:
		return Vector(map(math.atan, a))
	except:
		raise TypeError, 'Vector::FAILURE in atan'

def acos(a):
	"""
	Elementwise inverse cosine.
	"""
	try:
		return Vector(map(math.acos, a))
	except:
		raise TypeError, 'Vector::FAILURE in acos'

def sqrt(a):
	"""
	Elementwise sqrt.
	"""
	try:
		return Vector(map(math.sqrt, a))
	except:
		raise TypeError, 'Vector::FAILURE in sqrt'

def sinh(a):
	"""
	Elementwise hyperbolic sine.
	"""
	try:
		return Vector(map(math.sinh, a))
	except:
		raise TypeError, 'Vector::FAILURE in sinh'

def tanh(a):
	"""
	Elementwise hyperbolic tangent.
	"""
	try:
		return Vector(map(math.tanh, a))
	except:
		raise TypeError, 'Vector::FAILURE in tanh'

def cosh(a):
	"""
	Elementwise hyperbolic cosine.
	"""
	try:
		return Vector(map(math.cosh, a))
	except:
		raise TypeError, 'Vector::FAILURE in cosh'


def pow(a,b):
	"""
	Takes the elements of a and raises them to the b-th power
	"""
	try:
		return Vector(map(lambda x: x**b, a))
	except:
		try:
			return Vector(map(lambda x,y: x**y, a, b))
		except:
			raise TypeError, 'Vector::FAILURE in pow'
	
def atan2(a,b):	
	"""
	Arc tangent
	
	"""
	try:
		return Vector(map(math.atan2, a, b))
	except:
		raise TypeError, 'Vector::FAILURE in atan2'

