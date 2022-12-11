from ...math import Rect, Point

def get_bounding_rect(original_rect, is_pixel_background, space_width=1):
	""" Returns bounding rect for the part of an image.
	Crops background stripes on left and right sides, leaving vertical positions intact.
	Pixel color is checked using is_pixel_background(Point),
	which should return True is specified pixel has background color (is "empty").
	In case when there are no non-background pixels found in given rect,
	it will be squeezed down to space_width.
	"""
	actual_left = None
	for x in range(original_rect.left, original_rect.right + 1):
		all_transparent = all(is_pixel_background(Point(x, y)) for y in range(original_rect.top, original_rect.bottom + 1))
		if not all_transparent:
			actual_left = x
			break
	actual_right = None
	for x in reversed(range(original_rect.left, original_rect.right + 1)):
		all_transparent = all(is_pixel_background(Point(x, y)) for y in range(original_rect.top, original_rect.bottom + 1))
		if not all_transparent:
			actual_right = x
			break
	if actual_left is None or actual_right is None:
		actual_left = original_rect.left
		actual_right = original_rect.left + (space_width or original_rect.width) - 1
	return Rect((actual_left, original_rect.top), (actual_right - actual_left + 1, original_rect.height))
