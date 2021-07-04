import traceback

import discord, aiohttp, json, io, re, fast_colorthief
from discord.ext import commands
from pygicord import Paginator
from yarl import URL

async def packages(query):
    async with aiohttp.ClientSession() as client:
        async with client.get(URL(f'https://api.parcility.co/db/search?q={query}'.replace(" ","%20"), encoded=True)) as resp:
            if resp.status == 200:
                response = json.loads(await resp.text())
                data = response.get('data')
    pages = []
    for object in data:
        embed = discord.Embed(color=discord.Color.blue())
        async with aiohttp.ClientSession() as client:
            async with client.get(URL(f'https://api.parcility.co/db/package/{object["Package"]}', encoded=True)) as resp:
                if resp.status == 200:
                    response = json.loads(await resp.text())
                    if response.get('code') == 200:
                        object["Price"] = response['data'].get("Price")
                        if object['Price'] != None:
                            embed.title = f"{discord.utils.escape_markdown(object['normalizedName'])} `{object['Price']}`"
                        else:
                            embed.title = f"{discord.utils.escape_markdown(object['normalizedName'])}"
                else:
                    embed.title = f"{discord.utils.escape_markdown(object['normalizedName'])}"
        try:
            embed.set_author(name=object['Author'] if object['Author'] else "Unknown")
            embed.add_field(name="Repo", value=f"[{object['repo']['label']}]({discord.utils.escape_markdown(object['repo']['url'])})" or "Unknown", inline=True)
            embed.add_field(name="Add Repo", value=f"[Click Here](https://sharerepo.stkc.win/?repo={discord.utils.escape_markdown(object['repo']['url'])})", inline=True)
            embed.add_field(name="More Info", value=f"[View Depiction]({discord.utils.escape_markdown(object['Depiction']).replace(' ','%20')})", inline=False)
            embed.set_thumbnail(url=object['Icon'])
        except Exception as e:
            print(e)
        embed.description = f"```\n{discord.utils.escape_markdown(object['Description'])}\n```"
        async with aiohttp.ClientSession() as client:
            async with client.get(URL(f'https://api.parcility.co/db/package/{object["Package"]}/sileo', encoded=True)) as resp:
                if resp.status == 200 :
                    response = json.loads(await resp.text())
                    if response.get('status') == True:
                        if 'headerImage' in response.get('data'):
                            if response.get('data')['headerImage'] != 'https://repo.dynastic.co/assets/img/default-sileo-banner.png':
                                embed.set_image(url=response.get('data')['headerImage'])
        embed.set_footer(text=object['Package'])
        pages.append(embed)
    return pages

class Parcility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        pattern = re.compile(r".*?(?<!\[)+\[\[((?!\s+)([\w+\ \&\+\-]){2,})\]\](?!\])+.*")
        if not pattern.match(message.content):
            return
        
        matches = pattern.findall(message.content)
        if not matches:
            return

        search_term = matches[0][0].replace('[[', '').replace(']]','')
        if not search_term:
            return

        ctx = await self.bot.get_context(message)

        try:
            async with ctx.typing():
                paginator = Paginator(pages = await packages(search_term), has_input = False)
                await paginator.start(ctx)
        except Exception:
            embed = discord.Embed(title="Not Found", color=discord.Color.red())
            embed.description = f'Sorry, I couldn\'t find any matching tweaks by that name.'
            await ctx.message.delete(delay=15)
            await ctx.send(embed=embed, delete_after=15)

    @commands.command(name='package', aliases=['tweak'])
    async def package(self, ctx, *, query):
        try:
            async with ctx.typing():
                paginator = Paginator(pages = await packages(query), has_input = False)
                await paginator.start(ctx)
        except UnboundLocalError:
            embed = discord.Embed(title="Not Found", color=discord.Color.red())
            embed.description = f'Sorry, I couldn\'t find any matching tweaks by that name.'
            await ctx.message.delete(delay=15)
            await ctx.send(embed=embed, delete_after=15)

    @commands.command(name='repo', aliases=['repository'])
    async def repo(self, ctx, *, query):
        try:
            async with ctx.typing():
                async with aiohttp.ClientSession() as client:
                    async with client.get(URL(f'https://api.parcility.co/db/repo/{query}'.replace(" ","%20"), encoded=True)) as resp:
                        if resp.status == 200:
                            response = json.loads(await resp.text())
                    try:
                        async with aiohttp.ClientSession() as client:
                            async with client.get(URL(response.get('data')['Icon'])) as img:
                                if img.status == 200:
                                    image_bytes = io.BytesIO(await img.read())
                                    rgb = fast_colorthief.get_dominant_color(image_bytes, quality=1)
                                    color = int(f'{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}', 16) 
                                else:
                                    color = discord.Color.blue()
                        embed = discord.Embed(color=color)
                        embed.title = f"{response.get('data')['Label']}"
                        try:
                            embed.set_author(name=f"{response.get('data')['package_count']} packages, {response.get('data')['section_count']} sections")
                            embed.add_field(name="URL", value=f"{response.get('data')['url']}" or f"{response.get('data')['url']}", inline=True)
                            embed.add_field(name="Add Repo", value=f"[Click Here](https://sharerepo.stkc.win/?repo={discord.utils.escape_markdown(response.get('data')['url'])})", inline=True)
                            embed.description = f"```\n{discord.utils.escape_markdown(response.get('data')['Description'])}\n```"
                            embed.set_thumbnail(url=response.get('data')['Icon'])
                        except Exception as e:
                            print(e)
                            traceback.print_exc()
                    except Exception as e:
                        print(e)
                        traceback.print_exc()
                await ctx.send(embed=embed)
        except Exception:
            embed = discord.Embed(title="Not Found", color=discord.Color.red())
            embed.description = f'Sorry, I couldn\'t find any matching repos by that name.'
            await ctx.message.delete(delay=15)
            await ctx.send(embed=embed, delete_after=15)

def setup(bot):
    bot.add_cog(Parcility(bot))
