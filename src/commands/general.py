import traceback

import discord, datetime, json, random
from discord.ext import commands
import aiohttp, io
from random import randint
from yarl import URL
from colorthief import ColorThief

start_time = datetime.datetime.utcnow()

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    @commands.guild_only()
    async def help(self, ctx):
        dm = ctx.author
        embed=discord.Embed(title="Help", color=discord.Color.green())
        embed.add_field(name="Parcility", value="`!package <query: package name>`\n`!repo <query: repo name>`", inline=False)
        embed.add_field(name="IPSW Downloads", value="`!firmware <device: identifier/name>`", inline=False)
        embed.add_field(name="General", value="`!jumbo <emoji: mention>`\n`!userinfo [user: mention/id]`\n`!pfp [user: mention/id]`\n`!ping`\n`!cat`\n`!catgirl`\n`!catboy`", inline=False)
        embed.add_field(name="Moderation", value="`!purge <amount: integer>`\n`!kick <user: mention/id>`\n`!ban <user: mention/id>`\n`!unban <user: id>`", inline=False)
        embed.add_field(name="GitHub", value='https://github.com/xstecky/Table-Bot', inline=True)
        embed.add_field(name="Invite", value='https://discord.com/api/oauth2/authorize?client_id=795276002552446996&permissions=2080762999&scope=bot%20applications.commands', inline=True)
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
        try:
            await dm.send(embed=embed)
            await ctx.send('📬')
        except:
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
                    image_bytes = io.BytesIO(await img.read())
                    cf = ColorThief(image_bytes)
                    dc = cf.get_color(quality=1)
                    rgb = dc
                    color = int(f'{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}', 16) 
                    embed = discord.Embed(title=emoji.name, color=color)
                    embed.set_image(url=emoji.url)
                    await ctx.send(embed=embed)

    @commands.command(name='avatar', aliases=['pfp'])
    @commands.guild_only()
    async def avatar(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        async with aiohttp.ClientSession() as client:
            async with client.get(URL(str("https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=16".format(user)))) as img:
                image_bytes = io.BytesIO(await img.read())
                cf = ColorThief(image_bytes)
                dc = cf.get_color(quality=1)
                rgb = dc
                color = int(f'{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}', 16) 
                embed = discord.Embed(title=user.display_name, color=color)
                if user.is_avatar_animated():
                    embed.add_field(name="View as", value=f'[gif]({"https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.gif?size=1024)".format(user)} [png]({"https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024)".format(user)} [jpg]({"https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.jpg?size=1024)".format(user)} [webp]({"https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.webp?size=1024)".format(user)}', inline=False)
                else:
                    embed.add_field(name="View as", value=f'[png]({"https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024)".format(user)} [jpg]({"https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.jpg?size=1024)".format(user)} [webp]({"https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.webp?size=1024)".format(user)}', inline=False)
                embed.set_image(url=user.avatar_url)
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
            async with client.get(URL(str("https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=16".format(user)))) as img:
                image_bytes = io.BytesIO(await img.read())
                cf = ColorThief(image_bytes)
                dc = cf.get_color(quality=1)
                rgb = dc
                color = int(f'{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}', 16) 
                embed=discord.Embed(title="User Info", description=f"{user.mention} ({user.id})", color=color)
                embed.add_field(name="Created On", value=user.created_at.strftime("%B %d, %Y"), inline=True)
                embed.add_field(name="Joined On", value=user.joined_at.strftime("%B %d, %Y"), inline=True)
                embed.add_field(name="Roles", value=roles if roles else "None", inline=False)
                embed.set_thumbnail(url=user.avatar_url)
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

    @commands.command(name="catgirl")
    @commands.guild_only()
    async def catgirl(self, ctx):
        async with aiohttp.ClientSession() as client:
            async with client.get(URL('https://nekos.life/api/v2/img/neko', encoded=True)) as resp:
                if resp.status == 200:
                    response = json.loads(await resp.text())
                    image = response.get('url')
                    async with aiohttp.ClientSession() as client:
                        async with client.get(URL(str(image))) as img:
                            image_bytes = io.BytesIO(await img.read())
                            cf = ColorThief(image_bytes)
                            dc = cf.get_color(quality=1)
                            rgb = dc
                            color = int(f'{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}', 16) 
                            embed = discord.Embed(color=color)
                            embed.set_image(url=image)
                            await ctx.send(embed=embed)

    @commands.command(name="catboy")
    @commands.guild_only()
    async def catboy(self, ctx):
        async with aiohttp.ClientSession() as client:
            async with client.get(URL('https://api.catboys.com/img', encoded=True)) as resp:
                if resp.status == 200:
                    response = json.loads(await resp.text())
                    image = response.get('url')
                    async with aiohttp.ClientSession() as client:
                        async with client.get(URL(str(image))) as img:
                            image_bytes = io.BytesIO(await img.read())
                            cf = ColorThief(image_bytes)
                            dc = cf.get_color(quality=1)
                            rgb = dc
                            color = int(f'{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}', 16) 
                            embed = discord.Embed(color=color)
                            embed.set_image(url=image)
                            await ctx.send(embed=embed)

    @commands.command(name="cat", aliases=['peepee'])
    @commands.guild_only()
    async def cat(self, ctx):
        photonumber = randint(1, 947)
        async with aiohttp.ClientSession() as client:
            async with client.get(URL(str(f"https://assets.stkc.win/botpeepee/{photonumber}.jpg"))) as img:
                image_bytes = io.BytesIO(await img.read())
                cf = ColorThief(image_bytes)
                dc = cf.get_color(quality=1)
                rgb = dc
                color = int(f'{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}', 16) 
                embed = discord.Embed(color=color)
                embed.set_image(url=f"https://assets.stkc.win/botpeepee/{photonumber}.jpg")
                await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(General(bot))
