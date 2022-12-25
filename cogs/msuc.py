import os
import sys
import asyncio
import discord
from discord.ext import commands, tasks
import DiscordUtils
music = DiscordUtils.Music()

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("music cog loaded")

    @commands.Cog.listener()
    async def s(self, ctx):
        player = music.get_player(guild_id=ctx.guild.id)
        song = await player.toggle_song_loop()
        song.is_looping = False
        print(song.is_looping)
        print(player.queue)
        song2 = await player.remove_from_queue(int(0))
        await ctx.send(f'{song2.name} was skipped nooooooob')

    @commands.Cog.listener()
    async def r(self, ctx, index):
        player = music.get_player(guild_id=ctx.guild.id)
        song = await player.remove_from_queue(int(index))
        await ctx.send(f'{song.name} was removed from the queue lmao bald')

    @commands.Cog.listener()
    async def p(self, ctx, *, url):
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
                raise
            await ctx.send(f"hey baldthony '{song.name}' is now playing lmaooooooo baldthony")
        else:
            song = await player.queue(url, search=True)
            await ctx.send(f"'{song.name}' has been added to the queue lmao nooby fortnite player")

    @commands.Cog.listener()
    async def l(self, ctx):
        player = music.get_player(guild_id=ctx.guild.id)
        song = await player.toggle_song_loop()
        if song.is_looping:
            return await ctx.send("haha song is looping noobs")
        else:
            return await ctx.send("song isnt looping anymore bald")

    @commands.Cog.listener()
    async def q(self, ctx):
        player = music.get_player(guild_id=ctx.guild.id)
        await ctx.send(f"{', '.join([song.name for song in player.current_queue()])}")

    @commands.Cog.listener()
    async def np(self, ctx):
        player = music.get_player(guild_id=ctx.guild.id)
        song = player.now_playing()
        await ctx.send(song.name)


def setup(bot):
    bot.add_cog(music(bot))