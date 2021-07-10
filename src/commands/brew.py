import discord, aiohttp, json, re
from discord.ext import commands
from pygicord import Paginator
from yarl import URL

async def get_pages(query):
    async with aiohttp.ClientSession() as client:
        async with client.get(URL(f'https://formulae.brew.sh/api/formula.json', encoded=True)) as resp:
            if resp.status == 200:
                response = json.loads(await resp.text())
    pages = []
    for object in response:
        try:
            if query not in object['name']:
                continue
            embed = discord.Embed(color=discord.Color.blue())
            #embed.set_author(name=response['name'])
            embed.title = f"{object['name']} `{object['versions']['stable']}`"
            embed.description = f"```\n{discord.utils.escape_markdown(object['desc'])}\n```"
            embed.add_field(name="Homepage", value=f"{object['homepage']}", inline=True)
            embed.add_field(name="License", value=f"{object['license']}", inline=True)
            pages.append(embed)
        except Exception as e:
            await print(e)
    return pages

class brew(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        pattern = re.compile(r".*?(?<!\{)+\{\{((?!\s+)([\w+\ \&\+\-]){2,})\}\}(?!\})+.*")
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
                paginator = Paginator(pages = await get_pages(search_term), has_input = False)
                await paginator.start(ctx)
        except Exception:
            embed = discord.Embed(title="Not Found", color=discord.Color.red())
            embed.description = f'Sorry, I couldn\'t find any matching packages by that name.'
            await ctx.message.delete(delay=15)
            await ctx.send(embed=embed, delete_after=15)

    @commands.command(name='brew')
    async def brew(self, ctx, *, query):
        async with ctx.typing():
            try:
                paginator = Paginator(pages = await get_pages(query), has_input = False)
                await paginator.start(ctx)
            except UnboundLocalError:
                embed = discord.Embed(title="Not Found", color=discord.Color.red())
                embed.description = f'orry, I couldn\'t find any matching packages by that name.'
                await ctx.message.delete(delay=15)
                await ctx.send(embed=embed, delete_after=15)

def setup(bot):
    bot.add_cog(brew(bot))
