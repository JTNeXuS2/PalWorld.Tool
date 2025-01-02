@echo off
title "Palworld_bot %cd%"

:start
python Palworld_bot.py
timeout /t 5
goto start
