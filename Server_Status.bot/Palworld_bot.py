#Python 3.8 or higher is required.
#py -3 -m pip install -U disnake
#pip3 install python-a2s
#pip install aiofiles
#pip install psutil

import disnake
from disnake.ext import commands, tasks
from disnake import Intents
import json
import datetime
import a2s
import requests
import configparser
import re
import unicodedata
from requests.auth import HTTPBasicAuth
from concurrent.futures import ThreadPoolExecutor

import aiohttp
import asyncio
import time
import os
import glob
import subprocess
import random
import base64
import aiofiles
import psutil

#Buffer Limits
from collections import deque
MAX_MESSAGES = 14
TIME_WINDOW = 60
BUFFER_LIMIT = MAX_MESSAGES // 2  # Половина лимита
message_buffer = deque()
send_interval = 0
shard_count = 3

#cant used
prefix = '/'

#Nothing change more

def read_cfg():
    config = configparser.ConfigParser(interpolation=None)
    try:
        with open('config.ini', 'r', encoding='utf-8') as file:
            config.read_file(file)
    except FileNotFoundError:
        print("Error: Config.ini not found.")
        return None
    return config
async def write_cfg(section, key, value):
    config = read_cfg()
    if f'{section}' not in config:
        config[f'{section}'] = {}
    config[f'{section}'][f'{key}'] = str(f'{value}')

    with open('config.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)
def update_settings():
    global token, channel_id, crosschat_id, message_id, update_time, bot_name, bot_ava, address, command_prefex, username, password, log_directory, cheat_log_directory, webhook_url, annonce_time, ch_list, cmd_list, cheaters, hide_personal_data, death_send, ingamecmd_list

    config = read_cfg()
    if config:
        try:
            token = config['botconfig'].get('token', None)
            channel_id = config['botconfig'].get('channel_id', None)
            crosschat_id = config['botconfig'].get('crosschat_id', None)
            message_id = config['botconfig'].get('message_id', None)
            bot_name = config['botconfig'].get('bot_name', None)
            bot_ava = config['botconfig'].get('bot_ava', None)
            username = config['botconfig'].get('username', None)
            password = config['botconfig'].get('password', None)
            update_time = config['botconfig'].get('update_time', None)
            annonce_time = config['botconfig'].get('annonce_time', None)
            command_prefex = config['botconfig'].get('command_prefex', None) and config['botconfig'].get('command_prefex').lower()
            address = (config['botconfig'].get('ip', None), int(config['botconfig'].get('query_port', 0)), int(config['botconfig'].get('restapi_port', 0)))
            log_directory = config['botconfig'].get('log_dir', None)
            cheat_log_directory = os.path.join(log_directory, "Cheats/")
            webhook_url = config['botconfig'].get('webhook_url', None)
            ch_list = config['botconfig'].get('ch_list', 'Global, Local, Guild').split(', ')
            cmd_list = config['botconfig'].get('cmd_list', '/, /TeleportToMe').split(', ')
            cheaters = config['botconfig'].getboolean('cheaters', True)
            hide_personal_data = config['botconfig'].getboolean('hide_personal_data', True)
            death_send = config['botconfig'].getboolean('death_send', True)

        except ValueError as e:
            print(f"Error: wrong value in config file {e}")
        except Exception as e:
            print(f"Error: {e}")

token = None
channel_id = None
crosschat_id = None
message_id = None
bot_name = None
bot_ava = None
username = None
password = None
update_time = 10
annonce_time = 600
address = None
command_prefex = None
webhook_url = None
log_directory = None
cheat_log_directory = None
current_file = None
file_position = 0
current_index = 0
cheat_current_file = None
cheat_file_position = 0
useonce = None
ch_list = []
cmd_list = []
ingamecmd_list = []
cheaters = True
hide_personal_data = True
death_send = True
proc = None
proc_pid = None
update_settings()

annonce_file = 'annonces.txt'
if not os.path.exists(annonce_file):
    with open(annonce_file, 'w', encoding='utf-8') as f:
        f.write('')

#bot idents
intents = disnake.Intents.default()
intents.messages = True
intents = disnake.Intents().all()
client = commands.Bot(command_prefix=prefix, intents=intents, case_insensitive=True)
#bot = commands.Bot(command_prefix=prefix, intents=intents, case_insensitive=True)
bot = commands.AutoShardedBot(command_prefix=prefix, intents=intents, shard_count=shard_count ,case_insensitive=True)

def find_latest_file(log_directory):
    list_of_files = glob.glob(f'{log_directory}*')
    # Фильтруем список, исключая файлы, имена которых содержат '-cheats'
    filtered_files = [file for file in list_of_files if '-cheats' not in os.path.basename(file)]
    if not filtered_files:
        return None
    latest_file = max(filtered_files, key=os.path.getctime)
    return latest_file

async def watch_log_file(log_directory):
    global current_file, file_position
    old_line = ""
    while True:
        new_file = find_latest_file(log_directory)
        if new_file != current_file:
            current_file = new_file
            print(f"watch log start at {current_file}")
            file_position = 0
        async with aiofiles.open(current_file, 'r', encoding='utf-8') as file:
            await file.seek(file_position)
            lines = await file.readlines()
            file_position = await file.tell()
        for line in lines:
            if line != old_line:
                await process_line(line)
                old_line = line
        await asyncio.sleep(1)

def find_latest_cheat_file(cheat_log_directory):
    list_of_files = glob.glob(f'{cheat_log_directory}*')
    filtered_files = [file for file in list_of_files if '-cheats_DISABLE' not in os.path.basename(file)]
    if not filtered_files:
        return None
    latest_file = max(filtered_files, key=os.path.getctime)
    return latest_file

async def watch_cheat_log_file(cheat_log_directory):
    global cheat_current_file, cheat_file_position
    old_line = ""
    while True:
        new_file = find_latest_cheat_file(cheat_log_directory)
        if new_file != cheat_current_file:
            cheat_current_file = new_file
            print(f"watch cheat_log start at {cheat_current_file}")
            cheat_file_position = 0

        async with aiofiles.open(cheat_current_file, 'r', encoding='utf-8') as file:
            await file.seek(cheat_file_position)
            lines = await file.readlines()
            cheat_file_position = await file.tell()

        for line in lines:
            if line != old_line:
                await process_line(line)
                old_line = line
        await asyncio.sleep(1)

async def cmd_online():
    info, players, settings, metrics = await request_api(address)
    if players is None:
        print("No players found.")
        return

    players_list = []
    for player in players['players']:
        name = player.get('name', '')
        if not name.strip():
            name = player.get('accountName', '')
        players_list.append(name)
    players_string = ', '.join(players_list)
    #print(f"{players_string}")
    await send_annonce(players_string)

async def process_line(line):
    # Parse log string
    chat_pattern = r"\[(.*?)\] \[info\] \[Chat::([^]]+)\]\['([^']+)' \(([^)]+)\)\](\[Admin\])?: (.+)"
    chat_pattern2 = r"\[(.*?)\]\[info\] \[Chat::([^]]+)\]\['([^']+)' \(([^)]+)\)\](\[Admin\])?: (.+)"

    login_pattern = r"^\[(.*?)\] \[info\] \'(.+?)\' \((.*?)\) has logged (in|out)\.?\s*$"
    login_pattern2 = r"^\[(.*?)\]\[info\] \'(.+?)\' \((.*?)\) has logged (in|out)\.?\s*$"

    death_pattern = r"\[(.*?)\] \[info\] '([^']+)' \(([^)]+)\) was attacked by a wild '([^']+)' \(([^)]+)\) and died."
    death_pattern2 = r"\[(.*?)\]\[info\] '([^']+)' \(([^)]+)\) was attacked by a wild '([^']+)' \(([^)]+)\) and died."
    
    helicopter_pattern = r"\[(.*?)\] \[info\] '([^']+)' \(([^)]+)\) has killed the Combat Helicopter at the OilRig(.*)"
    helicopter_pattern2 = r"\[(.*?)\]\[info\] '([^']+)' \(([^)]+)\) has killed the Combat Helicopter at the OilRig(.*)"

    # Parse Cheater
    if cheaters and ("*may be* a cheater" in line or "is a cheater! Reason:" in line):
        send_to_discord(f"**[WARN] may be a cheater!**", f"```{line}```")
        return

    # Parse Cheater Change SteamID
    if cheaters and ("is logging in with different steamid. Old steamid" in line):
        send_to_discord(f"[@here] **may be a cheater!**", f"```{line}```")
        return

    # Parse Chat
    chat_match = re.match(chat_pattern, line)
    if not chat_match:
        chat_match = re.match(chat_pattern2, line)

    if chat_match:
        timestamp = chat_match.group(1)
        channel = chat_match.group(2)
        nick = chat_match.group(3)
        platform_info = chat_match.group(4)
        is_admin = chat_match.group(5)
        message = chat_match.group(6)
        # Dont parse channels not from the list
        if channel and channel.lower() not in [ch.lower() for ch in ch_list]:
            return

        # Parse Chat Commands
        ingamecmd_list = ['!online']
        if message and any(message.lower().startswith(cmd.lower()) for cmd in ingamecmd_list):
            try:
                await cmd_online()
            except Exception as e:
                print(f"cmd_online ERROR: {e}")
            #return

        # Parse Commands
        if message and any(message.lower().startswith(cmd.lower()) for cmd in cmd_list):
            return
        # HIDE ADMIN PASS
        if message and '/adminpassword' in message.lower():
            message = '/AdminPassword Geted Admin Rights!!'
        # Извлечение платформы и идентификатора
        platform_id = None
        ip = None
        uid = None
        platform_parts = platform_info.split(',')
        for part in platform_parts:
            key_value = part.split('=')
            if len(key_value) > 1:
                key = key_value[0].strip()
                value = key_value[1].strip()
                if key.startswith('Steam') or key.startswith('Xbox') or key.startswith('Mac'):
                    platform_id = value
                elif key == 'IP':
                    ip = value
                elif key == 'UID':
                    uid = value
        # send to webhook
        send_to_discord(f"[{channel}] **{nick}**", message)

    # Parse Log(in/out)
    login_match = re.match(login_pattern, line)
    if not login_match:
        login_match = re.match(login_pattern2, line)
    if login_match:
        timestamp = login_match.group(1)
        nick = login_match.group(2)
        platform_info = login_match.group(3)
        action = login_match.group(4)
        platform_id = None
        ip = None
        uid = None
        platform_parts = platform_info.split(',')
        for part in platform_parts:
            key_value = part.split('=')
            if len(key_value) > 1:
                key = key_value[0].strip()
                value = key_value[1].strip()
                if key.startswith('Steam') or key.startswith('Xbox') or key.startswith('Mac') or key == 'UserId':
                    platform_id = value
                elif key == 'IP':
                    if value != 'Invalid':
                        ip = f"[{value}]"
                    else:
                        ip = ""
                elif key == 'UID':
                    uid = value
        # send to webhook
        if hide_personal_data:
            message = f"has logged **{action}**."
        else:
            message = f"[{platform_id}]{ip}: has logged **{action}**."
        send_to_discord(f"**{nick}**", message)

    # Parse death
    death_match = re.match(death_pattern, line)
    if not death_match:
        death_match = re.match(death_pattern2, line)
    if death_send and death_match:
        timestamp = death_match.group(1)
        nick = death_match.group(2)
        platform_info = death_match.group(3)
        enemy = death_match.group(4)
        weapon = death_match.group(5)
        platform_id = None
        ip = None
        uid = None
        platform_parts = platform_info.split(',')
        
        for part in platform_parts:
            key_value = part.split('=')
            if len(key_value) > 1:
                key = key_value[0].strip()
                value = key_value[1].strip()
                if key.startswith('Steam') or key.startswith('Xbox') or key.startswith('Mac'):
                    platform_id = value
                elif key == 'IP':
                    ip = value
                elif key == 'UID':
                    uid = value
        # send to webhook
        send_to_discord(f"**{nick}**", f"was attacked by a wild **{enemy}**:{weapon} and died.")

    # Parse Helicopter
    helicopter_match = re.match(helicopter_pattern, line)
    if not helicopter_match:
        helicopter_match = re.match(helicopter_pattern2, line)
    if death_send and helicopter_match:
        timestamp = helicopter_match.group(1)
        nick = helicopter_match.group(2)
        platform_info = helicopter_match.group(3)
        level = helicopter_match.group(4)
        platform_id = None
        ip = None
        uid = None
        platform_parts = platform_info.split(',')
        
        for part in platform_parts:
            key_value = part.split('=')
            if len(key_value) > 1:
                key = key_value[0].strip()
                value = key_value[1].strip()
                if key.startswith('Steam') or key.startswith('Xbox') or key.startswith('Mac'):
                    platform_id = value
                elif key == 'IP':
                    ip = value
                elif key == 'UID':
                    uid = value
        # send to webhook
        send_to_discord(f"**{nick}**", f"has killed the **Combat Helicopter** at the OilRig{level}")
    # END PARSE
    return None

def send_to_discord(nick, message):
    message_buffer.append((nick, message))

async def send_from_buffer_to_discord(nick, message):
    def escape_markdown(text):
        markdown_chars = ['\\', '*', '_', '~', '`', '>', '|']
        for char in markdown_chars:
            text = text.replace(char, '\\' + char)
        return text
    def truncate_message(text, max_length=2000):
        return text if len(text) <= max_length else text[:max_length-3] + '...'
    nick = escape_markdown(nick)
    message = escape_markdown(message)
    # Recovery BOLD **
    nick = nick.replace(r'\*\*', '**')
    message = message.replace(r'\*\*', '**')
    message = message.replace(r'\`\`\`', '```')
    message = truncate_message(message)
    message = f"{nick}: {message}"
    data = {"content": message}
    response = requests.post(webhook_url, json=data)
    if response.status_code != 204:
        print(f"Error sending message to Discord: {response.status_code} - {response.text}")


async def request_api(address):
    urls = [
        f"http://{address[0]}:{address[2]}/v1/api/info",
        f"http://{address[0]}:{address[2]}/v1/api/players",
        f"http://{address[0]}:{address[2]}/v1/api/settings",
        f"http://{address[0]}:{address[2]}/v1/api/metrics"
    ]
    
    base64enc = f"{username}:{password}"
    base64_bytes = base64.b64encode(base64enc.encode('utf-8'))
    base64_string = base64_bytes.decode('utf-8')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {base64_string}'
    }
    async with aiohttp.ClientSession() as session:
        results = []
        for url in urls:
            # async with session.post(url, headers=headers, data=payload) as response:
            # async with session.get(url, auth=aiohttp.BasicAuth(username, password)) as response:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    response_text = await response.text()
                    try:
                        data = json.loads(response_text)  # Попытка декодировать текст как JSON
                        results.append(data)
                    except json.JSONDecodeError:
                        print("Ошибка декодирования JSON. Полученные данные не являются корректным JSON.")
                        results.append(response_text)
                else:
                    print(f"Ошибка при запросе {url}: {response.status}")
                    results.append(None)

    info, players, settings, metrics = results
    return info, players, settings, metrics

