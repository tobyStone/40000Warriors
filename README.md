40000 Warriors

A 2D side‑scroll action game built with Python and Pygame, featuring a Space Marine Scout battling hordes of Tyranid enemies through gothic halls and boss arenas.

🔥 Features

Player: Control a Space Marine Scout with ranged and melee attacks, ammo management, health and armor.

Tyranid Enemies: Variety of Tyranid types (Genestealer, Warrior, Gaunt, Lictor, Carnifex, Zoanthrope, Mawloc, etc.) with unique stats and behaviors.

NPC System: Interact with NPCs (Sergeant Tarkus, Magos Vex, Inquisitor Kryptman) to drive objectives.

Room System: Four distinct rooms (Main Hall, Armory, Chapel, Boss Arena) with smooth transitions.

Bosses: Special boss encounters with unique mechanics (ground pound, psychic blast, swoop attacks).

Pickups & UI: Ammo, health pickups; on‑screen bars, kill counter, objectives display.

Cutscene Player: Intro video support (assets/cut_scenes/intro.mp4).

Configurable Sprite Loader:

Loads from assets/character/ (PNG filenames are matched case‑insensitive, dash/underscore tolerant).

Falls back to assets/enemies/ or a magenta placeholder if missing.

Auto‑scales sprites to hitbox sizes; global scale factor configurable via TYRANID_SCALE.

Easy Tyranid Control: Disable or resize enemy types by editing tyranid_sprites.py (comment out in factory or adjust hitbox parameters).

📦 Requirements

Python 3.9 (tested on 3.9.x)

Pygame pip install pygame

FFmpeg on your PATH for cutscene playback (or skip intro if unavailable)

Windows (recommended: use the Python launcher py)

🚀 Installation & Running

# Clone the repo
git clone https://github.com/tobyStone/40000Warriors.git
cd 40000Warriors

# Create & activate a Python 3.9 virtual environment
py -3.9 -m venv venv39
venv39\Scripts\activate    # Windows

# Install dependencies
pip install pygame

# (Optional) Verify FFmpeg is installed:
ffmpeg -version

# Run the game
py -3.9 main_game.py

Controls:

← → ↑ ↓ or WASD to move

Left‑click to shoot

V for melee attack

R to reload

E to interact with NPCs

SPACE to activate doors/transitions

P to pause

F to toggle fullscreen

ESC to quit

🗂️ Project Structure

40000Warriors/

assets/

backgrounds/ – Room backgrounds

character/ – Sprite art for player, NPCs, Tyranids

cut_scenes/ – Intro video(s)

boss_system.py – Boss AI & spawning

cutscene_player.py – Cutscene playback helper

game_launcher.py – Entry point (launch GUI/CLI)

generate_sprites.py – (Optional) sprite‑sheet generator

interior_3d.py – 3D room rendering utilities

main_game.py – Main game loop & orchestrator

npc_system.py – NPC creation & dialogue system

pickup_system.py – Health & ammo pickup logic

room_system.py – Room definitions & transitions

scout_marine.py – Player character class

tyranid_sprites.py – Enemy base class & subclasses

ui_system.py – On‑screen HUD, messages, objectives
⚙️ Customization & Tips

Sprite Scale: Tweak TYRANID_SCALE at the top of tyranid_sprites.py to uniformly resize all enemies.

Enable/Disable Enemies: Comment out unwanted entries in the create_tyranid factory or TYRANID_COLORS map.

Asset Paths: The loader first checks assets/character/, then assets/enemies/ if configured, then falls back to a placeholder.

Python Launcher Flags: Use py -3.9 main_game.py to pin the interpreter version.

❓ Troubleshooting

-3.9 not recognized: Ensure the Python launcher is installed. Activate your venv and run python main_game.py instead.

Sprites appear as colored boxes: Verify your PNG filenames exactly match (case‑insensitive) the type names (e.g., carnifex.png, hive_tyrant.png) in assets/character/.

Cutscene fails: Check that assets/cut_scenes/intro.mp4 exists, or remove/rename that file to skip the intro.



