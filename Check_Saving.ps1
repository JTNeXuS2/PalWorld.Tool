$file = "C:\wgsm\servers\3\serverfiles\Pal\Saved\SaveGames\0\1BD18BF5482BEA39D7037EB9EFDADBB2\Level.sav"
$timeout = 3 * 60 # last change save 3 min ago
$retryInterval = 2 * 60 # check every 2 minutes
$ip = "65.109.109.73" # server ip
$port = 8215 # server port rcon
$rcon_pass = "RCONPASS"
$rcon_path = "C:\wgsm\servers\Tool\ARRCON.exe" # find and download from https://github.com/radj307/ARRCON/releases

$checkCount = 1
$host.ui.RawUI.WindowTitle = $MyInvocation.MyCommand.Definition +" Save: "+ $file

while ($true) {
    try {
        $lastWriteTime = (Get-Item -Path $file).LastWriteTime
        $timeDiff = (Get-Date) - $lastWriteTime

        if ($timeDiff.TotalSeconds -gt $timeout) {
            if ($checkCount -ge 4) {
                Write-Output "SERVER CAN'T SAVE ALL TIME, RESTARTING!!! Last saved: $lastWriteTime"
                & $rcon_path -H $ip -P $port -p $rcon_pass "Shutdown 10 RESTART 10 SECONDS"
                Write-Output "RESTARTING!!!"
                $checkCount = 1
                Start-Sleep -Seconds 130
                & $rcon_path -H $ip -P $port -p $rcon_pass "Save"
            } else {
                Write-Output "SERVER CAN'T SAVE $checkCount TIME!!! Last saved: $lastWriteTime"
                & $rcon_path -H $ip -P $port -p $rcon_pass "pgbroadcast Level.sav Failed to save... lets try to force it"
                & $rcon_path -H $ip -P $port -p $rcon_pass "Save"
                $checkCount++
            }
        } else {
            Write-Output "Check $checkCount. Last saved: $lastWriteTime"
            $checkCount = 1
        }
    }
    catch {
        Write-Error "Error: $_"
        $checkCount = 1
    }
    Start-Sleep -Seconds $retryInterval
}
