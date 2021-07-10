import traceback

import discord
import re
import json
import aiohttp
import io
import urllib
from datetime import datetime
from discord.ext import commands, menus
from yarl import URL
import fast_colorthief

package_url = 'https://api.parcility.co/db/package/'
search_url = 'https://api.parcility.co/db/search?q='

async def package_request(package):
    async with aiohttp.ClientSession() as client:
        async with client.get(URL(f'{package_url}{package.get("Package")}', encoded=True)) as resp:
            if resp.status == 200:
                response = json.loads(await resp.text())
                if response.get('code') == 200:
                    package["Price"] = response['data'].get("Price")
            else:
                return None
    return package

async def search_request(search):
    async with aiohttp.ClientSession() as client:
        async with client.get(URL(f'{search_url}{urllib.parse.quote(search)}', encoded=True)) as resp:
            if resp.status == 200:
                response = json.loads(await resp.text())
                if response.get('code') == 404:
                    return []
                elif response.get('code') == 200:
                    return response.get('data')
                else:
                    return None
            else:
                return None

async def aiter(packages):
    for package in packages:
        p = await package_request(package)
        yield p

class TweakMenu(menus.AsyncIteratorPageSource):
    def __init__(self, response, length):
        super().__init__(response, per_page=1)
        self.page_length = length
        
    async def format_page(self, menu, entry):
        entry = await package_request(entry)
        pattern = re.compile(r"((http|https)\:\/\/)[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*")
        if (pattern.match(entry.get('Icon'))):
            async with aiohttp.ClientSession() as client:
                async with client.get(URL(entry.get('Icon'))) as img:
                    if img.status == 200:
                        image_bytes = io.BytesIO(await img.read())
                        rgb = fast_colorthief.get_dominant_color(image_bytes, quality=1)
                        color = int(f'{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}', 16) 
                    else:
                        color = discord.Color.blue()
        else:
            color = discord.Color.blue()
        if entry.get('Price') != None:
            embed = discord.Embed(title=f"{entry.get('Name')} `{entry.get('Price')}`", color=color)
        else:
            try:
                async with aiohttp.ClientSession() as client:
                        async with client.get(URL(f"{entry.get('repo').get('url')}{entry.get('builds')[-1].get('Filename')}")) as deb:
                            if deb.status != 200 and 'repo.dynastic.co' not in entry.get('repo').get('url'):
                                offline = "\n**⚠️ This package is unavailable and cannot be downloaded.**"
                            else:
                                offline = ""
            except:
                offline = ""
            embed = discord.Embed(title=f"{entry.get('Name')} `{entry.get('Version')}`{offline}", color=color)
        embed.set_author(name=entry.get('Author') if entry.get('Author') else "Unknown")
        embed.description = f"```\n{discord.utils.escape_markdown(entry.get('Description'))}\n```"
        embed.add_field(name="Repo", value=f"[{entry.get('repo').get('label')}]({entry.get('repo').get('url')})" or "Unknown", inline=True)
        if entry.get('repo').get('isDefault') == False:
            embed.add_field(name="Add Repo", value=f"[Click Here](https://sharerepo.stkc.win/?repo={entry.get('repo').get('url')})" or "Unknown", inline=True)
        if entry.get('Depiction') != None:
            embed.add_field(name="More Info", value=f"[View Depiction]({discord.utils.escape_markdown(entry.get('Depiction')).replace(' ','%20')})", inline=False)
        if entry.get('Depends') != None:
            embed.add_field(name="Dependencies", value=f"```xml\n{entry.get('Depends')}```\n", inline=False)
        if entry.get('builds')[-1].get('Filename') != None and entry.get('Price') == None and entry.get('repo').get('url').__contains__('repounclutter.coolstar.org') == False:
            embed.add_field(name="Download", value=f"[Debian Package]({entry.get('repo').get('url')}{entry.get('builds')[-1].get('Filename')})", inline=False)
        if (pattern.match(entry.get('Icon'))):
            embed.set_thumbnail(url=entry.get('Icon'))
        async with aiohttp.ClientSession() as client:
            async with client.get(URL(f'https://api.parcility.co/db/package/{entry.get("Package")}/sileo', encoded=True)) as resp:
                if resp.status == 200 :
                    response = json.loads(await resp.text())
                    if response.get('status') == True:
                        if 'headerImage' in response.get('data'):
                            if response.get('data')['headerImage'] != 'https://repo.dynastic.co/assets/img/default-sileo-banner.png':
                                embed.set_image(url=response.get('data')['headerImage'])
        embed.set_footer(text=discord.utils.escape_markdown(entry.get('Package'))+f" • Page {menu.current_page +1}/{self.page_length}" or "Unknown")
        return embed

        #embed = discord.Embed(title=entry.get('Name'), color=color)
        #embed.description = discord.utils.escape_markdown(entry.get('Description'))
        #embed.add_field(name="Author", value= discord.utils.escape_markdown(entry.get('Author') or "No author"), inline=True)
        #embed.add_field(name="Version", value= discord.utils.escape_markdown(entry.get('Version') or "No version"), inline=True)
        #embed.add_field(name="Price", value=entry.get("Price") or "Free")
        #embed.add_field(name="Repo", value=f"[{entry.get('repo').get('label')}]({entry.get('repo').get('url')})" or "No repo", inline=True)
        #if entry.get('repo').get('isDefault') == False:
        #    embed.add_field(name="Add Repo", value=f"[Click Here](https://sharerepo.stkc.win/?repo={entry.get('repo').get('url')})" or "No repo", inline=True)
        #embed.add_field(name="More Info", value=f"[View on Parcility](https://parcility.co/package/{entry.get('Package')}/{entry.get('repo').get('slug')})", inline=False)
        #if (pattern.match(entry.get('Icon'))):
        #    embed.set_thumbnail(url=entry.get('Icon'))
        #async with aiohttp.ClientSession() as client:
        #    async with client.get(URL(f'https://api.parcility.co/db/package/{entry.get("Package")}/sileo', encoded=True)) as resp:
        #        if resp.status == 200 :
        #            response = json.loads(await resp.text())
        #            if response.get('status') == True:
        #                if 'headerImage' in response.get('data'):
        #                    if response.get('data')['headerImage'] != 'https://repo.dynastic.co/assets/img/default-sileo-banner.png':
        #                        embed.set_image(url=response.get('data')['headerImage'])
        #embed.set_footer(text=discord.utils.escape_markdown(entry.get('Package'))+f" • Page {menu.current_page +1}/{self.page_length}" or "No package")
        #embed.timestamp = datetime.now()
        #return embed
    
