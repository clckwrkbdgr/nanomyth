import pygame
from contextlib import contextmanager

class SDLEngine:
	def __init__(self, size, window_title=None):
		pygame.init()
		pygame.display.set_mode(tuple(size))
		pygame.display.set_caption(window_title or '')
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
			window = pygame.display.get_surface()
			with self._enter_rendering_mode():
				for widget in self.widgets:
					widget.draw(window)
