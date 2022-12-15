def create_unique_name(filepath, existing_names):
	""" Tries to make unique name from given Path objects
	so it would not conflict with existing names.
	Path is not required to be absolute but it is encouraged.
	"""
	path_parts = list(filepath.parent.parts) + [filepath.stem]
	name = path_parts[-1]
	path_parts.pop()
	while path_parts and name in existing_names:
		name = path_parts[-1] + '_' + name
		path_parts.pop()
	if name in existing_names:
		return str(filepath)
	return name
