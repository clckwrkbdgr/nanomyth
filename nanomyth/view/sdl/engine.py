import os
from contextlib import contextmanager
from pathlib import Path
import pygame
from ...math import Size, Point
from . import context
from .image import BaseImage
from ..utils import fs
from ...utils.meta import typed
from ._base import Engine

class SDLEngine(Engine):
	"""
	SDL-based game engine.

	Operates on set of Context objects.
	Uses the topmost (the latest) Context object to process events and draw.
	"""
	@typed((Size, tuple, list), scale=int, window_title=(str, None))
	def __init__(self, size, scale=1, window_title=None):
		""" Creates SDL engine with a viewport of given size (required) and pixel scale factor (defaults to 1).
		Optional window title may be set.
		"""
		self._scale = scale
		pygame.init()
		pygame.display.set_mode(tuple(size))
		pygame.display.set_caption(window_title or '')
		self._window = pygame.display.get_surface()
		self._contexts = []
		self._images = {}
	@typed(context.Context)
	def init_context(self, context):
		""" (Re-)Initializes current context.
		Replaces all current contexts in the stack if were present.
		By default engine is constructed with empty context stack and will immediately exit when run.
		"""
		self._contexts = [context]
	def get_window_size(self):
		""" Returns window size (unscaled). """
		return Size(
			self._window.get_width() // self._scale,
			self._window.get_height() // self._scale,
			)
	@typed(str, BaseImage)
	def add_image(self, name, image):
		""" Puts image under specified name in the global image list. """
		self._images[name] = image
		return image
	@typed((Path, str))
	def make_unique_image_name(self, image_path):
		""" Tries to create unique short name for image path. """
		image_path = Path(image_path).resolve()
		return fs.create_unique_name(image_path, self._images)
	@typed(str)
	def get_image(self, name):
		""" Returns image by name. """
		return self._images[name]
	@typed((Path, str))
	def find_image_name_by_path(self, filename):
		""" Returns image name by file name. """
		filename = Path(filename).resolve()
		for image_name in self._images:
			image = self._images[image_name]
			if hasattr(image, 'filename') and image.filename == filename:
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
	@typed(pygame.Surface, Point)
	def render_texture(self, texture, pos):
		""" Renders SDL texture at given screen pos
		considering scale factor (for both positions and sizes).
		"""
		dest_size = Size(
				texture.get_width() * self._scale,
				texture.get_height() * self._scale,
				)
		dest = pygame.Rect(
				pos.x * self._scale,
				pos.y * self._scale,
				dest_size.width,
				dest_size.height,
				)
		texture = pygame.transform.scale(texture, tuple(dest_size))
		self._window.blit(texture, dest)
	def run(self, custom_update=None): # TODO callable type.
		""" Main event loop.
		Processes events and controls for the current context and draws its widgets.
		Also for transparent contexts draws all contexts under it until non-transparent is found.
		Handles switching contexts.
		When the last context quits, the whole event loop stops.
		"""
		while self._contexts:
			contexts_to_draw = []
			for c in reversed(self._contexts):
				contexts_to_draw.append(c)
				if not c.transparent:
					break
			contexts_to_draw = reversed(contexts_to_draw)
			with self._enter_rendering_mode():
				for c in contexts_to_draw:
					c.draw(self)

			current_context = self._contexts[-1]
			if current_context._pending_context: # TODO see comment for Context.set_pending_context
				self._contexts.append(current_context._pending_context)
				current_context._pending_context = None
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					try:
						new_context = current_context.update(pygame.key.name(event.key))
						if new_context:
							self._contexts.append(new_context)
					except context.Context.Finished:
						self._contexts.pop()
				elif event.type == pygame.QUIT: # pragma: no cover
					self._contexts.clear()
			if custom_update:
				custom_update()
