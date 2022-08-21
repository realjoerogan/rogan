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
bot = commands.Bot(command_prefix = '.')

global symbol1
global symbol2
global name1
global name2
global turn
turn = 0

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
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=("No Recent Matches")))
    logger.warning(f"BotLaunched::")

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
async def jolomi(ctx):
    jaredQuotes = ['Beachs im black', 'POV jerad when a black man wont pick cotton']
    await ctx.send(f"Your Jolomi Quote is: ''{random.choice(jaredQuotes)}''"    )

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
async def gen(ctx):
    healthtypewhen = ['being targeted by sentry', 'playing pyro', 'submerged underwater', 'carrying the intelligence', 'taunting', 'disguised', 'cloaked', 'sapping a teleporter', 'sapping a dispenser', 'healing from dispenser']

    jumptypewhen = ['equipped', 'holstered', 'marked for dead', 'building a sentry', 'building a teleporter']

    firetypewhen = ['underwater', 'targeted by sentry', 'equipped', 'dead', 'playing sniper', 'below 3 health', 'rocket jumping']

    row1 = ['1', '2', '3', '4', '5', '6', '7']
    row2 = ['1', '2', '3', '4', '5', '6']
    nrow1 = ['1', '2', '3', '4', '5', '6']
    nrow2 = ['1', '2', '3', '4', '5', '6']
    nrow3 = ['1', '2', '3', '4', '5']
    damagetype = ['fire', 'explosive', 'emotional']
    damagetypewhen = ['in air', 'on fire', 'underwater', 'dead']
    accuracytypewhen = ['rocket jumping', 'taunting', 'on fire', 'dead', 'building a sentry', 'underwater']
    pos1 = random.choice(row1)
    pos2 = random.choice(row2)
    neg1 = random.choice(nrow1)
    neg2 = random.choice(nrow2)
    neg3 = random.choice(nrow3)

    if pos1 == '1':
        embed1 = (f"all minicrits are crits")

    if pos1 == '2':
        embed1 = (f"guaranteed crits when {random.choice(healthtypewhen)}")

    if pos1 == '3':
        embed1 = (f"kill everyone on map when {random.choice(firetypewhen)}")

    if pos1 == '4':
        embed1 = (f"every kill makes you immune to backstabs for {random.randint(4, 95)} seconds")

    if pos1 == '5':
        embed1 = (f"-{random.randint(32, 99)}% crit vulnerability when {random.choice(jumptypewhen)}")

    if pos1 == '6':
        embed1 = (f"allows you to steer bullets with your mouse")

    if pos1 == '7':
        embed1 = (f"{random.randint(4, 87)}% backstab immunity")

    if pos2 == '1':
        embed2 = (f"grants immunity to racism on kill")

    if pos2 == '2':
        embed2 = (f"allows you to crash the server on kill")

    if pos2 == '3':
        embed2 = (f"cloak meter multiples by {random.randint(3, 54)} each kill")

    if pos2 == '4':
        embed2 = (f"you can cyberbully scorch shot users")

    if pos2 == '5':
        embed2 = (f"+{random.randint(3, 54)}% damage each death")

    if pos2 == '6':
        embed2 = (f"headshots rip a hole in the space time continuum")

    if neg1 == '1':
        negembed1 = (f"+{random.randint(10, 99)}% {random.choice(damagetype)} damage vulnerability while {random.choice(damagetypewhen)}")

    if neg1 == '2':
        negembed1 = (f"you get cyberbullied")

    if neg1 == '3':
        negembed1 = (f"-{random.randint(10, 99)}% max health when {random.choice(healthtypewhen)}")

    if neg1 == '4':
        negembed1 = (f"-{random.randint(60, 99)}% jump height when {random.choice(jumptypewhen)}")

    if neg1 == '5':
        negembed1 = (f"-{random.randint(60, 99)}% fire rate when {random.choice(firetypewhen)}")

    if neg1 == '6':
        negembed1 = (f"you die after {random.randint(16, 74)} seconds")

    if neg2 == '1':
        negembed2 = (f"you die when healed")

    if neg2 == '2':
        negembed2 = (f"accuracy reduced by {random.randint(60,99)}% when {random.choice(accuracytypewhen)}")

    if neg2 == '3':
        negembed2 = (f"instantly die to the hot hand")

    if neg2 == '4':
        negembed2 = (f"you cant be healed by dispensers")

    if neg2 == '5':
        negembed2 = (f"-{random.randint(10, 99)}% heal rate when {random.choice(healthtypewhen)}")

    if neg2 == '6':
        negembed2 = (f"go into 3rd person for {random.randint(3, 54)} seconds on kill")

    if neg3 == '1':
        negembed3 = (f"you burn for {random.randint(50, 5432)}% longer")

    if neg3 == '2':
        negembed3 = (f"+{random.randint(4, 654)}% switch time when {random.choice(healthtypewhen)}")

    if neg3 == '3':
        negembed3 = (f"you are banned from getting rescue rangers")

    if neg3 == '4':
        negembed3 = (f"all incoming damage is multiplied by {random.randint(2, 6)}")

    if neg3 == '5':
        negembed3 = (f"-{random.randint(75, 99)}% max health when gunslinger is equipped")


    embed = discord.Embed(
        description=(f'**pros** \n {embed1} \n {embed2} \n **cons** \n {negembed1} \n {negembed2} \n {negembed3}')
    )
    await ctx.send(embed=embed)

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
    channel = bot.get_channel(946168492988698625)
    await channel.send(embed=embed)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=(f"{team1} {score1} - {score2} {team2}")))

@bot.command()
async def post(link=None, description=None):
    channel = bot.get_channel(967248569423761468)
    await channel.send(description)
    await channel.send(link)


@bot.command(description="Mutes the specified user.")
@commands.has_permissions(manage_messages=True)
async def tempmute(ctx, member: discord.Member, timed: DurationConverter, *, reason=None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="mute of shame")

    if not mutedRole:
        mutedRole = await guild.create_role(name="mute of shame")

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

# @bot.event
# async def on_message(message):
#     if not message.author.bot:
#         if 'delta' in message.content:
#             await message.delete()
#             await message.channel.send("Messaged Deleted; Subject Message: " + message.content)
#         elif 'rune' in message.content:
#             await message.delete()
#             await message.channel.send("Messaged Deleted; Subject Message: " + message.content)
#         elif 'undertale' in message.content:
#             await message.delete()
#             await message.channel.send("Messaged Deleted; Subject Message: " + message.content)
#         elif 'the' in message.content:
#             if 'game' in message.content:
#                 await message.delete()
#                 await message.channel.send("Messaged Deleted; Subject Message: " + message.content)
#         else:
#             await bot.process_commands(message)

bot.run(token)


