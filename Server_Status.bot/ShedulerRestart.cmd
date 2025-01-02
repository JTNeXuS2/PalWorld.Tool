@echo off
cd %~dp0
chcp 65001
setlocal enabledelayedexpansion

set "host=65.109.107.147"
set "port=8215"
set "rcon_pass=RCON/ADMIN"
:: 05:50 and 16:50 Autorun + 10 min for annonces
set triggers="(New-ScheduledTaskTrigger -Daily -At '05:50'), (New-ScheduledTaskTrigger -Daily -At '16:50')"

set "originalPath=%~dp0"
set "modifiedPath=%originalPath:\=_%"
set "modifiedPath=%modifiedPath:/=_%"
set "modifiedPath=%modifiedPath::=_%"
title "%modifiedPath%"

:: Run once to setup script in to windows task sheduler (taskschd.msc) 11:50 Autorun
schtasks /query /tn "%modifiedPath%"
echo %errorlevel%
if %errorlevel% == 1 (
    echo Task not found. Adding task to the scheduler...

    rem Создаем задачу с двумя триггерами через PowerShell

    powershell -Command "Register-ScheduledTask -TaskName '%modifiedPath%' -Action (New-ScheduledTaskAction -Execute '%~dp0ShedulerRestart.cmd') -Trigger !triggers! -Force"

    echo Task created successfully.
    echo exit
    timeout /t 5
    exit
)


:: ANNONCE pgbroadcast- palguard / broadcast - vanilla
echo Discord annonce 1
"C:\wgsm\servers\Tool\ARRCON.exe" -H %host% -P %port% -p %rcon_pass% "pgbroadcast RESTART 10 MINUTES"
timeout /t 300

echo Discord annonce 2
"C:\wgsm\servers\Tool\ARRCON.exe" -H %host% -P %port% -p %rcon_pass% "pgbroadcast RESTART 5 MINUTES"
timeout /t 240

echo Discord annonce 3
"C:\wgsm\servers\Tool\ARRCON.exe" -H %host% -P %port% -p %rcon_pass% "pgbroadcast RESTART 60 SECONDS"
timeout /t 50

"C:\wgsm\servers\Tool\ARRCON.exe" -H %host% -P %port% -p %rcon_pass% "pgbroadcast RESTART 10 SECONDS"
timeout /t 5
"C:\wgsm\servers\Tool\ARRCON.exe" -H %host% -P %port% -p %rcon_pass% "pgbroadcast RESTART 5 SECONDS"
timeout /t 5

echo Exiting Worlds...
"C:\wgsm\servers\Tool\ARRCON.exe" -H %host% -P %port% -p %rcon_pass% "Shutdown 2 STOP"
timeout /t 10

EXIT
