""" Utilities for TMX (Tiled editor) maps.
"""
import os
from collections import defaultdict
from pathlib import Path
import pytmx
from ...math import Matrix, Point, Size
from ...game.map import Map, Terrain, Portal
from .image import TileSetImage

def _load_tmx_image_tile(image, engine, tileset_sizes):
	""" Parses TMX image [tile] definition
	and adds image to the engine (loading any tileset if needed).
	Returns image name for this specific tile.
	"""
	tileset_filename, tile_pos, _flags = image
	tileset_filename = Path(tileset_filename)
	tile_pos = Point(
			tile_pos[0] // tile_pos[2],
			tile_pos[1] // tile_pos[3],
			)

	tileset_name = engine.find_image_name_by_path(tileset_filename)
	if not tileset_name:
		tileset_name = engine.make_unique_image_name(tileset_filename)
		tileset_size = tileset_sizes[tileset_filename]
		engine.add_image(tileset_name, TileSetImage(tileset_filename, tileset_size))

	tile_name = '{0}_{1}_{2}'.format(tileset_name, tile_pos.x, tile_pos.y)
	engine.add_image(tile_name, engine.get_image(tileset_name).get_tile(tile_pos))
	return tile_name

def load_tmx_map(filename, engine):
	""" Loads Map from given file.
	Will load any image tileset required (if it is not loaded yet).

	Tile layers are loaded in terrain tiles in given order.

	Objects are recognized by properites:
	- passable(bool): additional Terrain image, makes terrain passable/blocked.
	- portal_dest_*: Creates portal tile (all properties are required):
	  - portal_dest_map: Name of the map to go to.
	  - portal_dest_x,
	    portal_dest_y: Destination tile on the target map.

	Objects that are not recognized are loaded into terrain tiles as top images.
	"""
	tiled_map = pytmx.TiledMap(filename)
	tileset_sizes = dict((
		Path(filename).parent/tileset.source,
		Size(tileset.columns, tileset.tilecount // tileset.columns),
		) for tileset in tiled_map.tilesets)

	tiles = Matrix((tiled_map.width, tiled_map.height), [])
	for layer in tiled_map.visible_tile_layers:
		layer = tiled_map.layers[layer]
		for x, y, image in layer.tiles():
			tile_name = _load_tmx_image_tile(image, engine, tileset_sizes)
			tiles.cell((x, y)).append(tile_name)
	objects = defaultdict(list)
	for layer in tiled_map.visible_object_groups:
		layer = tiled_map.layers[layer]
		for obj in layer:
			pos = Point(
				int(obj.x // obj.width),
				int(obj.y // obj.height),
				)
			objects[pos].append(obj)
			tile_name = _load_tmx_image_tile(obj.image, engine, tileset_sizes)
			tiles.cell(pos).append(tile_name)

	real_map = Map(tiles.size)
	for pos in real_map.tiles.keys():
		passable = True
		for obj in (objects[pos] if pos in objects else []):
			if 'passable' in obj.properties and not obj.passable:
				passable = False
			if 'portal_dest_map' in obj.properties:
				real_map.add_portal(pos, Portal(
					obj.portal_dest_map,
					(obj.portal_dest_x, obj.portal_dest_y),
					))
		real_map.set_tile(pos, Terrain(tiles.cell(pos), passable=passable))
	return real_map
