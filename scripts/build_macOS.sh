#!/bin/bash -x
source .venv/bin/activate
python scripts/update_version.py
pyinstaller --onedir --name StarDodge --windowed --add-data "assets:assets" -i ./assets/images/space_ship3.icns game.py
