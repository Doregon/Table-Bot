import discord, requests
from discord.ext import tasks, commands


class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status.start()

    @tasks.loop(seconds=9000)
    async def status(self):
        r = requests.get('https://api.parcility.co/db/repo/procursus')
        pkg = r.json()['data']['package_count']
        sec = r.json()['data']['section_count']
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{pkg} packages, {len(self.bot.guilds)} servers'))

    @status.before_loop
    async def before_status(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Status(bot))