async def get_info_restapi(address):
    try:
        info, players, settings, metrics = await request_api(address)
        return info, players, settings, metrics
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        channel = await bot.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)
        embed = disnake.Embed(
            title=f"**{address[0]}:{address[1]}**",
            colour=disnake.Colour.red(),
            description=f"offline or cannot answer",
        )
        await message.edit(content=f'Last update: {datetime.datetime.now().strftime("%H:%M")}', embed=embed)

async def get_info(address):
    try:
        info = a2s.info(address)
        players = a2s.players(address)
        rules = a2s.rules(address)
        '''
        # DEBUG
        print(f'\n=== Server Info ===')
        info_parts = f'{info}'.split(", ")
        for part in info_parts:
            print(f'    {part}')

        print(f'\n=== Players List ===')
        for player in players:
            normal_time = datetime.datetime.utcfromtimestamp(player.duration).strftime('%H:%M:%S')
            print(f"    {player.name}, Time: {normal_time}")

        print(f'\n=== Rules ===')
        for key, value in rules.items():
            print(f'    {key}: {value}')
        '''
        return info, players, rules
    except Exception as e:
        #print(f"An error occurred while getting server info: {e}")
        channel = await bot.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)
        embed = disnake.Embed(
            title=f"**{address[0]}:{address[1]}**",
            colour=disnake.Colour.red(),
            description=f"offline or cannot answer",
        )
        await message.edit(content=f'Last update: {datetime.datetime.now().strftime("%H:%M")}', embed=embed)


