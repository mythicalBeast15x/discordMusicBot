import discord
from discord.ext import commands

class help_cog(commands.Cog):
    def __init__(self, bot):

        self.bot = bot
        self.help_message = """
        ```
        General Commands:
        /help - displays all the available commands
        /play <keywords> - finds the song on youtube and plays it in current channel
        /queue - displays the current music queue
        /skip - skips the current song being played
        /clear - stops the music and clears the queue
        /leave - disconnects the bot form voice channel
        /pause - pauses the current song
        /resume - resumes the current song
        ```
        """
        self.text_channel_text = []

    """
    @commands.Cog.listener()
    async def on_ready(self):
        print("Connected to Discord")
    """
    @commands.Cog.listener()
    async def on_ready(self):
        print("Connected to Discord")
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_text.append(channel)
        await self.send_to_all(self.help_message)


    async def send_to_all(self, msg):
        for text_channel in self.text_channel_text:
            await text_channel.send(msg)
            #print('sent')

    @commands.command(name = "help", help="Displays all the available commands")
    async def help(self, ctx):
        await ctx.send(self.help_message)