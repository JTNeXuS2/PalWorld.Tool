:: ADD compatible PalGuard 1.5.2+ Auto Update
:: Add sav_cli 
@echo off
cd %~dp0
chcp 65001
setlocal enabledelayedexpansion

set "host=65.109.109.73"
set "port=8215"
set "rcon_pass=RCON/ADMIN"
set triggers="(New-ScheduledTaskTrigger -Daily -At '23:50'), (New-ScheduledTaskTrigger -Daily -At '04:50'), (New-ScheduledTaskTrigger -Daily -At '08:50'), (New-ScheduledTaskTrigger -Daily -At '11:50'), (New-ScheduledTaskTrigger -Daily -At '15:50'), (New-ScheduledTaskTrigger -Daily -At '19:50')"

set "originalPath=%~dp0"
set "modifiedPath=%originalPath:\=_%"
set "modifiedPath=%modifiedPath:/=_%"
set "modifiedPath=%modifiedPath::=_%"
title "%modifiedPath%"

::goto DEBUG
::pause

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
"C:\wgsm\servers\Tool\ARRCON.exe" -H %host% -P %port% -p %rcon_pass% "Save"
timeout /t 300

echo Discord annonce 2
"C:\wgsm\servers\Tool\ARRCON.exe" -H %host% -P %port% -p %rcon_pass% "pgbroadcast RESTART 5 MINUTES"
timeout /t 240

echo Discord annonce 3
"C:\wgsm\servers\Tool\ARRCON.exe" -H %host% -P %port% -p %rcon_pass% "pgbroadcast RESTART 60 SECONDS"
"C:\wgsm\servers\Tool\ARRCON.exe" -H %host% -P %port% -p %rcon_pass% "Save"
timeout /t 50

echo Exiting Worlds...
timeout /t 2
"C:\wgsm\servers\Tool\ARRCON.exe" -H %host% -P %port% -p %rcon_pass% "Shutdown 10 RESTART 10 SECONDS"
timeout /t 5
"C:\wgsm\servers\Tool\ARRCON.exe" -H %host% -P %port% -p %rcon_pass% "pgbroadcast RESTART 5 SECONDS"
timeout /t 13

:KILL

:update_palguard
set API_URL=https://api.github.com/repos/Ultimeit/PalDefender/releases/latest
set "DOWNLOAD_URL="
set "DOWNLOAD_d3d9="
powershell -Command "try { Invoke-WebRequest -Uri '%API_URL%' -TimeoutSec 5 -UseBasicParsing | Out-Null; exit 0 } catch { exit 1 }"
if errorlevel 1 (
    echo Ошибка: Сайт недоступен или таймаут 5 секунд превышен. Скачивание отменено.
    goto skip_update
)
:: NEW PalDefender.zip
if "%DOWNLOAD_URL%"=="" (
	for /f "usebackq delims=" %%A in (`powershell -Command "(Invoke-WebRequest -Uri '%API_URL%' -UseBasicParsing).Content | ConvertFrom-Json | Select-Object -ExpandProperty assets | Where-Object { $_.name -eq 'PalDefender.zip' } | Select-Object -ExpandProperty browser_download_url"`) do set DOWNLOAD_URL=%%A
	:: d3d9
	for /f "usebackq delims=" %%A in (`powershell -Command "(Invoke-WebRequest -Uri '%API_URL%' -UseBasicParsing).Content | ConvertFrom-Json | Select-Object -ExpandProperty assets | Where-Object { $_.name -eq 'd3d9.dll' } | Select-Object -ExpandProperty browser_download_url"`) do set DOWNLOAD_d3d9=%%A
)
:: OLD PalDefender_Windows.zip
if "%DOWNLOAD_URL%"=="" (
	for /f "usebackq delims=" %%A in (`powershell -Command "(Invoke-WebRequest -Uri '%API_URL%' -UseBasicParsing).Content | ConvertFrom-Json | Select-Object -ExpandProperty assets | Where-Object { $_.name -eq 'PalDefender_Windows.zip' } | Select-Object -ExpandProperty browser_download_url"`) do set DOWNLOAD_URL=%%A
)
if "%DOWNLOAD_URL%"=="" (
    echo Ошибка: Не удалось найти ссылку на PalDefender.zip в последнем релизе.
    goto skip_update
)