async def update_avatar_if_needed(bot, bot_name, bot_ava):
    # Проверяем, совпадает ли ссылка на аватар
    current_avatar_url = bot.user.avatar.url if bot.user.avatar else None
    if current_avatar_url != bot_ava:
        try:
            response = requests.get(bot_ava)
            response.raise_for_status()  # Проверка на ошибки HTTP
            data = response.content
            print("Avatar data retrieved successfully.")
            await bot.user.edit(avatar=data)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching avatar: {e}")

async def send_annonce(text):
    send_url = f"http://{address[0]}:{address[2]}/v1/api/announce"
    # Кодируем строку в Base64
    base64enc = f"{username}:{password}"
    base64_bytes = base64.b64encode(base64enc.encode('utf-8'))
    base64_string = base64_bytes.decode('utf-8')
    # Формируем заголовок
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {base64_string}'
    }
    text = unicodedata.normalize('NFKD', text).encode('utf-8', 'ignore').decode("utf-8")
    # Разбиваем текст на части длиной не более 127 символов
    messages = [text[i:i + 127] for i in range(0, len(text), 127)]
    
    try:
        async with aiohttp.ClientSession() as session:
            for message in messages:
                payload = json.dumps({"message": message})
                async with session.post(send_url, headers=headers, data=payload) as response:
                    if response.status != 200:
                        print(f"Failed annonce status: code {response.status}")
                        return response.status
        #print("Annonce sent successfully.")
        return True
    except Exception as e:
        print(f"Error sending message via REST API: {e}")
        return False

