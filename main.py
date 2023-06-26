import discord
from discord.ext import commands
import os
from help_cog import help_cog
from music_cog import music_cog
bot = commands.Bot(command_prefix="/")
 bot.run(os.getenv('TOKEN'))