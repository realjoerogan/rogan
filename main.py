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
bot = commands.Bot(command_prefix='.')


global symbol1
global symbol2
global name1
global name2
global turn
turn = 0

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
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)


@bot.event
async def on_ready():
    for guild in bot.guilds:
        await guild.me.edit(nick=f"")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=("No Active Matches")))
    logger.warning(f"BotLaunched::")
    gsi.start()


@tasks.loop(seconds=1)
async def gsi():
    global matchEnd
    global t_name2
    global ct_name2

    x = requests.get('http://127.0.0.1:3000')
    if x.status_code == 200:
        data = x.json()
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
            for guild in bot.guilds:
                if guild.me.nick != (f"live on {map_name}"):
                    await guild.me.edit(nick=f"live on {map_name}")
            await bot.change_presence(activity=discord.Game(name=(f"{ct_name} {ct_score} - {t_score} {t_name}")))
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
                                title=(f"{ct_name.replace(ct_name2, 'counter terrorists')} {ct_score} - {t_score} {t_name.replace(t_name2, 'prob terrorists idk')}"),
                                timestamp=datetime.now().astimezone(pytz.timezone('US/Eastern'))
                            )
                            await channel.send(embed=embed)


        else:
            print("no map")
            matchEnd = 0
    else:
        print("no map")
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
async def rps(ctx, symbol):

    global turn
    global symbol1
    global symbol2
    global name1
    global name2

    if turn == 0:
        symbol1 = (ctx.message.content[5:])
        name1 = (ctx.message.author.display_name)
        await ctx.message.delete()
        turn = 1

    if (turn == 1):
        symbol2 = (ctx.message.content[5:])
        name2 = (ctx.message.author.display_name)
        await ctx.message.delete()
        embed = discord.Embed(
            title=f"{name1} vs {name2}",
            description=f"{name1} selected: **{symbol1}** \n {name2} selected: **{symbol2}**",
            # timestamp=datetime.now().astimezone(pytz.timezone('US/Eastern'))
        )
        # embed.set_footer(text=f"Hash: {ctx.message.__hash__}")
        # embed.set_footer(text=f"Hash: {ctx.message.__hash__}")
        await ctx.send(embed=embed)
        turn = 0

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

@bot.command()
@commands.has_permissions(manage_messages=True)
async def score(ctx, score1=None, score2=None, team1=None, team2=None):
    guild = ctx.guild
    embed = discord.Embed(
        title=f"{team1} {score1} - {score2} {team2}",
        timestamp=datetime.now().astimezone(pytz.timezone('US/Eastern'))
    )
    channel = discord.utils.get(ctx.guild.channels, name="Match Results")
    if not channel:
        channel = await guild.create_text_channel(name="Match Results")
    await channel.send(embed=embed)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=(f"{team1} {score1} - {score2} {team2}")))


@bot.command()
@commands.has_permissions(manage_messages=True)
async def tempmute(ctx, member: discord.Member, timed: DurationConverter, *, reason=None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=True)

    multiplier = {'s': 1, 'm': 60, 'h': 3600}
    amount, unit = timed

    await member.add_roles(mutedRole, reason=None)
    embed = discord.Embed(
        title="Member Muted",
        description=(f"Member {member.mention} was muted for {amount}{unit}, reason {reason}."),
        timestamp=datetime.now().astimezone(pytz.timezone('US/Eastern'))
    )
    await ctx.send(embed=embed)

    mute_time = amount * multiplier[unit]
    print(mute_time)
    await asyncio.sleep(amount * multiplier[unit])
    print("User Unmuted")

    await member.remove_roles(mutedRole)
    embed = discord.Embed(
        title="Member Unmuted",
        description=(f"Member {member.mention} has been unmuted, mute reason '{reason}.'"),
        timestamp=datetime.now().astimezone(pytz.timezone('US/Eastern'))
    )
    await ctx.send(embed=embed)

bot.run(token)
