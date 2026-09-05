# Water Game

A small management game about pumping, cleaning and selling water, written in
Python with [Pyxel](https://github.com/kitao/pyxel).

**[Play it in a browser](https://game.konh.org)** — nothing to install.

## What you do

Buy pumps, place them on the world map, take contracts, and spend the profit on
better equipment. The lab lets you research upgrades; the collection tracks what
you have found.

## Running it locally

```bash
pip install pyxel
pyxel run water_game
```

Or play the packaged version:

```bash
pyxel play water_game.pyxapp
```

## How it is put together

| Path | What it does |
| --- | --- |
| `water_game/main.py` | Entry point and the scene loop |
| `water_game/scenes/` | Title, world map, shop, lab, collection, results, ending |
| `water_game/graphics/` | Sprites, particles, animations, UI, cursor |
| `water_game/data/` | Pumps, contracts and levels — the game's numbers, kept out of the code |

`index.html` is the whole game compiled to a single self-contained page: the
`.pyxapp` is embedded in it as base64 and runs through Pyxel's WebAssembly
build, so it needs no server beyond somewhere to serve one file.

## Licence

MIT — see [LICENSE](./LICENSE).
