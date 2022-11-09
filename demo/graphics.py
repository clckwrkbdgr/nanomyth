import os
from pathlib import Path

DEMO_ROOTDIR = Path(__file__).parent

def download_resource(url, dest_dir_name, dest_filename): # pragma: no cover -- resources are downloaded and unpack any way at the first run.
	""" Downloads free resource to use in demo.
	Returns root directory of the unpacked resource.
	"""
	dest_root_dir = DEMO_ROOTDIR/dest_dir_name
	dest_root_dir.mkdir(parents=True, exist_ok=True)
	zip_file = dest_root_dir/dest_filename
	if not zip_file.exists():
		print('Downloading {0} resource...'.format(dest_dir_name))
		import urllib.request
		response = urllib.request.urlopen(url)
		zip_file.write_bytes(response.read())
	if [_.name for _ in dest_root_dir.iterdir()] == [dest_filename]: # Not unpacked.
		print('Unpacking {0} resource...'.format(dest_dir_name))
		import zipfile
		with zipfile.ZipFile(zip_file) as archive:
			archive.extractall(path=str(dest_root_dir))
	return dest_root_dir

def download_resources():
	# Original page: <https://opengameart.org/content/dawnlike-16x16-universal-rogue-like-tileset-v181>
	tileset = download_resource('https://opengameart.org/sites/default/files/DawnLike_5.zip', 'DawnLike', 'DawnLike.zip')
	# Original page: <https://opengameart.org/content/8x8-font>
	font = download_resource('https://opengameart.org/sites/default/files/8x8Text.zip', '8x8Text', '8x8Text.zip')
	# Original page: <https://opengameart.org/content/6-adventure-game-backgrounds>
	background = download_resource('https://opengameart.org/sites/default/files/5DragonsBkgds.zip', '5DragonsBkgds', '5DragonsBkgds.zip')
	return dict(
			tileset=tileset,
			font=font,
			background=background,
			)
