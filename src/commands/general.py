import traceback

import discord, datetime
from discord.ext import commands

start_time = datetime.datetime.utcnow()

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    @commands.guild_only()
    async def help(self, ctx):
        embed=discord.Embed(title="Help", color=discord.Color.green())
        embed.add_field(name="Parcility", value="`!package`\n`!repo`", inline=True)
        embed.add_field(name="General", value="`!userinfo`\n`!ping`", inline=True)
        embed.add_field(name="Moderation", value="`!kick`\n`!ban`\n`!unban`", inline=True)
        embed.add_field(name="GitHub", value='https://github.com/xstecky/Table-Bot', inline=False)
        embed.add_field(name="Discord", value='https://diatr.us/discord', inline=False)

        now = datetime.datetime.utcnow() # Timestamp of when uptime function is run
        delta = now - start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        if days:
            time_format = "{d} days, {h} hours, {m} minutes, and {s} seconds"
        else:
            time_format = "{h} hours, {m} minutes, and {s} seconds"
        uptime_stamp = time_format.format(d=days, h=hours, m=minutes, s=seconds)

        embed.set_footer(text=f'Online for {uptime_stamp}')
        await ctx.send(embed=embed)

    @commands.command(name="info", aliases=['userinfo'])
    @commands.guild_only()
    async def info(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        roles = ""
        if isinstance(user, discord.Member):
            for role in user.roles:
                if role != ctx.guild.default_role:
                    roles += role.mention + " "
        else:
            roles = "No roles."
            joined = f"User not in {ctx.guild.name}."
        embed=discord.Embed(title="User Info", description=f"<@{user.id}> ({user.id})", color=user.color)
        embed.add_field(name="Created On", value=user.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Joined On", value=user.joined_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Roles", value=roles if roles else "None", inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024".format(user))
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    @commands.guild_only()
    async def ping(self, ctx):
        lag = round(self.bot.latency*1000, 1)
        if lag >= 50:
            embed = discord.Embed(title="Pong!", color=discord.Color.red())
        if lag <= 49:
            embed = discord.Embed(title="Pong!", color=discord.Color.green())
        embed.description = f'Latency is {lag} ms.'
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
