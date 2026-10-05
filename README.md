# The One Screen

A comprehensive single-screen conversion for **The Legend of Zelda: Ocarina of Time 3D**, designed to feel natural on a traditional controller and modern emulator setup.

The mod reworks the game's UI, controls, HUD behavior, menus, Ocarina interface, and screen-routing logic so that touchscreen-dependent features can be used comfortably without constantly interacting with a second display.

**The goal is to preserve the look and feel of Ocarina of Time 3D while making it behave more like a native single-screen console game.**

![The One Screen gameplay HUD — Link on the purple and gold platform in Kakariko Village](screenshots/gameplay-hud.png)

## Features

- Single-screen-friendly gameplay and menu presentation
- Redesigned HUD for traditional controllers
- Xbox-style button labels and contextual controls
- Proper LB/RB item functionality
- Correct X/Y item-slot behavior
- Reworked Ocarina controls, presentation, and song sheet
- D-pad shortcuts for Items, Gear, Ocarina, and View
- Start opens the Pause menu; Select opens the Map
- Inventory, Gear, Map, File Select, and other interfaces adapted for the new layout
- Context-sensitive screen switching for special game states
- Frontend backdrop fixes and full-width main-screen transition fades
- Numerous HUD and UI fixes designed specifically around single-screen play

Enjoying The One Screen? [Support development with a donation via PayPal](https://www.paypal.com/donate/?hosted_button_id=UCP5YEHAS7HYA).

## Compatibility and installation

**USA Rev 1 only** | Title ID `0004000000033500` | **Alpha 1.1.12**

Designed for **The Legend of Zelda: Ocarina of Time 3D — USA Rev 1** and tested primarily with **Azahar**.

[Download ZIP](https://github.com/toadalle/The-One-Screen/archive/refs/heads/main.zip), extract it, and copy `load` into your Azahar user directory. Replace any previous version of this title's mod.

```text
load/mods/0004000000033500/
```

A legally obtained game copy is required. No game ROM, CIA, CCI, or copyrighted retail executable is included. Separate texture packs shown in screenshots are not bundled.

## Controls

### Azahar bindings

| Controller | 3DS binding |
| --- | --- |
| A / B / X / Y | A / B / X / Y respectively |
| LT / RT | L / R |
| LB / RB | ZL / ZR |
| Start / Select | Start / Select |
| D-pad | Corresponding D-pad directions |
| Left stick | Circle Pad |

### Gameplay shortcuts

| Control | Action |
| --- | --- |
| D-pad Up | Items |
| D-pad Down | Gear |
| D-pad Right | Ocarina |
| Hold D-pad Left | View |
| Start | Pause menu |
| Select | Map |

The mod handles item-slot translation internally: Xbox Y uses the native X item lane, and Xbox X uses the native Y item lane.

### Ocarina

| Control | Action |
| --- | --- |
| B | Play the native A note |
| A | Quit |
| RB | Open the song sheet |

The remaining notes use the LT, RT, X, and Y labels shown on screen.

## Screenshots

The main image above shows the controller HUD in Kakariko Village. These screenshots also showcase the adapted menus and Ocarina interfaces.

![Gameplay HUD at a forest entrance](screenshots/gameplay-forest.png)

| Inventory | Ocarina |
| --- | --- |
| ![Inventory](screenshots/inventory.png) | ![Ocarina](screenshots/ocarina-controls.png) |

| Song sheet | File Select |
| --- | --- |
| ![Song sheet with Xbox-style note labels](screenshots/song-sheet.png) | ![Adapted File Select screen](screenshots/file-select.png) |

| Sheikah visions | Boss challenge |
| --- | --- |
| ![Sheikah vision selection menu](screenshots/visions.png) | ![Boss challenge selection menu](screenshots/boss-challenge.png) |

## Optional Azahar graphics settings

To use the graphics settings pictured in the showcase setup, open **Azahar Configuration → Graphics → Enhancements** and use the following as a starting point. These enhancements are optional; choose a lower internal resolution if needed for smooth performance.

| Setting | Showcase value |
| --- | --- |
| Internal Resolution | 6x Native (2400×1440) |
| Use Integer Scaling | Off |
| Enable Linear Filtering | On |
| Post-Processing Shader | None (builtin) |
| Texture Filter | xBRZ |
| Stereoscopic 3D Mode | Off |
| Depth | 0% |
| Eye to Render in Monoscopic Mode | Left Eye (default) |
| Disable Right Eye Rendering / Swap Eyes | Off |
| Use custom textures | On |
| Preload custom textures | Off |
| Async custom texture loading | On |
| Dump textures | Off |

**Custom textures require a separately installed texture pack.** Enabling the option alone does not install textures, and these settings alone may not reproduce every detail of the showcase images.

![Azahar Graphics Enhancements settings used for the showcase setup](screenshots/azahar-graphics-settings.png)

## Building

Requires Python 3, Zig 0.14.1, `requirements-build.txt`, your own retail inputs matching `config/resource_inputs.json`, and `CascadiaCode-Regular.ttf` in `assets/fonts/`.

```sh
python -m pip install -r requirements-build.txt
python tools/build.py --retail-dir PATH_TO_RETAIL --zig PATH_TO_ZIG --output tos-alpha-1.1.12.zip
```

## Development

The One Screen was developed through extensive reverse engineering, testing, iteration, and community tooling. AI-assisted development tools, including ChatGPT and Codex, were used during portions of the reverse-engineering and implementation process.

## Credits

Shout-out to [M-1](https://gamebanana.com/members/1544353) and their [OoT3D: Single Screen Experience](https://gamebanana.com/mods/695893). Seeing another approach to single-screen OoT3D was a major source of inspiration and helped spark ideas for what could be improved or approached differently.

**The One Screen was developed independently and does not include or redistribute code or files from M-1's mod.** The projects take their own approaches to many of the same problems, and their work deserves recognition for helping inspire this one.

## License

[MIT](LICENSE) covers original project code, scripts, tooling, and documentation. Game-derived assets and inherited third-party material are excluded; see [third-party notices](THIRD_PARTY_NOTICES.md).

Unofficial project; not affiliated with or endorsed by Nintendo.
