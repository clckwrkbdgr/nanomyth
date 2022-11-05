import pygame
from ...math import Point

class ImageWidget:
	def __init__(self, image, topleft):
		self.topleft = Point(topleft)
		self.image = image
	def draw(self, engine):
		engine.render_texture(self.image.get_texture(), self.topleft)
