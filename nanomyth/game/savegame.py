""" Saving/loading game state.
"""
from pathlib import Path

class Savefile:
	""" Abstract savefile class.
	"""
	def __init__(self, filename):
		""" Savefile always operates on a real file.
		"""
		self.filename = Path(filename)
	def save(self, world): # pragma: no cover
		""" Override this to store world in the file. """
		raise NotImplementedError
	def load(self): # pragma: no cover
		""" Override this to load world from the filename. """
		raise NotImplementedError

class PickleSavefile(Savefile):
	""" Serializing using Python built-in pickle module.
	Offers small files at the cost at being platform-dependent and binary format.
	"""
	def save(self, world):
		import pickle
		savedata = pickle.dumps(world)
		self.filename.write_bytes(savedata)
	def load(self):
		if not self.filename.exists():
			return None
		import pickle
		savedata = self.filename.read_bytes()
		return pickle.loads(savedata)

class JsonpickleSavefile(Savefile):
	""" Serializing using jsonpickle module.
	Offers cross-platform format and readability of the resulting data at the cost of file size.
	"""
	def save(self, world):
		import json, jsonpickle
		savedata = jsonpickle.encode(world, keys=True, make_refs=False)
		self.filename.write_text(json.dumps(json.loads(savedata), indent=1, sort_keys=True))
	def load(self):
		if not self.filename.exists():
			return None
		import json, jsonpickle
		savedata = self.filename.read_text()
		return jsonpickle.decode(savedata, keys=True)
