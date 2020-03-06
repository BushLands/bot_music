import traceback
import sys
import discord
from discord.ext import commands
import random

class General(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print('Logged on as {}!'.format(self.bot.user))

	@commands.command('shutdown', aliases=['спать'])
	@commands.has_permissions(administrator=True)
	async def shutdown(self, ctx: commands.Context):
		await self.bot.logout()
		print('Logged out. Session closed.')

class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception
        """

        if hasattr(ctx.command, 'on_error'):
            return
        
        ignored = (commands.UserInputError)
        error = getattr(error, 'original', error)
        
        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send('Ты не мой сенпай, бака!')

        elif isinstance(error, commands.CommandNotFound):
        	return await ctx.send(random.choice(['Не поняла', 'Что сказал?', 'Переформулируй']))
            
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)