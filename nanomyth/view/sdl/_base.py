import pygame

class SDLEngine:
	def __init__(self, size, window_title=None):
		pygame.init()
		pygame.display.set_mode(tuple(size))
		pygame.display.set_caption(window_title or '')

		self.running = False
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
