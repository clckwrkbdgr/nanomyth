from contextlib import contextmanager
import pygame
from ...math import Size
from . import context

class SDLEngine:
	"""
	SDL-based game engine.

	Operates on set of Context objects.
	Uses the topmost (the latest) Context object to process events and draw.
	"""
	def __init__(self, size, initial_context, scale=1, window_title=None):
		""" Creates SDL engine with a viewport of given size (required) and pixel scale factor (defaults to 1).
		Another required argument is the initial game Context.
		Optional window title may be set.
		"""
		self.scale = scale
		pygame.init()
		pygame.display.set_mode(tuple(size))
		pygame.display.set_caption(window_title or '')
		self.window = pygame.display.get_surface()
		self.contexts = [initial_context]
		self.running = False
		self.images = {}
	def add_image(self, name, image):
		""" Puts image under specified name in the global image list. """
		self.images[name] = image
		return image
	def get_image(self, name):
		""" Returns image by name. """
		return self.images[name]
	@contextmanager
	def _enter_rendering_mode(self):
		""" RAII that enters into SDL rendring mode till the end of scope. """
		try:
			pygame.display.get_surface().fill((0,0,0))
			yield
		finally:
			pygame.display.flip()
	def render_texture(self, texture, pos):
		""" Renders SDL texture at given screen pos
		considering scale factor (for both positions and sizes).
		"""
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
		""" Main event loop.
		Processes events and controls for the current context and draws its widgets.
		Also handles switching contexts.
		When the last context quits, the whole event loop stops.
		"""
		self.running = True
		while self.running:
			current_context = self.contexts[-1]
			with self._enter_rendering_mode():
				current_context.draw(self)

			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					try:
						new_context = current_context.update(pygame.key.name(event.key))
						if new_context:
							self.contexts.append(new_context)
					except context.Context.Finished:
						self.contexts.pop()
						if not self.contexts:
							self.running = False
				elif event.type == pygame.QUIT:
					self.running = False
