#!/bin/bash -x
source .venv/bin/activate
python scripts/update_version.py
pyinstaller --onedir --name StarDodge --windowed --add-data "assets:assets" --add-data "data_no_git:data_no_git" -i ./assets/images/space_ship3.icns game.py
