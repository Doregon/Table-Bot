import discord, aiohttp, json, utils.device_models
from discord.ext import commands
from pygicord import Paginator
from yarl import URL
from hurry.filesize import size, alternative

async def get_pages(query):
    try:
        async with aiohttp.ClientSession() as client:
            human_name = query.lower()
            async with client.get(URL(f'https://api.ipsw.me/v4/device/{utils.device_models.devices[human_name]}?type=ipsw', encoded=True)) as resp:
                if resp.status == 200:
                    response = json.loads(await resp.text())
    except Exception:
        async with aiohttp.ClientSession() as client:
            async with client.get(URL(f'https://api.ipsw.me/v4/device/{query.replace(" ","").replace("ipod","iPod").replace("macbookpro","MacBookPro").replace("adp","ADP").replace("imac","iMac").replace("macmini","Macmini").replace("macbookair","MacBookAir").replace("iphone","iPhone").replace("ipad","iPad").replace("appletv","AppleTV")}?type=ipsw', encoded=True)) as resp:
                if resp.status == 200:
                    response = json.loads(await resp.text())
    pages = []
    signed = ""
    color = None
    for object in response['firmwares']:
        if object['signed'] == True:
            signed = '```diff\n+ This firmware is currently being signed and can be used to restore or update.\n```'
            color = discord.Color.green()
        if object['signed'] == False:
            signed = '```diff\n- This firmware is not being signed and can not be used to restore or update.\n```'
            color = discord.Color.red()
        if object['releasedate'] == None:
            releasedate = 'Unknown'
        else:
            releasedate = object['releasedate']
        if object['sha1sum'] == None:
            sha1sum = 'Unknown'
        else:
            sha1sum = object['sha1sum']
        embed = discord.Embed(color=color)
        embed.title = f"{object['version']} `{object['buildid']}`"
        embed.set_author(name=response['name'])
        embed.add_field(name="Released on", value=f"`{releasedate}`", inline=True)
        embed.add_field(name="SHA1", value=f"`{sha1sum}`", inline=True)
        embed.add_field(name="Download", value=f"[{object['url'][:30]}...]({object['url']}) `{size(object['filesize'], system = alternative)}`", inline=False)
        embed.description = signed
        embed.set_footer(text=object['identifier'])
        pages.append(embed)
    return pages

class ipswme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='firmware', aliases=['device'])
    async def firmware(self, ctx, *, query):
        try:
            paginator = Paginator(pages = await get_pages(query), has_input = False)
            await paginator.start(ctx)
        except UnboundLocalError:
            embed = discord.Embed(title="Not Found", color=discord.Color.red())
            embed.description = f'Sorry, I couldn\'t find a matching device by that name. You can find these on https://ipsw.me/.'
            await ctx.message.delete(delay=15)
            await ctx.send(embed=embed, delete_after=15)

def setup(bot):
    bot.add_cog(ipswme(bot))