async def auto_annonces(current_index):
    global useonce
    annonces_list = {}
    with open(annonce_file, 'r', encoding='utf-8') as f:
        for index, line in enumerate(f):
            annonces_list[index] = line.strip()
    if not useonce:
        if annonces_list:  # Проверяем, что annonces_list не пустой
            current_index = random.randint(0, len(annonces_list) - 1)
            useonce = 1
        pass
    if annonces_list:
        text = annonces_list.get(current_index, '')
        print(f'Annonsing: {text}')
        await send_annonce(text)
        current_index += 1
    if current_index > len(annonces_list) - 1:
        current_index = 0
    return current_index

async def find_process():
    process_dir = log_directory.rstrip("\\PalDefender\\logs\\")
    process_name = "PalServer-Win64-Shipping-Cmd.exe"
    try:
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cwd']):
            try:
                if (proc.info['name'].lower() == process_name.lower() and 
                    proc.info['cwd'].lower() == process_dir.lower()):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

@tasks.loop(seconds=0.1)
async def message_sender():
    global send_interval
    try:
        #print(f"\rCurrent Buffer Limit: {len(message_buffer)}", end='')
        await asyncio.sleep(send_interval)
        if message_buffer:
            message = message_buffer.popleft()
            await send_from_buffer_to_discord(*message)
            if len(message_buffer) > BUFFER_LIMIT:
                send_interval += 1  # Увеличиваем интервал
            else:
                send_interval = max(0, send_interval - 0.1)  # Уменьшаем интервал, не ниже 0.1 секунды
    except Exception as e:
        print(f'\nmessage buffer ERROR >>: {e}')

