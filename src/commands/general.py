import traceback

import discord, datetime
from discord.ext import commands
import aiohttp, io
from yarl import URL
from colorthief import ColorThief

start_time = datetime.datetime.utcnow()

#class AppURLopener(urllib.request.FancyURLopener):
#    version = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.69 Safari/537.36"
#urllib._urlopener = AppURLopener()

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    @commands.guild_only()
    async def help(self, ctx):
        embed=discord.Embed(title="Help", color=discord.Color.green())
        embed.add_field(name="Parcility", value="`!package`\n`!repo`", inline=True)
        embed.add_field(name="General", value="`!jumbo`\n`!userinfo`\n`!ping`", inline=True)
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

    @commands.command(name='jumbo', aliases=['e','enlarge','emoji'])
    @commands.guild_only()
    async def jumbo(self, ctx, emoji: discord.PartialEmoji = None):
        if emoji is None:
            embed = discord.Embed(title="Error", color=discord.Color.red())
            embed.description = f'You must specify an emoji to enlarge!'
            await ctx.message.delete(delay=15)
            await ctx.send(embed=embed, delete_after=15)
        else:
            async with aiohttp.ClientSession() as client:
                async with client.get(URL(str(emoji.url))) as img:
                    image_bytes = buffer = io.BytesIO(await img.read())
                    cf = ColorThief(image_bytes)
                    dc = cf.get_color(quality=1)
                    rgb = dc
                    color = int(f'{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}', 16) 
                    embed = discord.Embed(title=emoji.name, color=color)
                    embed.set_image(url=emoji.url)
                    await ctx.send(embed=embed)

    @commands.command(name="info", aliases=['userinfo', 'ui'])
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
        async with aiohttp.ClientSession() as client:
            async with client.get(URL(str('https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024"'.format(user)))) as img:
                image_bytes = buffer = io.BytesIO(await img.read())
                cf = ColorThief(image_bytes)
                dc = cf.get_color(quality=1)
                rgb = dc
                color = int(f'{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}', 16) 
                embed=discord.Embed(title="User Info", description=f"<@{user.id}> ({user.id})", color=color)
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
