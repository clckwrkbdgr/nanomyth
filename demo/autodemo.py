import pygame
import time
import itertools
from pathlib import Path

class AutoSequence:
	def __init__(self, delay_sec, sequence_file):
		self.delay = delay_sec

		sequence_file = Path(sequence_file)
		keypresses = list(itertools.chain.from_iterable(
				map(str.split, # Split lines into keypresses
					filter(None, # Remove empty lines.
						map(str.strip, # Strip spaces.
							(
								line.split('#', 1)[0] # Strip comments.
								for line in sequence_file.read_text().splitlines()
								)
							)
						)
					)
				))

		self.keypresses = keypresses
		self.last_event = time.time()
	def __call__(self):
		if not self.keypresses:
			return
		current_time = time.time()
		if current_time < self.last_event + self.delay:
			return

		key = pygame.key.key_code(self.keypresses[0])
		pygame.time.set_timer(
				pygame.event.Event(pygame.KEYDOWN, key=key),
				10, loops=1)
		pygame.time.set_timer(
				pygame.event.Event(pygame.KEYUP, key=key),
				20, loops=1)

		self.keypresses.pop(0)
		self.last_event = current_time