@tasks.loop(seconds=90)
async def watch_dog():
    global proc_pid
    proc = await find_process()

    if proc is not None:
        if proc_pid is None or proc_pid != proc.info["pid"]:
            proc_pid = proc.info["pid"]
            print(f'Watch Dog start at PID: {proc_pid}')
    else:
        print("Watch Dog is OFF")
        return
    # KILL if not response
    failed_checks = 0
    for _ in range(2):
        try:
            await request_api(address)
            break
        except Exception as e:
            failed_checks += 1
            print(f'Watch Dog Server not response {failed_checks}')
            await asyncio.sleep(30)
    if failed_checks == 2 and proc is not None:
        print(f'Terminating process: {proc.info["name"]} (PID: {proc.info["pid"]})')
        send_to_discord(f"[@here] **WachDog**", 'SERVER NOT RESPONSE!!! FINISH HIM')
        proc.terminate()

@tasks.loop(seconds=2)
async def watch_logs():
    global current_file, file_position
    try:
        current_file = find_latest_file(log_directory)
        if current_file:
            file_position = os.path.getsize(current_file)
            print(f"watch log start at {current_file}")
            await watch_log_file(log_directory)
    except Exception as e:
        print(f'watch log ERROR >>: {e}')

@tasks.loop(seconds=2)
async def watch_cheat_logs():
    global cheat_current_file, cheat_file_position
    try:
        cheat_current_file = find_latest_cheat_file(cheat_log_directory)
        if cheat_current_file:
            cheat_file_position = os.path.getsize(cheat_current_file)
            print(f"watch cheat_log start at {cheat_current_file}")
            await watch_cheat_log_file(cheat_log_directory)
    except Exception as e:
        print(f'watch cheat_log ERROR >>: {e}')

@tasks.loop(seconds=int(annonce_time))
async def annonces():
    global current_index
    current_index = await auto_annonces(current_index)

