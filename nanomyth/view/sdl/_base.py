import os
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
	def make_unique_image_name(self, abs_image_path):
		""" Tries to create unique short name for image path (should be abs path). """
		path_name = os.path.splitext(abs_image_path)[0]
		path_parts = []
		while path_name:
			path_name, dirname = os.path.split(path_name)
			if dirname:
				path_parts.append(dirname)
			else:
				path_parts.append(path_name)
				path_name = ''
		path_parts.reverse()

		image_name = path_parts[-1]
		path_parts.pop()
		while path_parts and image_name in self.images:
			image_name = path_parts[-1] + '_' + image_name
			path_parts.pop()
		if image_name in self.images:
			return abs_image_path # Fallback to the full name.
		return image_name
	def get_image(self, name):
		""" Returns image by name. """
		return self.images[name]
	def find_image_name_by_path(self, abs_filename):
		""" Returns image name by file name (should abs path). """
		for image_name in self.images:
			image = self.images[image_name]
			if hasattr(image, 'filename') and image.filename == abs_filename:
				return image_name
		return None
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
	def run(self, custom_update=None):
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
				elif event.type == pygame.QUIT: # pragma: no cover
					self.running = False
			if custom_update:
				custom_update()
