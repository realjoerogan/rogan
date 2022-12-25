import discord
from discord.ext import commands


class automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
#
    @commands.Cog.listener()
    async def on_ready(self):
        print("automod cog loaded")
#
#     @commands.Cog.listener("on_message")
#     async def pings(self, message):
#         ctx = await self.bot.get_context(message)
#
#         if message.author.bot:
#             return
#
#         if "@here" in message.content.lower() or "@everyone" in message.content.lower():
#             channel = self.bot.get_channel(1032786294239154266)
#
#             embed = discord.Embed(title='Automated Warning', color=0xFFFFFF)
#             embed.add_field(name='User', value=message.author.mention, inline=True)
#             embed.add_field(name='Channel', value=message.channel.mention, inline=True)
#             embed.add_field(name=chr(173), value=chr(173))
#             embed.add_field(name='Warn Reason', value="Unnecessary Pings", inline=True)
#             embed.set_footer(text="Hobbes", icon_url=ctx.author.avatar_url)
#
#             await channel.send(embed=embed)
#
#             await self.bot.process_commands(message)
#         else:
#             return
#
#     @commands.Cog.listener("on_message")
#     async def profanity(self, message):
#         ctx = await self.bot.get_context(message)
#
#         if message.author.bot:
#             return
#
#         blocked_word_list = ['nigga', 'nigger', 'niggas', 'niggers', 'fuck', 'shit', 'pussy', 'pussys', 'bitch']
#
#         if any(blocked in message.content.lower() for blocked in blocked_word_list):
#             channel = self.bot.get_channel(1032786294239154266)
#
#             embed = discord.Embed(title='Automated Warning', color=0xFFFFFF)
#             embed.add_field(name='User', value=message.author.mention, inline=True)
#             embed.add_field(name='Channel', value=message.channel.mention, inline=True)
#             embed.add_field(name=chr(173), value=chr(173))
#             embed.add_field(name='Warn Reason', value="Profanity", inline=True)
#             embed.set_footer(text="Hobbes", icon_url=ctx.author.avatar_url)
#
#             await channel.send(embed=embed)
#
#             await self.bot.process_commands(message)
#         else:
#             return
#
#
def setup(bot):
    bot.add_cog(automod(bot))