@tasks.loop(seconds=int(update_time))
async def update_status():
    try:
        info, players, settings, metrics = await get_info_restapi(address)
        player_count = metrics["currentplayernum"]
        max_players = metrics["maxplayernum"]
        activity = disnake.Game(name=f"Online:{player_count}/{max_players}")
        await bot.change_presence(status=disnake.Status.online, activity=activity)

        if bot.user.name != bot_name:
            await bot.user.edit(username=bot_name)

        async def upd_msg():
            update_settings()
            uptime_seconds = metrics["uptime"]
            hours = f"{uptime_seconds // 3600:02}"
            minutes = f"{(uptime_seconds % 3600) // 60:02}"
            message = (
                f":earth_africa:Direct Link: **{settings['PublicIP']}:{settings['PublicPort']}**\n"
                f":map: Guid: **{info['worldguid']}**\n"
                f":green_circle: Online: **{player_count}/{max_players}**\n"
                f":film_frames: FPS: **{metrics['serverfps']}**\n"
                f":asterisk: Day: **{metrics['days']}**\n"
                f":timer: UpTime: **{hours}:{minutes}**\n"
                f":newspaper: Ver: **{info['version']}**\n"
                f"============ Server Settings ============\n"
                f"PVP:      **{settings['bIsPvP']}**\n"
                f"HardCore: **{settings['bHardcore']}**\n"
                f"Exp Rate: **{settings['ExpRate']}**\n"
                f"Drop Loot: **{settings['DeathPenalty']}**\n"
                f"Lost Pal: **{settings['bPalLost']}**\n"
                f"Decay Camps: **{settings['AutoResetGuildTimeNoOnlinePlayers']}h**\n"
                f"Base Camps: **{settings['BaseCampMaxNumInGuild']}**\n"
                f"Invaders: **{settings['bEnableInvaderEnemy']}**\n"
            )
            addition_embed = disnake.Embed(
                title=f"**{info['servername']}**",
                colour=disnake.Colour.green(),
                description=f"{message}",
            )
            try:
                channel = await bot.fetch_channel(channel_id)
                message = await channel.fetch_message(message_id)

                if message:
                    await message.edit(content=f'Last update: {datetime.datetime.now().strftime("%H:%M")}', embed=addition_embed)
            except Exception as e:
                print(f'Failed to fetch channel, message or server data. Maybe try /{command_prefex}_sendhere\n {e}')
        await upd_msg()
    except Exception as e:
        print(f'Cant connect to server, check ip and query/rest_api port \n ERROR >>: {e}')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}\nBot Shards: {bot.shard_count}')
    print('Invite bot link to discord (open in browser):\nhttps://discord.com/api/oauth2/authorize?client_id='+ str(bot.user.id) +'&permissions=8&scope=bot\n')
    try:
        await update_avatar_if_needed(bot, bot_name, bot_ava)
    except Exception as e:
        print(f'update_avatar ERROR >>: {e}')
    update_status.start()
    watch_dog.start()
    watch_logs.start()
    watch_cheat_logs.start()
    message_sender.start()
    annonces.start()

@bot.event
async def on_message(message):
    if message.author == client.user:		#отсеим свои сообщения
        return;
    if message.author.bot:
        return;
    if str(message.channel.id) != crosschat_id:
        return
    if message.content.startswith(''):
        text = ''
        text = f'{message.author.global_name}: { message.content}'
        #print(f"global_name: {message.author.global_name} text: {text}")
        await send_annonce(text)

#template admin commands
'''
@bot.slash_command(description="Add SteamID to Whitelist")
async def admin_cmd(ctx: disnake.ApplicationCommandInteraction, steamid: str):
    if ctx.author.guild_permissions.administrator:
        print(f'it admin command')
        try:
            await ctx.send(f'admin command try', ephemeral=True)
        except Exception as e:
            await ctx.send(f'ERROR Adding SteamID', ephemeral=True)
    else:
        await ctx.response.send_message("❌ You do not have permission to run this command.", ephemeral=True)
'''
#template users command
'''
@bot.slash_command(description="Show commands list")
async def help(ctx):
    await ctx.send('**==Support commands==**\n'
    f' Show commands list```{prefix}help```'
    f' Show server status```{prefix}moestatus```'
    f'\n **Need admin rights**\n'
    f' Auto send server status here```{prefix}sendhere```'
    f' Add server to listing```{prefix}serveradd adress:port name```',
    ephemeral=True
    )
'''

