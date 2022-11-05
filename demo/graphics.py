import os

def download_dawnlike_tileset():
	""" Downloads free tileset to use in demo.

	Original page: <https://opengameart.org/content/dawnlike-16x16-universal-rogue-like-tileset-v181>
	"""
	url = 'https://opengameart.org/sites/default/files/DawnLike_5.zip'
	dawnlike_root = os.path.join(os.path.dirname(__file__), 'DawnLike')
	if not os.path.exists(dawnlike_root):
		os.makedirs(dawnlike_root)
	zip_file = os.path.join(dawnlike_root, 'DawnLike.zip')
	if not os.path.exists(zip_file):
		print('Downloading DawnLike tileset...')
		import urllib.request
		response = urllib.request.urlopen(url)
		with open(zip_file, 'wb') as f:
			f.write(response.read())
	if os.listdir(dawnlike_root) == ['DawnLike.zip']: # Not unpacked.
		print('Unpacking DawnLike tileset...')
		import zipfile
		with zipfile.ZipFile(zip_file) as archive:
			archive.extractall(path=dawnlike_root)