class MenuPages(menus.MenuPages):
    async def update(self, payload):
        if self._can_remove_reactions:
            if payload.event_type == 'REACTION_ADD':
                await self.message.remove_reaction(payload.emoji, payload.member)
            elif payload.event_type == 'REACTION_REMOVE':
                return
        await super().update(payload)

class Parcility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repo_url = 'https://api.parcility.co/db/repo/'

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
        async with ctx.typing():
            response = await search_request(search_term)
        
        if response is None:
            embed = discord.Embed(title="Error", color=discord.Color.red())
            embed.description = f'An error occurred while searching for that tweak.'
            await ctx.message.delete(delay=15)
            await ctx.send(embed=embed, delete_after=15)
            return
        elif len(response) == 0:
            embed = discord.Embed(title="Not Found", color=discord.Color.red())
            embed.description = f'Sorry, I couldn\'t find any matching tweaks by that name.'
            await ctx.message.delete(delay=15)
            await ctx.send(embed=embed, delete_after=15)
            return
       
        menu = MenuPages(source=TweakMenu(aiter(response), len(response)), clear_reactions_after=True)
        await menu.start(ctx)

    @commands.command(name="package", aliases=['pkg'])
    @commands.guild_only()
    async def package(self, ctx, *, query):
        async with ctx.typing():
            response = await search_request(query)
            
            if response is None:
                embed = discord.Embed(title="Error", color=discord.Color.red())
                embed.description = f'An error occurred while searching for that tweak.'
                await ctx.message.delete(delay=15)
                await ctx.send(embed=embed, delete_after=15)
                return
            elif len(response) == 0:
                embed = discord.Embed(title="Not Found", color=discord.Color.red())
                embed.description = f'Sorry, I couldn\'t find any tweaks with that name.'
                await ctx.message.delete(delay=15)
                await ctx.send(embed=embed, delete_after=15)
                return
        
            menu = MenuPages(source=TweakMenu(aiter(response), len(response)), clear_reactions_after=True)
            await menu.start(ctx)

    @commands.command(name="repo")
    @commands.guild_only()
    async def repo(self, ctx, *, query):
        data = await self.repo_request(query)
        pattern = re.compile(r"((http|https)\:\/\/)[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*")

        if data is None:
            embed = discord.Embed(title="Error", color=discord.Color.red())
            embed.description = f'An error occurred while searching for that repo'
            await ctx.message.delete(delay=15)
            await ctx.send(embed=embed, delete_after=15)
            return
        elif len(data) == 0:
            embed = discord.Embed(title="Not Found", color=discord.Color.red())
            embed.description = f'Sorry, I couldn\'t find any matching repos by that name.'
            await ctx.message.delete(delay=15)
            await ctx.send(embed=embed, delete_after=15)
            return

        if (pattern.match(data.get('Icon'))):
            async with aiohttp.ClientSession() as client:
                async with client.get(URL(data.get('Icon'))) as img:
                    if img.status == 200:
                        image_bytes = io.BytesIO(await img.read())
                        rgb = fast_colorthief.get_dominant_color(image_bytes, quality=1)
                        color = int(f'{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}', 16) 
                    else:
                        color = discord.Color.blue()
        else:
            color = discord.Color.blue()
        embed = discord.Embed(title=data.get('Label'), color=color)
        embed.set_author(name=f"{data.get('package_count')} packages, {data.get('section_count')} sections")
        embed.description = f"```\n{discord.utils.escape_markdown(data.get('Description'))}\n```"
        embed.add_field(name="URL", value=f"{data.get('url')}" or f"{data.get('url')}", inline=True)
        if data.get('isDefault') == False:
            embed.add_field(name="Add Repo", value=f'[Click Here](https://sharerepo.stkc.win/?repo={data.get("url")})', inline=True)
        if (pattern.match(data.get('Icon'))):
            embed.set_thumbnail(url=data.get('Icon'))

        #embed = discord.Embed(title=data.get('Label'), color=color)
        #embed.description = data.get('Description')
        #embed.add_field(name="Packages", value=data.get('package_count'), inline=True)
        #embed.add_field(name="Sections", value=data.get('section_count'), inline=True)
        #embed.add_field(name="URL", value=data.get('url'), inline=False)
        #if data.get('isDefault') == False:
        #    embed.add_field(name="Add Repo", value=f'[Click Here](https://sharerepo.stkc.win/?repo={data.get("url")})', inline=True)
        #embed.add_field(name="More Info", value=f'[View on Parcility](https://parcility.co/{data.get("id")})', inline=True)
        #if (pattern.match(data.get('Icon'))):
        #    embed.set_thumbnail(url=data.get('Icon'))
        #if data.get('isDefault') == True:
        #    embed.set_footer(text='Default Repo')
        #embed.timestamp = datetime.now()

        await ctx.send(embed=embed)

    async def repo_request(self, repo):
        async with aiohttp.ClientSession() as client:
            async with client.get(f'{self.repo_url}{repo}') as resp:
                if resp.status == 200:
                    response = json.loads(await resp.text())
                    if response.get('code') == 404:
                        return []
                    elif response.get('code') == 200:
                        return response.get('data')
                    else:
                        return None
                else:
                    return None


def setup(bot):
    bot.add_cog(Parcility(bot))