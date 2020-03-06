import youtube_dl
import discord
from discord.ext import commands

import config
from player import *

class Music(commands.Cog):
    '''
    This code is made from this one: https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d
    Chech it out, amazing stuff!
    '''
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command can\'t be used in DM channels.')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('An error occurred: {}'.format(str(error)))

    @commands.command(name='join', 
        aliases = ['запрыгивай', 'залетай'],
        invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        """Joins a voice channel."""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='summon')
    @commands.has_permissions(manage_guild=True)
    async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        """Summons the bot to a voice channel.

        If no channel was specified, it joins your channel.
        """

        if not channel and not ctx.author.voice:
            raise VoiceError('You are neither connected to a voice channel nor specified a channel to join.')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='leave', 
        aliases=['выйди', 'свали', 'исчезни'])
    @commands.has_permissions(manage_guild=True)
    async def _leave(self, ctx: commands.Context):
        """Clears the queue and leaves the voice channel."""

        if not ctx.voice_state.voice:
            return await ctx.send('Not connected to any voice channel.')

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(name='play',
        aliases=['бахни', 'сваргань', 'проиграй', 'сыграй'])
    async def _play(self, ctx: commands.Context, *, line: str):
        """Plays a song.

        If line is a YT url, will look for the source and try to play it.

        If line is a command, will play specific plot:
        -- something - will play Rick Ashley's song

        """

        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        try:
            line = config.PLAYLIST[line]
        except KeyError:
            pass

        async with ctx.typing():
            # create AudoiSource object
            try:
                source = await YTDLSource.create_source(ctx, line, loop=self.bot.loop)
            except YTDLError as e:
                await print('An error occurred while processing this request: {}'.format(str(e)))
            else:
                ctx.voice_state.voice.play(source)

                self.playerMsgId = ctx.message.id # save for further usage

                # add reactions for control
                await ctx.message.add_reaction('⏹️')
                await ctx.message.add_reaction('⏸️')

    @commands.command(name='resume')
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx: commands.Context):
        """Resumes a currently paused song."""

        if not ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()

            # add control reactions
            await ctx.message.clear_reaction('▶️')
            await ctx.message.add_reaction('⏸️')

    @commands.command(name='pause', aliases=['тормозни', 'пауза', 'заткнись'])
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        """Pauses the currently playing song."""

        if not ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()

            # add control reactions
            await ctx.message.clear_reaction('⏸️')
            await ctx.message.add_reaction('▶️')

    @commands.command(name='stop')
    @commands.has_permissions(manage_guild=True)
    async def _stop(self, ctx: commands.Context):
        """Stops playing song and clears the queue."""

        ctx.voice_state.songs.clear()

        if not ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()

            # remove control reactions
            await ctx.message.clear_reaction('⏸️')
            await ctx.message.clear_reaction('▶️')
            await ctx.message.clear_reaction('⏹️')
            await ctx.message.add_reaction('✅')

            # clear variable
            self.playerMsgId = None

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        control_table = {
            '▶️' : self._resume,
            '⏸️': self._pause,
            '⏹️': self._stop
        }

        if (reaction.message.id == self.playerMsgId) and not user.bot:
            try:
                action = control_table[reaction.emoji] # get command
            except KeyError: # if there is no matched command
                return
            else:
                ctx = await self.bot.get_context(reaction.message) # get context
                ctx.voice_state = self.get_voice_state(ctx)
                await ctx.invoke(action)