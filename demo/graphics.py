import os
from pathlib import Path

def download_resource(url, dest_dir_name, dest_filename): # pragma: no cover -- resources are downloaded and unpack any way at the first run.
	""" Downloads free resource to use in demo.
	Returns root directory of the unpacked resource.
	"""
	dest_root_dir = os.path.join(os.path.dirname(__file__), dest_dir_name)
	if not os.path.exists(dest_root_dir):
		os.makedirs(dest_root_dir)
	zip_file = os.path.join(dest_root_dir, dest_filename)
	if not os.path.exists(zip_file):
		print('Downloading {0} resource...'.format(dest_dir_name))
		import urllib.request
		response = urllib.request.urlopen(url)
		with open(zip_file, 'wb') as f:
			f.write(response.read())
	if os.listdir(dest_root_dir) == [dest_filename]: # Not unpacked.
		print('Unpacking {0} resource...'.format(dest_dir_name))
		import zipfile
		with zipfile.ZipFile(zip_file) as archive:
			archive.extractall(path=dest_root_dir)
	return dest_root_dir

def download_resources():
	# Original page: <https://opengameart.org/content/dawnlike-16x16-universal-rogue-like-tileset-v181>
	tileset = download_resource('https://opengameart.org/sites/default/files/DawnLike_5.zip', 'DawnLike', 'DawnLike.zip')
	# Original page: <https://opengameart.org/content/8x8-font>
	font = download_resource('https://opengameart.org/sites/default/files/8x8Text.zip', '8x8Text', '8x8Text.zip')
	# Original page: <https://opengameart.org/content/6-adventure-game-backgrounds>
	background = download_resource('https://opengameart.org/sites/default/files/5DragonsBkgds.zip', '5DragonsBkgds', '5DragonsBkgds.zip')
	return dict(
			tileset=Path(tileset),
			font=Path(font),
			background=Path(background),
			)
