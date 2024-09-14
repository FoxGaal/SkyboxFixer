@echo off
if "%1"=="1" goto main
set /p input=Would you like to run first time setup? (y/N): 
if "%input%"=="y" goto setup
:main
python main.py
PAUSE>nul
exit
:setup
python setup.py
