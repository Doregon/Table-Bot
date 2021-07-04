import traceback

import discord, config
from discord.ext import commands

"""This is a multi file example showcasing many features of the command extension and the use of cogs.
These are examples only and are not intended to be used as a fully functioning bot. Rather they should give you a basic
understanding and platform for creating your own bot.

These examples make use of Python 3.6.2 and the rewrite version on the lib.

For examples on cogs for the async version:
https://gist.github.com/leovoel/46cd89ed6a8f41fd09c5

Rewrite Documentation:
http://discordpy.readthedocs.io/en/rewrite/api.html

Rewrite Commands Documentation:
http://discordpy.readthedocs.io/en/rewrite/ext/commands/api.html

Familiarising yourself with the documentation will greatly help you in creating your bot and using cogs.
"""


def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    # Notice how you can use spaces in prefixes. Try to keep them simple though.
    prefixes = ['!']

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


# Below cogs represents our folder our cogs are in. Following is the file name. So 'meme.py' in cogs, would be cogs.meme
# Think of it like a dot path import
initial_extensions = ['commands.parcility',
                      'commands.ipswme',
                      'commands.general',
                      'commands.moderation',
                      'utils.status',
                      'utils.piracy']

bot = commands.Bot(command_prefix=get_prefix, help_command=None, allowed_mentions=discord.AllowedMentions(roles=False, users=False, everyone=False))

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)


@bot.event
async def on_ready():
    """http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready"""

    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')

    print(f'Successfully logged in and booted...!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.description = f'Command incomplete.'
        await ctx.message.delete(delay=15)
        await ctx.send(embed=embed, delete_after=15)
        traceback.print_exc()
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.description = f'Bad argument.'
        await ctx.message.delete(delay=15)
        await ctx.send(embed=embed, delete_after=15)
        traceback.print_exc()
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.description = f'You do not have permission!'
        await ctx.message.delete(delay=15)
        await ctx.send(embed=embed, delete_after=15)
        traceback.print_exc()
    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.description = f'The bot is missing permissions!'
        await ctx.message.delete(delay=15)
        await ctx.send(embed=embed, delete_after=15)       
    else:
        traceback.print_exc()

bot.run(config.bot_token, bot=True, reconnect=True)
