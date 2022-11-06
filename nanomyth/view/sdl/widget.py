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

class TileMapWidget:
	def __init__(self, tilemap, topleft):
		self.topleft = Point(topleft)
		self.tilemap = tilemap
	def draw(self, engine):
		for pos in self.tilemap:
			image = engine.get_image(self.tilemap.cell(pos))
			tile_size = image.get_size()
			image_pos = Point(pos.x * tile_size.width, pos.y * tile_size.height)
			engine.render_texture(image.get_texture(), self.topleft + image_pos)

class LevelMapWidget:
	def __init__(self, level_map, topleft):
		self.topleft = Point(topleft)
		self.level_map = level_map
	def draw(self, engine):
		for pos, tile in self.level_map.iter_tiles():
			for image_name in tile.get_images():
				image = engine.get_image(image_name)
				tile_size = image.get_size()
				image_pos = Point(pos.x * tile_size.width, pos.y * tile_size.height)
				engine.render_texture(image.get_texture(), self.topleft + image_pos)
