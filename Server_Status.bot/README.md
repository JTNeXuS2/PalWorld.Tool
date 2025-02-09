### Features
    Server Status - {prefex}_sendhere
    CrossChat - use once {prefex}_lookhere or anonim {prefex}_annonce
    Auto Announcements in annonces.txt 1 string = 1 annonce
    List Players - {prefex}_players
### Requires
    Python 3.8 or higher is required.
### install
    pip install -U disnake
    pip install -U matplotlib
    pip3 install python-a2s
    pip install aiofiles
    pip install requests
    pip install psutil
    
    enable rest_api on pal-server (add on startup -RESTAPIEnabled=True -RESTAPIPort=8216 -AdminPassword="RCON/ADMIN/API PASSWORD")

    enable logs in serverfiles\Pal\Binaries\Win64\PalDefender\Config.json or old config palguard\palguard.json
    "logChat": true,
    "logPlayerDeaths": true,
    "logPlayerIP": true,
    "logPlayerLogins": true,
    "logPlayerUID": true,
#### Create app
    https://discord.com/developers/applications/
and get token
![image](https://github.com/JTNeXuS2/SoulMask.Tools/assets/88918931/1bbc7362-5a92-47c5-a314-d41ec9b4fd36)
enable intents
![image](https://github.com/JTNeXuS2/SoulMask.Tools/assets/88918931/7b8b7f40-3129-4d96-bfe6-b0bea1d80422)
#### Fill Config.ini
      bot_name = PalWorld x2
      token = secret_token
      ip = server_ip
      query_port = server_query_port
      restapi_port = server_restapi_port
      password = RCON/ADMIN
      command_prefex = short command prefix
      log_dir = path to palguard log
      webhook_url = discord webhook
      channel_id, message_id = use pal_sendhere in discord
      crosschat_id = use pal_lookhere in discord
      ch_list = list chanels to send in the webhook
      cmd_list = list comands  or prefex to hide in the webhook
      cheaters = send cheater warn in webhook
      hide_personal_data = hide platform id in webhook

launch !Start.cmd

invate your bot to discord (open link in browser)
![image](https://github.com/JTNeXuS2/SoulMask.Tools/assets/88918931/4d904844-cc7f-4a60-8ddb-5910c2555e23)

enter /commandprefex_sendhere (default in config /pal_sendhere) in channel

### have fun!
    screenshots
![image](https://github.com/user-attachments/assets/c3cdfb97-2568-47d9-b47a-0a8c1cef6dc5)
![image](https://github.com/user-attachments/assets/6006815f-6e30-4b98-9952-f0f430c76fab)
![image](https://github.com/user-attachments/assets/27ba738e-6e9f-4d47-97e7-268337356392)




#### find me on discord [![Discord](https://discordapp.com/api/guilds/626106205122592769/widget.png?style=shield)](https://discord.gg/qYmBmDR)
#### Donate for me
#### [yoomoney](https://yoomoney.ru/to/4100116619431314)
https://fkwallet.io  ID: F7202415841873335
#### [boosty](https://boosty.to/_illidan_)
