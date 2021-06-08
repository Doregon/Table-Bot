import discord, piracy_list
from discord.ext import commands


class Piracy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if any(substring in message.content.lower() for substring in piracy_list.repos) == True:
            embed = discord.Embed(title="**Dangerous Repo**", color=discord.Color.red())
            embed.description = f"You have linked a repository that is known to be harmful for reasons such as piracy, illegal content, or malware.\n\nRepositories marked as harmful often distribute software with unexpected effects, whether in the form of paid packages for free or other malicious packages. This can have lasting effects on your device and privacy, even sometimes affecting your ability to rejailbreak. We recommend that you exercise extreme caution to avoid harmful software."
            await message.channel.send(f'{message.author.mention}', embed=embed, allowed_mentions=discord.AllowedMentions(users=True))


def setup(bot):
    bot.add_cog(Piracy(bot))
