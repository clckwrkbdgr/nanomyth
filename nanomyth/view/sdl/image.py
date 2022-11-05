import pygame

class Image:
	def __init__(self, filename):
		self._data = pygame.image.load(str(filename))
