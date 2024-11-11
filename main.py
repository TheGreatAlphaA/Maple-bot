
import sys

try:
    import asyncio
except ModuleNotFoundError:
    print("Please install asyncio. (pip install asyncio)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    import configparser
except ModuleNotFoundError:
    print("Please install configparser. (pip install configparser)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    import discord
    from discord.ext import commands
except ModuleNotFoundError:
    print("Please install discordpy. (pip install discord.py)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

# Import each of the cogs
# from <file name> import <class name>
from dnd_cog import dnd_cog
from help_cog import help_cog
from keyword_cog import keyword_cog
from music_cog import music_cog
from network_cog import network_cog
from skyblock_cog import skyblock_cog
from finance_cog import finance_cog
from reminders_cog import reminders_cog
from yt_notifications_cog import yt_notifications_cog


# Import .ini  configuration file
# This keeps passwords and api keys out of the code
config = configparser.ConfigParser()
config.read("info.ini")

# Enables permissions for the bot to access discord user information
intents = discord.Intents.all()

# Define the bot
bot = commands.Bot(
    command_prefix='/', 
    intents=intents
)

# Removes the default help command so that we can write out our own
bot.remove_command('help')


# ------------------------- Startup -----------------

async def main():
    async with bot:
        await bot.add_cog(dnd_cog(bot))
        await bot.add_cog(help_cog(bot))
        await bot.add_cog(keyword_cog(bot))
        await bot.add_cog(music_cog(bot))
        await bot.add_cog(network_cog(bot))
        await bot.add_cog(skyblock_cog(bot))
        await bot.add_cog(finance_cog(bot))
        await bot.add_cog(reminders_cog(bot))
        await bot.add_cog(yt_notifications_cog(bot))
        await bot.start(config['BOT']['discord_bot_token'])


# ------------------ Launch the bot ------------------------

try:
    print("Booting up Maple-Bot...")
    asyncio.run(main())
except Exception as e:
    print("Error attempting to launch bot: ", str(e))
    e = input("Press enter to close")
    sys.exit()
