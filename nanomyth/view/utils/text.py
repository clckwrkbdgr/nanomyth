class TextWrapper:
	def __init__(self, text, width):
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
		raise NotImplementedError()
