python -m pip install pyinstaller
python -m PyInstaller --onefile --noconsole --icon="images/M.ico" --add-data="images/*;images" --clean HPSolver.py
rmdir /s /q build
del /q HPSolver.spec
