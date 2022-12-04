class TextWrapper:
	""" Wraps text to fit into given width
	considering actual pixel size of each letter.
	"""
	def __init__(self, text, width):
		""" Creates wrapper object for given text and width
		and prepares fields:
		- .lines - ready text lines.
		- .total_height - total pixel height of all lines.
		"""
		self.lines = []
		self.total_height = 0
		for line in text.splitlines():
			line_width = []
			line_height = 0
			current_line = ''
			for letter in line:
				letter_size = self.get_letter_size(letter)
				letter_width = letter_size.width
				line_height = max(line_height, letter_size.height)
				if sum(line_width) + letter_width > width:
					last_space_pos = current_line.rfind(' ')
					last_space_pos = last_space_pos if last_space_pos > -1 else len(current_line)
					self.total_height += line_height
					line_height = 0
					self.lines.append(current_line[:last_space_pos].rstrip())
					current_line = current_line[last_space_pos+1:]
					line_width = line_width[last_space_pos+1:]
				current_line += letter
				line_width.append(letter_width)
			self.total_height += line_height
			self.lines.append(current_line)
	def get_letter_size(self, letter): # pragma: no cover
		""" Returns Size of the given letter.
		Should be overriden in custom implementations.
		"""
		raise NotImplementedError()

class Scroller:
	""" Utility class that control/tracks scrolling item list vertically.
	Does not operate on actual item list, requires just its size.
	"""
	def __init__(self, total_items, viewport_height, item_height):
		""" Create scrolling for given items of with specified height each
		by fitting them into given viewport.
		Starts with the first item as the current one.
		"""
		self.item_count = total_items
		self.current_pos = 0
		self.height = viewport_height
		self.item_height = item_height
	def set_height(self, new_height):
		""" Changes viewport height.
		May update visible range and/or current item.
		"""
		self.height = new_height
		self.set_top_item(self.current_pos)
	def set_total_items(self, new_value):
		""" Changes number of items.
		May update visible range and/or current item.
		"""
		self.item_count = new_value
		self.set_top_item(self.current_pos)
	def number_of_visible_items(self):
		""" Returns number of items that fit into viewport.
		"""
		return min(self.height // self.item_height, self.item_count)
	def get_top_item(self):
		""" Returns the topmost visible item. """
		return self.current_pos
	def get_visible_range(self):
		""" Returns slice object of items that fit into viewport.
		"""
		return slice(self.current_pos, self.current_pos + self.number_of_visible_items())
	def set_top_item(self, item_pos):
		""" Tries to set new topmost visible item.
		Rearranges actual position so that all items are fit into the viewport window.
		"""
		item_pos = max(0, item_pos)
		item_pos = min(item_pos, self.item_count - self.number_of_visible_items())
		self.current_pos = item_pos
	def can_scroll_up(self):
		""" Returns True if there are items higher than current viewport can display
		and it can be scrolled up.
		"""
		return self.current_pos > 0
	def can_scroll_down(self):
		""" Returns True if there are items lower than current viewport can display
		and it can be scrolled down.
		"""
		return self.current_pos + self.number_of_visible_items() < self.item_count