#commands
@bot.slash_command(name=f'{command_prefex}_sendhere', description="Set this channel to status")
async def sendhere(ctx: disnake.ApplicationCommandInteraction):
    if ctx.author.guild_permissions.administrator:
        try:
            guild = ctx.guild
            print(f'New channel id - {ctx.channel.id}')
            await write_cfg('botconfig', 'channel_id', str(ctx.channel.id))
            channel = await guild.fetch_channel(ctx.channel.id)
            await ctx.response.send_message(content=f'This message for auto updated the status', ephemeral=False)

            last_message = await ctx.channel.fetch_message(ctx.channel.last_message_id)
            print(f'New message id - {last_message.id}')
            await write_cfg('botconfig', 'message_id', str(last_message.id))
            update_settings()

        except Exception as e:
            await ctx.response.send_message(content='❌ An error occurred. Please try again later.', ephemeral=True)
            print(f'Error occurred during file write: {e}')
    else:
        await ctx.response.send_message(content='❌ You do not have permission to run this command.', ephemeral=True)

@bot.slash_command(name=f'{command_prefex}_lookhere', description="Look this channel to crosschat")
async def lookhere(ctx: disnake.ApplicationCommandInteraction):
    if ctx.author.guild_permissions.administrator:
        try:
            guild = ctx.guild
            print(f'New crosschat channel id - {ctx.channel.id}')
            await write_cfg('botconfig', 'crosschat_id', str(ctx.channel.id))
            channel = await guild.fetch_channel(ctx.channel.id)
            await ctx.response.send_message(content=f'This channel id [**{channel}**] for crosschat', ephemeral=False)
            update_settings()

        except Exception as e:
            await ctx.response.send_message(content='❌ An error occurred. Please try again later.', ephemeral=True)
            print(f'Error occurred during file write: {e}')
    else:
        await ctx.response.send_message(content='❌ You do not have permission to run this command.', ephemeral=True)

@bot.slash_command(name=f'{command_prefex}_annonce', description="Sent annonce to server")
async def annonce(ctx: disnake.ApplicationCommandInteraction, text: str):
    if ctx.user.guild_permissions.administrator:
        if text.strip() == "":
            await ctx.response.send_message(content='❌ Please type text to annonce', ephemeral=True)
            return
        try:
            answer = await send_annonce(text)  # Предполагается, что send_annonce - это функция, которая отправляет объявление
            #print(f'Annonce answer: {answer}')
            if answer is True:
                await ctx.response.send_message(content=':white_check_mark: Annonce OK', ephemeral=True)
            else:
                await ctx.response.send_message(content=f'❌ Error code {answer}: Annonce failed.', ephemeral=True)
        except Exception as e:
            await ctx.response.send_message(content='❌ Annonce an error occurred. Please try again later.', ephemeral=True)
            print(f'Annonce failed: {e}')
    else:
        await ctx.response.send_message(content='❌ You do not have permission to run this command.', ephemeral=True)


'''
@bot.slash_command(name=f'{command_prefex}_status', description="Request Servers status")
async def status(ctx: disnake.ApplicationCommandInteraction, ip: str = None, query: int = None):
    if ip is None:
        ip = address[0]
    try:
        if ip is not None and query is not None:
            info, players, rules = await get_info((f"{ip}", int(query)))
        else:
            info, players, rules = await get_info(address)
        message = (
            f":earth_africa: Direct Link: **{ip}:{info.port}**\n"
            f":link: Invite: **{rules.get('SU_s', 'N/A')}**\n"
            f":map: Map: **{info.map_name}**\n"
            f":green_circle: Online: **{info.player_count}/{info.max_players}**\n"
            f":asterisk: Pass: **{info.password_protected}**\n"
            f":newspaper: Ver: **{rules.get('NO_s', 'N/A')}**\n"
        )
        addition_embed = disnake.Embed(
            title=f"**{info.server_name}**",
            colour=disnake.Colour.green()
        )
        addition_embed.add_field(name="", value=message, inline=False)

        try:
            await ctx.response.send_message(embed=addition_embed, ephemeral=True)
        except Exception as e:
            await ctx.response.send_message(f'❌ Failed to send the status message. \nError:\n{e}', ephemeral=True)
            print(f'Error occurred during sending message: {e}')

    except Exception as e:
        await ctx.response.send_message(content='❌ An error occurred. Please try again later.', ephemeral=True)
        print(f'Error occurred during fetching server info: {e}')
'''

