import discord
from discord.ext import commands


class verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("verify cog loaded")

    @commands.Cog.listener("on_raw_reaction_add")
    async def verify_reaction(self, payload: discord.RawReactionActionEvent):
        channel = 1032793227096494181
        if payload.channel_id != channel:
            return
        if str(payload.emoji) == "<:hobbes:1032795437113024532>":
            member = discord.utils.get(payload.member.guild.roles, name="Members")
            await payload.member.add_roles(member)

    @commands.command()
    async def verify(self, ctx):
        embed = discord.Embed(title="generic title", description="click the thing", color=0xFFFFFF)

        sent = await ctx.send(embed=embed)
        await sent.add_reaction("<:hobbes:1032795437113024532>")


def setup(bot):
    bot.add_cog(verify(bot))
