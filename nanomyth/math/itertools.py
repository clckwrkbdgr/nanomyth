from collections import OrderedDict

def stack_similar(seq, key=None):
	""" Iterates over sequence stacking similar items.
	Yields pair (item, count).
	Items come in order they first went in,
	i.e. first item in sequence "collects" all similar others.
	Similarity is checked using key() function.
	Result of key() should be hashable.
	Default key is hash().
	"""
	key = key or hash
	stack = OrderedDict()
	for item in seq:
		value = key(item)
		if value in stack:
			stack[value][1] += 1
		else:
			stack[value] = [item, 1]
	for _, (item, count) in stack.items():
		yield item, count
