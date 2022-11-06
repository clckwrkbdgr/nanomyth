import pygame
from ...math import Point

class ImageWidget:
	def __init__(self, image, topleft):
		self.topleft = Point(topleft)
		self.image = image
	def draw(self, engine):
		image = self.image
		if isinstance(self.image, str):
			image = engine.get_image(self.image)
		engine.render_texture(image.get_texture(), self.topleft)
