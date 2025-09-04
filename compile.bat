pip install pyinstaller
pyinstaller --onefile --noconsole --icon="images/M.ico" --add-data="images/*;images" --add-data="images/M.ico;." --add-data="images/settings.png;." --add-data="images/freedomdive.png;." --clean HPSolver.py
rmdir /s /q build
del /q HPSolver.spec
