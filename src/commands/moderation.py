import traceback

import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="clean", aliases=['purge', 'nuke'])
    @commands.guild_only()
    async def clean(self, ctx, limit: int):
        msg = 'message'
        await ctx.channel.purge(limit=limit+1)
        embed = discord.Embed(title="Success", color=discord.Color.green())
        embed.description = f'Deleted {limit} {msg if limit == 1 else "messages"}.'
        await ctx.send(embed=embed, delete_after=15)

    @commands.command(name="ban")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True) 
    async def ban(self, ctx, user: discord.Member, *, reason = None):
        if reason == None:
            reason = 'No reason provided'
        if user.id == ctx.guild.owner_id:
            embed = discord.Embed(title="No Permission", color=discord.Color.red())
            embed.description = f'You can\'t ban the server owner!'
            await ctx.message.delete(delay=15)
            await ctx.send(embed=embed, delete_after=15)
            return
        if user.top_role >= ctx.author.top_role:
            embed = discord.Embed(title="No Permission", color=discord.Color.red())
            embed.description = f'You don\'t have permission to ban that user.'
            await ctx.message.delete(delay=15)
            await ctx.send(embed=embed, delete_after=15)
            return
        await user.ban(reason=f'Banned by {ctx.author.name} ({ctx.author.id}) for "{reason}".')
        embed = discord.Embed(title="Banned", color=discord.Color.red())
        embed.description = f'Banned {user.name} for ``{reason}``.'
        await ctx.send(embed=embed, delete_after=15)

    @commands.command(name="unban")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True) 
    async def unban(self, ctx, id: int):
        await ctx.guild.unban(discord.Object(id=id), reason=f'Unbanned by {ctx.author.name} ({ctx.author.id}).')
        embed = discord.Embed(title="Unbanned", color=discord.Color.green())
        embed.description = f'Unbanned user.'
        await ctx.send(embed=embed, delete_after=15)

    @commands.command(name="kick")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True) 
    async def kick(self, ctx, user: discord.Member, *, reason = None):
        if reason == None:
            reason = 'No reason provided'
        if user.id == ctx.guild.owner_id:
            embed = discord.Embed(title="No Permission", color=discord.Color.red())
            embed.description = f'You can\'t kick the server owner!'
            await ctx.message.delete(delay=15)
            await ctx.send(embed=embed, delete_after=15)
            return
        if user.top_role >= ctx.author.top_role:
            embed = discord.Embed(title="No Permission", color=discord.Color.red())
            embed.description = f'You don\'t have permission to kick that user.'
            await ctx.message.delete(delay=15)
            await ctx.send(embed=embed, delete_after=15)
            return
        await user.kick(reason=f'Kicked by {ctx.author.name} ({ctx.author.id}) for "{reason}"".')
        embed = discord.Embed(title="Kicked", color=discord.Color.red())
        embed.description = f'Kicked {user.name} for ``{reason}``.'
        await ctx.send(embed=embed, delete_after=15)


def setup(bot):
    bot.add_cog(General(bot))
