from contextlib import contextmanager
import pygame
from ...math import Size

class SDLEngine:
	def __init__(self, size, scale=1, window_title=None):
		self.scale = scale
		pygame.init()
		pygame.display.set_mode(tuple(size))
		pygame.display.set_caption(window_title or '')
		self.window = pygame.display.get_surface()
		self.widgets = []
		self.running = False
	@contextmanager
	def _enter_rendering_mode(self):
		""" RAII that enters into SDL rendring mode till the end of scope. """
		try:
			pygame.display.get_surface().fill((0,0,0))
			yield
		finally:
			pygame.display.flip()
	def render_texture(self, texture, pos):
		dest_size = Size(
				texture.get_width() * self.scale,
				texture.get_height() * self.scale,
				)
		dest = pygame.Rect(
				pos.x * self.scale,
				pos.y * self.scale,
				dest_size.width,
				dest_size.height,
				)
		texture = pygame.transform.scale(texture, tuple(dest_size))
		self.window.blit(texture, dest)
	def run(self):
		self.running = True
		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					key_name = pygame.key.name(event.key)
					if key_name == 'escape':
						self.running = False
				elif event.type == pygame.QUIT:
					self.running = False
			with self._enter_rendering_mode():
				for widget in self.widgets:
					widget.draw(self)
