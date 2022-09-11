import sys
import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timezone
import pytz
import DiscordUtils
music = DiscordUtils.Music()
import logging
import random
import requests

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='.', intents=intents)


global symbol1
global symbol2
global name1
global name2
global turn
turn = 0

roundEnd = 0
matchEnd = 0
t_name2 = "T's"
ct_name2 = "CT's"


logger = logging.getLogger(__name__)


class DurationConverter(commands.Converter):
    async def convert(self, ctx, argument):
        amount = argument[:-1]
        unit = argument[-1]

        if amount.isdigit() and unit in ['s', 'm']:
            return (int(amount), unit)

        raise commands.BadArgument(message='Not a valid duration')


def read_token():
    with open("token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()


token = read_token()
client = discord.Client(intents=intents)


@bot.event
async def on_ready():
    for guild in bot.guilds:
        await guild.me.edit(nick=f"")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="No Active Matches"))
    logger.warning(f"BotLaunched::")
    gsi.start()


@tasks.loop(seconds=3)
async def gsi():
    global roundEnd
    global matchEnd
    global t_name2
    global ct_name2

    x = requests.get('http://127.0.0.1:8792')
    if x.status_code == 200:
        payload = x.json()
        sorted_data = []
        provider_messages = []

        # Pick some provider from the list...
        for providerid in payload.keys():
            sorted_data.append(payload[providerid])

        # sorted_data = sorted(sorted_data, key=lambda z: (z["provider"]["steamid"]))
        if len(sorted_data) > 0:
            provider_messages = sorted_data[0]

        if len(provider_messages) > 0:
            data = provider_messages[len(provider_messages) - 1]  # Get last (the most recent array element)
            if "map" in data.keys():
                ct_score = data['map']['team_ct']['score']
                t_score = data['map']['team_t']['score']
                if "name" in data['map']['team_ct'].keys():
                    ct_name = data['map']['team_ct']['name']
                else:
                    ct_name = "CT's"

                if "name" in data['map']['team_t'].keys():
                    t_name = data['map']['team_t']['name']
                else:
                    t_name = "T's"
                map_name = data['map']['name']

                print(f"Processing data for {data['provider']['steamid']} : {map_name} {ct_score} - {t_score}")
                for guild in bot.guilds:
                    is_workshop_name = map_name.split("/")
                    if len(is_workshop_name) > 1:
                        new_name = is_workshop_name[2]
                    else:
                        new_name = map_name
                    if data['map']['phase'] == "live":
                        if guild.me.nick != f"live on {new_name}":
                            await guild.me.edit(nick=f"live on {new_name}")
                    if data['map']['phase'] == "warmup":
                        if guild.me.nick != f"warmup on {new_name}":
                            await guild.me.edit(nick=f"warmup on {new_name}")
                await bot.change_presence(activity=discord.Game(name=f"{ct_name} {ct_score} - {t_score} {t_name}"))
                if "phase" in data['map'].keys():
                    gamePhase = data['map']['phase']
                    if gamePhase == "gameover":
                        if matchEnd == 0:
                            matchEnd = 1
                            print("game over")
                            for guild in bot.guilds:
                                scoreChannel = discord.utils.get(guild.channels, name="match-results")
                                if not scoreChannel:
                                    scoreChannel = await guild.create_text_channel(name="match-results")
                                channel = bot.get_channel(scoreChannel.id)
                                embed = discord.Embed(
                                    title=f"{ct_name.replace(ct_name2, 'counter terrorists')} {ct_score} - {t_score} {t_name.replace(t_name2, 'prob terrorists idk')}",
                                    timestamp=datetime.now().astimezone(pytz.timezone('US/Eastern'))
                                )
                                await channel.send(embed=embed)
            else:
                print("no map")
                matchEnd = 0
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=("No Active Matches")))
    else:
        print("no map")
        for guild in bot.guilds:
            if guild.me.nick != "":
                await guild.me.edit(nick="")
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=("No Active Matches")))
        matchEnd = 0
bot.run(token)

