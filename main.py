import discord
from discord.ext import commands
import os
from help_cog import help_cog
from music_cog import music_cog
from constants import Constants
Constants = Constants()
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

bot.remove_command("help")
h_cog = help_cog(bot)
bot.add_cog(h_cog)
bot.add_cog(music_cog(bot))
@bot.event
async def on_ready():
    await h_cog.on_ready()



bot.run(Constants.TOKEN)