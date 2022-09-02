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
    # channel = bot.get_channel(1014279089022062612)
    # embed = discord.Embed(
    #     title=f"update: v0.9.8",
    #     description=f"**whats new?**\nsupport for multiple game state integrations has been added, this means that anyone running the gsi in their config directly will have their matches processed through the bot. whoever starts their match first will have their match displayed in the nickname and status, and once the match ends/they leave the match that was second in the que will replace it.\n**what this this mean for my existing gsi?**\nnothing! i specifically wrote this all in a way that the game state integration itself isnt affected, there are no available updates for the gsi.\n**does this mean you can see all my data?**\nof course not! the only non-cs related thing i can view is your steamid64 (which you can find by going to someones profile)\n**ok but why should i care?**\nthe round data being collected from this (rounds won/lost, equipment cost, etc) is being fed into a maching learning algorithm that tries to calculate the chance that a team will win a round. even though csgo already does this, all it does is divide the equipment costs of both teams, while this accounts for how many rounds this team previously won with a similar equipment cost.\n**how do i join?**\nits really easy, just go to https://github.com/realjoerogan/rogangsi and click the green code button and press download zip. unzip it using 7zip or any alternatives and put .cfg file located in the unzipped folder into the cfg directory of your cs installation.",
    #     timestamp=datetime.now().astimezone(pytz.timezone('US/Eastern'))
    # )
    # await channel.send(embed=embed)
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


@bot.command()
async def s(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.toggle_song_loop()
    song.is_looping = False
    print(song.is_looping)
    print(player.queue)
    song2 = await player.remove_from_queue(int(0))
    await ctx.send(f'{song2.name} was skipped nooooooob')

@bot.command()
async def r(ctx, index):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.remove_from_queue(int(index))
    await ctx.send(f'{song.name} was removed from the queue lmao bald')


@bot.command()
async def p(ctx, *, url):
    player = music.get_player(guild_id=ctx.guild)
    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()
    if not player:
        player = music.create_player(ctx, ffmpeg_error_betterfix=True)
    if not ctx.voice_client.is_playing():
        await player.queue(url, search=True)
        try:
            song = await player.play()
        except:
            logger.error("Unexpected error:", sys.exc_info()[0])
            raise
        await ctx.send(f"hey baldthony '{song.name}' is now playing lmaooooooo baldthony")
    else:
        song = await player.queue(url, search=True)
        await ctx.send(f"'{song.name}' has been added to the queue lmao nooby fortnite player")



@bot.command()
async def l(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.toggle_song_loop()
    if song.is_looping:
        return await ctx.send("haha song is looping noobs")
    else:
        return await ctx.send("song isnt looping anymore bald")


@bot.command()
async def q(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    await ctx.send(f"{', '.join([song.name for song in player.current_queue()])}")

@bot.command()
async def np(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = player.now_playing()
    await ctx.send(song.name)
    
bot.run(token)