:: Download PalGuard
powershell -Command "Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile 'PalDefender.zip' -UseBasicParsing"
:: Download d3d9

if "!DOWNLOAD_d3d9!" neq "" (
	powershell -Command "Invoke-WebRequest -Uri '%DOWNLOAD_d3d9%' -OutFile 'd3d9.dll' -UseBasicParsing"
)

if not exist PalDefender.zip (
    echo Ошибка при скачивании файла.
    goto skip_update
)
if exist PalDefender.zip (
    echo Update PalGuard
	if exist "Pal\Binaries\Win64\PalDefender.DELETE" del /f /q "Pal\Binaries\Win64\PalDefender.DELETE"
	if exist "Pal\Binaries\Win64\version.DELETE" del /f /q "Pal\Binaries\Win64\version.DELETE"
	if exist "Pal\Binaries\Win64\d3d9.DELETE" del /f /q "Pal\Binaries\Win64\d3d9.DELETE"
	::
	if exist "Pal\Binaries\Win64\PalDefender.dll" ren "Pal\Binaries\Win64\PalDefender.dll" "PalDefender.DELETE"
	if exist "Pal\Binaries\Win64\version.dll" ren "Pal\Binaries\Win64\version.dll" "version.DELETE"
	if exist "Pal\Binaries\Win64\d3d9.dll" ren "Pal\Binaries\Win64\d3d9.dll" "d3d9.DELETE"
	
	echo Распаковываем PalDefender.zip — извлекаем только PalDefender.dll и version.dll в Pal\Binaries\Win64
	powershell -Command "Add-Type -AssemblyName System.IO.Compression.FileSystem; $zip = [System.IO.Compression.ZipFile]::OpenRead('PalDefender.zip'); $dest='Pal\Binaries\Win64'; if (-not (Test-Path $dest)) { New-Item -ItemType Directory -Path $dest | Out-Null }; foreach ($entry in $zip.Entries) { if ($entry.Name -eq 'PalDefender.dll' -or $entry.Name -eq 'version.dll' -or $entry.Name -eq 'd3d9.dll') { $target = Join-Path $dest $entry.Name; $stream = $entry.Open(); $fileStream = [System.IO.File]::Open($target, [System.IO.FileMode]::Create); $stream.CopyTo($fileStream); $fileStream.Close(); $stream.Close() } }; $zip.Dispose()"
	
	if exist "d3d9.dll" move "d3d9.dll" "Pal\Binaries\Win64\d3d9.dll"
)
:skip_update
timeout /t 3


taskkill /f /im pst.exe
taskkill /f /im sav_cli.exe
del /s /q "C:\wgsm\servers\3\serverfiles\PST\save-tools-err.txt"
del /s /q "C:\wgsm\servers\3\serverfiles\PST\save-tools-out.txt"
del /s /q "C:\wgsm\servers\3\serverfiles\PST\pst.db"
if exist "Pal\Binaries\Win64\PalDefender.DELETE" del /f /q "Pal\Binaries\Win64\PalDefender.DELETE"
if exist "Pal\Binaries\Win64\version.DELETE" del /f /q "Pal\Binaries\Win64\version.DELETE"

:FIND
set "WindowTitle=%~dp0Pal\Binaries\Win64"
:: FIND PID
::powershell.exe -command "$Processes = Get-Process; $Processes | Where-Object {$_.MainWindowTitle -like '*%WindowTitle%*'} | ForEach-Object {Write-Host $_.Id}"
::powershell.exe -command "$Processes = Get-Process; $Processes | Where-Object { $_.Path -like '*%WindowTitle%*' } | ForEach-Object {Write-Host $_.Id}"

:: KILL
::powershell.exe -command "$Processes = Get-Process; $Processes | Where-Object {$_.MainWindowTitle -like '*%WindowTitle%*'} | ForEach-Object {Stop-Process -Id $_.Id}"
powershell.exe -command "$Processes = Get-Process; $Processes | Where-Object { $_.Path -like '*%WindowTitle%*' } | ForEach-Object {Stop-Process -Id $_.Id}"

:DEBUG
timeout /t 1
cd %~dp0SaveCleaner
call "^!DelPlayers.bat"
timeout /t 3
EXIT
