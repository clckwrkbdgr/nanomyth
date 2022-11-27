from ...math import Size, Matrix

def tiled_panel(tilemap, size):
	""" Fills matrix of tiles using tiles from given mapping.
	Tilemap should be a Matrix of 3x3 that covers every possible part:
	+ - + : Top-left and top-right corners, and plain top tile.
	| . | : Left and right tiles, plus middle/center tile that fills the insides.
	+ _ + : Bottom-left and bottom-right corners, and plain bottom tile.

	Size must be >= 2x2 so at least corners will be used.
	If passed size is less, it is automatically adjusted so it will be no less than 2x2.

	Returns created matrix.
	"""
	assert tilemap.size == Size(3, 3)
	size = Size(size)
	size = Size(max(size.width, 2), max(size.height, 2))
	panel_tiles = []
	for row_index in range(size.height):
		tilemap_y = 0 if row_index == 0 else (2 if row_index == size.height - 1 else 1)
		panel_tiles.append([tilemap.cell((0 if col_index == 0 else (2 if col_index == size.width - 1 else 1), tilemap_y))
			for col_index in range(size.width)
			])
	panel_tiles = Matrix.from_iterable(panel_tiles)
	return panel_tiles
