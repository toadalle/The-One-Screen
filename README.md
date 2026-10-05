# The One Screen

A single-screen conversion for **The Legend of Zelda: Ocarina of Time 3D**, built for traditional controllers and Azahar.

## Features

- Controller-friendly HUD with Xbox-style labels
- LB/RB item support and corrected X/Y item slots
- Adapted inventory, gear, map, and frontend menus
- Reworked Ocarina controls and song sheet
- D-pad shortcuts and context-sensitive screen switching

## Installation

**USA Rev 1 only** | Title ID `0004000000033500` | **Alpha 1.1.12**

[Download ZIP](https://github.com/toadalle/The-One-Screen/archive/refs/heads/main.zip), extract it, and copy `load` into your Azahar user directory. Replace any previous version of this title's mod.

```text
load/mods/0004000000033500/
```

A legally obtained game copy is required. No ROM or retail executable is included. Separate texture packs shown in screenshots are not bundled.

## Controls

Bind A/B/X/Y directly in Azahar; LT/RT to L/R and LB/RB to ZL/ZR.

| Control | Action |
| --- | --- |
| D-pad Up / Down | Items / Gear |
| D-pad Right | Ocarina |
| Hold D-pad Left | View |
| Start / Select | Pause / Map |

In Ocarina mode, B plays the native A note, A quits, and RB opens the song sheet.

## Screenshots

![Gameplay HUD](screenshots/gameplay-hud.png)

| Inventory | Ocarina |
| --- | --- |
| ![Inventory](screenshots/inventory.png) | ![Ocarina](screenshots/ocarina-controls.png) |

![Song sheet](screenshots/song-sheet.png)

## Building

Requires Python 3, Zig 0.14.1, `requirements-build.txt`, your own retail inputs matching `config/resource_inputs.json`, and `CascadiaCode-Regular.ttf` in `assets/fonts/`.

```sh
python -m pip install -r requirements-build.txt
python tools/build.py --retail-dir PATH_TO_RETAIL --zig PATH_TO_ZIG --output tos-alpha-1.1.12.zip
```

Developed with AI assistance from ChatGPT and Codex.

## License

[MIT](LICENSE) covers original project code, scripts, tooling, and documentation. Game-derived assets and inherited third-party material are excluded; see [third-party notices](THIRD_PARTY_NOTICES.md).

Unofficial project; not affiliated with or endorsed by Nintendo.
