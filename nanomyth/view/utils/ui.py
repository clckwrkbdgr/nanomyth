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
		If item_height is callable, it should take item index as argument and return its height.
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
	def set_total_items(self, new_value, item_height=None):
		""" Changes number of items.
		May update visible range and/or current item.
		Optional item_height for new sequence can be given.
		"""
		self.item_count = new_value
		self.set_top_item(self.current_pos)
		if item_height:
			self.item_height = item_height
	def number_of_visible_items(self, custom_current_pos=None):
		""" Returns number of items that fit into viewport.
		"""
		if not callable(self.item_height):
			return min(self.height // self.item_height, self.item_count)
		result = 0
		total_height = 0
		current_pos = custom_current_pos or self.current_pos
		item_range = range(current_pos, self.item_count)
		if current_pos < 0:
			current_pos = -current_pos
			item_range = reversed(range(0, current_pos + 1))
		for item_index in item_range:
			item_height = self.item_height(item_index)
			if total_height + item_height > self.height:
				break
			total_height += item_height
			result += 1
		return result
	def get_top_item(self):
		""" Returns the topmost visible item. """
		return self.current_pos
	def get_visible_slice(self):
		""" Returns slice object of items that fit into viewport.
		"""
		return slice(self.current_pos, self.current_pos + self.number_of_visible_items())
	def get_visible_range(self):
		""" Returns range object of items that fit into viewport.
		"""
		return range(self.current_pos, self.current_pos + self.number_of_visible_items())
	def set_top_item(self, item_pos):
		""" Tries to set new topmost visible item.
		Rearranges actual position so that all items are fit into the viewport window.
		"""
		item_pos = max(0, item_pos)
		item_pos = min(item_pos, self.item_count - self.number_of_visible_items())
		self.current_pos = item_pos
	def ensure_item_visible(self, item_pos):
		""" Re-arranges range of visible items to make specified one visible.
		"""
		if item_pos < self.current_pos:
			self.current_pos = item_pos
		elif item_pos >= self.current_pos + self.number_of_visible_items():
			self.current_pos = item_pos - self.number_of_visible_items(custom_current_pos=-item_pos)
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

class SelectionList:
	""" Item list with option to set selected item.
	"""
	def __init__(self, items=None, on_selection=None):
		""" Creates list from given items.
		If on_selection is given, it should be callable of two parameters (item, is_selected),
		which shall be triggered for each de-selected item (is_selected=False)
		and selected item (is_selected=True).
		"""
		self.items = list(items or [])
		self.selected = None
		self.on_selection = on_selection
	def __len__(self):
		return len(self.items)
	def __iter__(self):
		return iter(self.items)
	def __getitem__(self, item_index):
		return self.items[item_index]
	def append(self, new_item):
		self.items.append(new_item)
	def select(self, item_index):
		""" Selects item with given index,
		or clears selection when None.
		If on_selection callable was supplied, calls for de-selected item
		and for selected one.
		"""
		if self.selected is not None:
			if self.on_selection:
				self.on_selection(self.items[self.selected], False)
		self.selected = item_index
		if self.selected is not None:
			if self.on_selection:
				self.on_selection(self.items[self.selected], True)
	def select_prev(self):
		""" Selects previous item if possible. """
		self.select(self.get_prev_selected_index())
	def select_next(self):
		""" Selects next item if possible. """
		self.select(self.get_next_selected_index())
	def has_selection(self):
		""" Returns True if some item is selected. """
		return self.selected is not None
	def get_selected_index(self):
		""" Returns index of selected item or None. """
		return self.selected
	def get_next_selected_index(self):
		""" Returns index of the item that follows the selected one.
		If current item is the last one, returns it's index again.
		"""
		if not self.items:
			return None
		if self.selected is None:
			return 0
		return min(len(self.items) - 1, self.selected + 1)
	def get_prev_selected_index(self):
		""" Returns index of the item that is followed by the selected one.
		If current item is the first one, returns it's index again.
		"""
		if not self.items:
			return None
		if self.selected is None:
			return len(self.items) - 1
		return max(0, self.selected - 1)
	def get_selected_item(self):
		""" Returns value of the selected item. """
		return self.items[self.selected]
