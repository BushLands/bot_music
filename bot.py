import discord
from discord.ext import commands

import config
import music

musicbot = commands.Bot(command_prefix = commands.when_mentioned_or('!'))
musicbot.add_cog(music.Music(musicbot))

@musicbot.event
async def on_ready():
	print('Logged on as {}!'.format(musicbot.user))

@musicbot.command('shutdown')
async def shutdown(ctx):
	await musicbot.logout()
	print('Logged out. Session closed.')

musicbot.run(config.TOKEN)