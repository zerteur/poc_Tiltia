@echo off
:: Script batch pour lancer une application Python avec un argument

:: Spécifier le chemin complet vers l'exécutable Python si nécessaire
:: Par exemple, set PYTHON_PATH="C:\Python39\python.exe"
set PYTHON_PATH=py

:: Spécifier le chemin vers le script Python
set SCRIPT_PATH=C:\Users\lproudhom\Documents\Web\Alt\main.py

:: Argument à passer au script Python
set ARGUMENT=10.208.0.0/22

:: Exécution du script Python avec l'argument
%PYTHON_PATH% %SCRIPT_PATH% %ARGUMENT%

:: Pause pour garder la fenêtre ouverte après l'exécution
pause
