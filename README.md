nanomyth
========

Very minimal engine for very simple RPGs.

Building and installing
-----------------------

To build package, run:

```sh
$ make build
# OR directly:
$ python setup.py build
$ python -m pip wheel --disable-pip-version-check . --no-deps --wheel-dir=dist
```

Install created package directly via `pip`:

```sh
$ pip install -U dist/nanomyth-*.whl
```

Demo app
--------

There is a demo app that presents in form of a simple and small game.
It's source demonstrates usage of engine API and various patterns.

Demo app uses free graphics from OpenGameArt:
- Tile set: <https://opengameart.org/content/dawnlike-16x16-universal-rogue-like-tileset-v181>
- Font: <https://opengameart.org/content/8x8-font>
- Set of backgrounds: <https://opengameart.org/content/6-adventure-game-backgrounds>

Just run `python demo/demo.py`.

TODO
----

1. [X] Simple static map on single screen.
	- [X] Loading tilesets from file.
	- [X] Loading map layout from file.
2. [X] Main menu.
	- [X] MVC for all objects.
	- [X] Screens (contexts), stackable event loops: update()+draw().
	- [X] Simple menu with keyboard controls.
	- [X] Play/Continue/Exit.
3. [X] Player character.
	- [X] Movement on map.
	- [X] Facing directions.
	- [X] Obstacles.
4. [X] World of maps.
	- [X] Separate set of adjoined maps.
	- [X] Movement between maps (exits, entrances, portals; entering/starting points).
5. [X] Saving/loading.
	- [X] Pickle, jsonpickle, custom serializers via `__getstate__`/`__setstate__`
	- [X] Save/load in menu.
	- [X] Different slots for saving, separate dialog screen for choosing slot.
	- [X] Dialog for overwriting save files [Yes/No].
6. [X] Autosave.
	- [X] Terrain with trigger event.
	- [X] Autosaving on checkpoint tiles.
	- [X] Displaying message box [OK] on autosaving.
7. [X] NPC.
	- [X] Standalone objects like characters, info posts etc.
	- [X] Interactions with NPC.
	- [X] Separate screen dialog for large scrollable texts.
8. [X] Quests.
	- [X] Triggers to start/stop quests (checkpoint tiles, talking with NPCs).
	- [X] Quest steps, conditions on moving to the next step.
	- [X] Displaying current quest state on HUD.
	- [X] List of quests, quest book dialog.
9. [ ] Items.
	- [X] Items laying on terrain.
	- [X] Slot for item, picking/dropping items.
	- [ ] Character's inventory, inventory screen dialog.
	- [ ] Displaying inventory status on HUD.
	- [ ] Stackable items, non-stackable unique items.
	- [ ] Usable items, using items on target (NPC, object).
	- [ ] Triggers for items (for NPC/quests, opening terrain etc).
	- [ ] One-time pickable item stashes (like piles, loot-drops or chests).
	- [ ] External stashes (shelves). Exchanging items with stash.
10. [ ] MOBs.
	- [ ] Standing still, random shuffling, sentinel waypoints.
	- [ ] Interaction with mobs: using items, talking.
	- [ ] Hitting mobs, HP, damage.
	- [ ] Displaying battle log, info about battle state, hp, hits etc.
11. [ ] Battle.
	- [ ] Player's HP. Mobs hitting back.
	- [ ] Displaying player's stats on HUD.
	- [ ] Items for battle: weapon/shield, armor/clothing.
	- [ ] Mobs can have and use items too.
	- [ ] Mobs can have inventory and drop loot.
	- [ ] Trigger for quests on monster death.
	- [ ] Projectiles, throwing.
11. [ ] Animation based on sprite sheets.
	- [ ] Animated static objects.
	- [ ] Animated movements, hits, projectiles, particle events.
	- [ ] Transition effects for screens/movements between maps.
12. [ ] Extra.
	- [ ] Doors (open/closed/locked/unlocked).
	- [ ] Destructible terrain.
	- [ ] Moveable/pullable objects (sokoban crates).
	- [ ] Switches/levers with triggers.
	- [ ] Press-plates (moving objects on them, dropping items) with triggers (doors, quests etc).
	- [ ] Damaging terrain (beartraps, spikes etc).
	- [ ] Explosions with damage range (bombs, DOOM barrels, throwable grenades etc).