@bot.slash_command(name=f'{command_prefex}_players', description="Request Players status")
async def players(ctx: disnake.ApplicationCommandInteraction):
    try:
        info, players, settings, metrics = await request_api(address)
        #print(json.dumps(players, indent=4, ensure_ascii=False))

        index = "#"
        name = "Name"
        level = "Level"
        userId = "SteamID"
        ping = "Ping"
        table_header = f"|{index:<2}|{name:<18}|{level:<5}|{userId:<18}|{ping:<4}|\n"
        table_rows = ""
        for index, player in enumerate(players['players'], start=1):
            name = player['name']
            if not name.replace(" ", ""):
                name = player.get('accountName', '')
            level = player['level']
            userId = player['userId'].replace("steam_", "")
            ping = round(player['ping'])
            table_rows += f"|{index:<2}|{name:<18}|{level:<5}|{userId:<18}|{ping:<4}|\n"

        # Формируем сообщение с таблицей
        full_table = f"```\n{table_header}{table_rows}```"

        # Разделяем сообщение на части по 1500 символов
        max_length = 1700
        current_message = "```\n" + table_header  # Начинаем с заголовка

        for row in table_rows.splitlines(keepends=True):  # Сохраняем переносы строк
            if len(current_message) + len(row) > max_length:
                # Если добавление строки превышает лимит, отправляем текущее сообщение
                current_message += "```"  # Закрываем кодовый блок
                await ctx.send(current_message, ephemeral=True)
                current_message = "```\n" + table_header + row  # Начинаем новый блок с заголовком
            else:
                current_message += row  # Добавляем строку в текущее сообщение

        # Отправляем оставшийся текст, если он есть
        if current_message.strip() != "```\n" + table_header:
            current_message += "```"  # Закрываем кодовый блок
            await ctx.send(current_message, ephemeral=True)

    except Exception as e:
        await ctx.response.send_message(content='❌ An error occurred. Please try again later.', ephemeral=True)
        print(f'Error occurred during fetching server info: {e}')

@bot.slash_command(name=f'{command_prefex}_players_net', description="Request Players net status")
async def players_net(ctx: disnake.ApplicationCommandInteraction):
    if ctx.user.guild_permissions.administrator:
        try:
            info, players, settings, metrics = await request_api(address)
            index = "#"
            name = "Name"
            ping = "Ping"
            ip = "IP"
            table_header = f"|{index:<2}|{name:<18}|{ping:<4}|{ip:<16}|\n"
            table_rows = ""
            for index, player in enumerate(players['players'], start=1):
                name = player['name']
                if not name.replace(" ", ""):
                    name = player.get('accountName', '')
                ping = round(player['ping'])
                ip = player['ip']
                table_rows += f"|{index:<2}|{name:<18}|{ping:<4}|{ip:<16}|\n"
            # Формируем сообщение с таблицей
            full_table = f"```\n{table_header}{table_rows}```"

            # Разделяем сообщение на части по 1700 символов
            max_length = 1700
            current_message = "```\n" + table_header
            for row in table_rows.splitlines(keepends=True):
                if len(current_message) + len(row) > max_length:
                    current_message += "```"
                    await ctx.send(current_message, ephemeral=True)
                    current_message = "```\n" + table_header + row
                else:
                    current_message += row
            if current_message.strip() != "```\n" + table_header:
                current_message += "```"
                await ctx.send(current_message, ephemeral=True)
        except Exception as e:
            await ctx.response.send_message(content='❌ An error occurred. Please try again later.', ephemeral=True)
            print(f'Error occurred during fetching server info: {e}')
    else:
        await ctx.response.send_message(content='❌ You do not have permission to run this command.', ephemeral=True)

try:
    bot.run(token)
except disnake.errors.LoginFailure:
    print(' Improper token has been passed.\n Get valid app token https://discord.com/developers/applications/ \nscreenshot https://junger.zzux.com/webhook/guide/4.png')
except disnake.HTTPException:
    print(' HTTPException Discord API')
except disnake.ConnectionClosed:
    print(' ConnectionClosed Discord API')
except disnake.errors.PrivilegedIntentsRequired:
    print(' Privileged Intents Required\n See Privileged Gateway Intents https://discord.com/developers/applications/ \nscreenshot http://junger.zzux.com/webhook/guide/3.png')
