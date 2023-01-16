""" Utilities for TMX (Tiled editor) maps.
"""
import os
from collections import defaultdict
from pathlib import Path
import pytmx
from ...math import Matrix, Point, Size
from ...game.actor import NPC
from ...game.items import Item, CollectibleItem
from ...game.map import Map, Terrain, Portal, Trigger
from ...game.quest import QuestStateChange
from .image import TileSetImage
from ...utils.meta import typed
from ._base import Engine

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

@typed((str, Path), Engine)
def load_tmx_map(filename, engine):
	""" Loads Map from given file.
	Will load any image tileset required (if it is not loaded yet).

	Tile layers are loaded in terrain tiles in given order.

	Objects are mainly recognized by type:
	- npc: Non-player character.
	  - name: (Required)
	  May have optional properties:
	  - trigger: Trigger for interacting with the NPC.
		See definition below for details.
	  - quest: It means that NPC is a part of a quest,
		and there should be a quest action with the name of the NPC present in that quest.
		It will be triggered upon interaction with the NPC.
	- portal: Portal tile (all properties are required):
	  - dest_map: Name of the map to go to.
	  - dest_x,
	    dest_y: Destination tile on the target map.

	Other objects (without known type) are considered additional Terrain image with optional properties.

	All objects may have optional properites:
	- passable(bool): additional Terrain image, makes terrain passable/blocked.
	- trigger: name of the action callback that's executed when player steps on the tile.
	  Action callback should be register beforehand using SDLEngine.register_trigger_action()

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
			if obj.type not in ['npc', 'item']:
				tile_name = _load_tmx_image_tile(obj.image, engine, tileset_sizes)
				tiles.cell(pos).append(tile_name)

	real_map = Map(tiles.size)
	for pos, _ in real_map.iter_tiles():
		passable = True
		for obj in (objects[pos] if pos in objects else []):
			if obj.type == 'item':
				sprite_name = _load_tmx_image_tile(obj.image, engine, tileset_sizes)
				if 'amount' in obj.properties:
					item = CollectibleItem(obj.name, sprite_name, obj.amount)
				else:
					item = Item(obj.name, sprite_name)
				real_map.add_item(pos, item)
				continue
			if obj.type == 'npc':
				sprite_name = _load_tmx_image_tile(obj.image, engine, tileset_sizes)
				trigger = None
				if 'trigger' in obj.properties:
					trigger = Trigger(obj.trigger)
				if 'quest' in obj.properties:
					trigger = QuestStateChange(obj.quest, obj.name)
				npc = NPC(obj.name, sprite_name, trigger=trigger)
				real_map.add_actor(pos, npc)
				continue
			if obj.type == 'portal':
				real_map.add_portal(pos, Portal(
					obj.dest_map,
					(obj.dest_x, obj.dest_y),
					))
				continue
			if 'passable' in obj.properties and not obj.passable:
				passable = False
			if 'trigger' in obj.properties:
				real_map.add_trigger(pos, Trigger(obj.trigger))
			if 'quest' in obj.properties:
				trigger = QuestStateChange(obj.quest, obj.name)
				real_map.add_trigger(pos, trigger)
		real_map.set_tile(pos, Terrain(tiles.cell(pos), passable=passable))
	return real_map
