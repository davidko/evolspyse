import time
# use as: from spyse.util.simulation import SimTime as time

class SimTime(object):
	__start = 0
	__scale = 1
	def __init__(self, scale):
		self.reset()
		self.setScale(scale)

	def setScale(self, scale):
		self.__scale = scale

	def reset(self):
		self.__start = time.time()

	def time(self):
		t = time.time()
		dt = (t - self.__start)
		return self.__start + dt * self.__scale

