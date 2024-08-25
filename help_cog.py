
import sys
import time
import random

try:
    import asyncio
except ModuleNotFoundError:
    print("Please install asyncio. (pip install asyncio)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    import discord
    from discord.ext import commands
except ModuleNotFoundError:
    print("Please install discordpy. (pip install discord.py)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")


# ------------------------- General Commands -----------------
class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = ""
        self.text_channel_list = []
        self.set_message()

    def set_message(self):
        self.help_message = f"""
```
General commands:
{self.bot.command_prefix}help - displays all the available commands
{self.bot.command_prefix}ping - sends a ping to test network latency
{self.bot.command_prefix}whoami - tells the user what their name is
{self.bot.command_prefix}whereami - tells the user what their status is
Music commands:
{self.bot.command_prefix}m q - displays the current music queue
{self.bot.command_prefix}m p <keywords> - plays a selected song from youtube
{self.bot.command_prefix}m skip - skips the current song being played
{self.bot.command_prefix}m clear - stops the music and clears the queue
{self.bot.command_prefix}m stop - disconnects the bot from the voice channel
{self.bot.command_prefix}m pause - pauses the current song being played or resumes if already paused
{self.bot.command_prefix}m resume - resumes playing the current song
{self.bot.command_prefix}m remove - removes last song from the queue
Dungeons & Dragons commands:
{self.bot.command_prefix}roll <dice> - rolls a dice. Use '+' to add additional dice or numbers. Example: 1d20+4d4+16
{self.bot.command_prefix}dnd spell <args> - casts a spell
{self.bot.command_prefix}dnd summon <creature> <amount> <action> [adv/dis] - summons a creature to perform an action
{self.bot.command_prefix}dnd colin <weapon name> [ammo type] [feats] [spells] [adv/dis] - perform an attack action as colin rahu
Hypixel Skyblock commands:
{self.bot.command_prefix}sb tracker <start/stop/status> - manages the skyblock ghast minion leaderboard tracker
{self.bot.command_prefix}sb collect - manages the skyblock ghast minion harvest reminder task
Keyword commands:
{self.bot.command_prefix}keyword add <keyword> - adds keywords to the keyword list
{self.bot.command_prefix}keyword remove <keyword> - removes keywords from the keyword list
{self.bot.command_prefix}keyword list - lists keywords on the keyword list
```
"""

    # ------------------------- Admin Commands -----------------

    # Changes discord presence to hint the bot's help command
    @commands.Cog.listener()
    async def on_ready(self):
        print("\nMaple-Bot v6.1\nCreated by Alpha_A [2021-2024]\n")
        await self.bot.change_presence(activity=discord.Game(f"{self.bot.command_prefix}help"))
        print(f"Bot Is Ready. Logged in as {self.bot.user}")

    # Command to force-exit the bot
    @commands.command(name="exit")
    @commands.is_owner()
    async def exit(self, ctx):
        sys.exit()

    # Command to sync the bot's command tree
    @commands.command(name="sync")
    @commands.is_owner()
    async def sync(self, ctx: commands.Context) -> None:
        await ctx.send("Starting global command sync. This may take a while...")
        # Sync the command tree
        synced = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(synced)} commands globally")

    # ------------------------- Generic Commands -----------------

    # Command to display the help text
    @commands.command(name="help", help="displays all the available commands")
    async def help(self, ctx):
        await ctx.send(self.help_message)

    # Command to send a ping to test network latency
    @commands.command(name="ping", help="sends a ping to test network latency")
    async def ping(self, ctx):
        # Get the start time
        pingtime = time.time()
        # Send a message to the channel
        pingms = await ctx.send("Pinging...")
        # Subtract the start time from the current time
        ping = time.time() - pingtime
        # Return the ping delay time
        await pingms.edit(content=":ping_pong:  time is `%.01f seconds`" % ping)

    # Command to tells the user what their name is
    @commands.command(name="whoami", help="tells the user what their name is")
    async def whoami(self, ctx):
        name = ctx.message.author.display_name
        true_name = ctx.message.author.name
        # Check if the user has the same name as the author
        if name == 'Alpha A':
            # If the user is the author, send a specical message
            if true_name == 'the_great_alpha_a':
                await ctx.send("Hi " + name + ". How are you doing today?")
            # If the user is not the author, but shares their name, send a special message
            else:
                await ctx.send("Your name is " + name + ". But... you know you can't fool me, right? I know you aren't really him.")
        # Otherwise, send the user their name
        else:
            await ctx.send("Your name is " + name + ".")

    # Command to tell the user what their status is
    @commands.command(name="whereami", help="tells the user what their status is")
    async def whereami(self, ctx):
        # Check if the user actually has a status set
        try:
            # If a status is set, set the variable to that status
            location = ctx.message.author.activities[0].name
        except IndexError:
            # If no status is set, set the variable to none
            location = None

        # If no status is set, send a generic message
        if location is None:
            await ctx.send(":thinking: It looks like you are currently somewhere on the internet.")
        # If a status is set, send the user their status
        else:
            await ctx.send(":earth_americas: It looks like you are currently " + location)

