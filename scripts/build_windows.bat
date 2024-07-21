@echo off
call venv\Scripts\activate.bat
python scripts\update_version.py
pyinstaller --onefile --name StarDodge.exe --add-data "assets;assets" -i .\assets\images\space_ship3.ico game.py
