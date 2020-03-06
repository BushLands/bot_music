def setup():
	import discord
	from discord.ext import commands

	import config
	import music
	import general
	import rofl

	musicbot = commands.Bot(command_prefix = commands.when_mentioned_or('!'))
	musicbot.add_cog(music.Music(musicbot))
	musicbot.add_cog(general.General(musicbot))
	musicbot.add_cog(general.CommandErrorHandler(musicbot))
	musicbot.add_cog(rofl.Rofl(musicbot))
	
	musicbot.run(config.TOKEN)

setup()