# ------------------------- Secret Commands -----------------

    # Command to make the bot say 'nya'
    @commands.command(name="nya")
    async def nya(self, ctx):
        await ctx.send("Nya!  (=^-ω-^=)")

    # Command to make the bot cringe
    @commands.command(name="cringe", aliases=['ಠ_ಠ', 'ಠಠ', 'ಠ', 'disapproval', 'disgust'])
    async def cringe(self, ctx):
        await ctx.send("Yikes.  ಠ_ಠ")

    # Command to make the bot say a jojo reference
    @commands.command(name="za_warudo", aliases=['the_world', "stop_time"])
    async def za_warudo(self, ctx):
        message = await ctx.send(content=":clock2: Za Warudo! Toki yo tomare!")
        await asyncio.sleep(1)
        await message.edit(content=":clock3: Za Warudo! Toki yo tomare!")
        await asyncio.sleep(1)
        await message.edit(content=":clock4: Za Warudo! Toki yo tomare!")
        await asyncio.sleep(1)
        await message.edit(content=":clock5: Za Warudo! Toki yo tomare!")
        await asyncio.sleep(1)
        await message.edit(content=":clock6: Za Warudo! Toki yo tomare!")
        await asyncio.sleep(1)
        await message.edit(content=":clock7: Five more seconds!")
        await asyncio.sleep(1)
        await message.edit(content=":clock8: Four more seconds...")
        await asyncio.sleep(1)
        await message.edit(content=":clock9: Three more seconds...")
        await asyncio.sleep(1)
        await message.edit(content=":clock10: Two more seconds...")
        await asyncio.sleep(1)
        await message.edit(content=":clock11: One more second...")
        await asyncio.sleep(1)
        await message.edit(content=":clock12: Zero. Toki wa ugokidasu.")
        await asyncio.sleep(5)
        await message.delete()

    # Command to make the bot send a subscribe link for Charlie Slimecicle
    @commands.command(name="subscribe_to_slimecicle", aliases=['slimecicle', 'subscribe_to_charlieslimecicle'])
    async def subscribe_to_slimecicle(self, ctx):
        x = random.randint(1, 20)
        if x < 10:
            await ctx.send("Subscribe to Charlie Slimecicle!\nhttps://www.youtube.com/user/Slimecicle?sub_confirmation=1")
        elif x < 20:
            await ctx.send("Subscribe to Charlie Slimecicle!\nhttps://www.twitch.tv/subs/slimecicle")
        elif x == 20:
            await ctx.send("Sbscrb t Chrl Slmccl!\nhttps://www.youtube.com/@Slmccl?sub_confirmation=1")
        else:
            await ctx.send("Subscribe to Charlie Slimecicle!\nhttps://www.youtube.com/user/Slimecicle?sub_confirmation=1")
