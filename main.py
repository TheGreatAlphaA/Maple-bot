
import sys
import math
import time
import datetime
import random

import common_lib
import database_lib
import network_lib
import keyword_lib
import skyblock_lib
import dnd_lib


try:
    import asyncio
except ModuleNotFoundError:
    print("Please install asyncio. (pip install asyncio)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    import configparser
except ModuleNotFoundError:
    print("Please install asyncio. (pip install configparser)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    import discord
    from discord.ext import tasks, commands
except ModuleNotFoundError:
    print("Please install discordpy. (pip install discord.py)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")


# ---- importing .ini file
config = configparser.ConfigParser()
config.read("info.ini")

# Enables permissions for the bot to access discord user information
intents = discord.Intents.all()

# Change only the no_category default string
help_command = commands.DefaultHelpCommand(
    no_category="Commands"
)

# Define the bot
client = commands.Bot(
    command_prefix=commands.when_mentioned_or("m!"),
    help_command=help_command,
    intents=intents
)


# ------------------------- Startup -----------------


@client.event
async def on_ready():
    # Define the task
    global harvest_task

    # Create the task
    harvest_task = asyncio.create_task(SkyblockNextHarvest())

    # Start the tracker loop
    SkyblockTrackerLoop.start()

    # Start the tracker loop
    NetworkTrackerLoop.start()

    await client.change_presence(activity=discord.Game("m!help"))
    print(f"Bot Is Ready. Logged in as {client.user}")
    # start the task loop that checks global vars
    # for each account to check. Default none as set above

# ------------------------- Channel Definitions ---------------------------


# This is the list of channels that allow commands to be run from
command_channel = int(config['BOT']['bot_commands_channel'])

# This is the list of channels that allow commands to be run from
network_logs_channel = int(config['NETWORK']['network_logs_channel'])

# This is the channel that skyblock messages are sent to
sb_channel = int(config['SKYBLOCK']['skyblock_tracker_channel'])

# This is the deals channel
deals_channel = int(config['KEYWORD']['deals_channel'])

# This is where deals that match the keyword list are reported
keyword_channel = int(config['KEYWORD']['keyword_channel'])


# ------------------------- Role Definitions ---------------------------


# This is the role that gets notified when minion harvests are ready
sb_role = int(config['SKYBLOCK']['skyblock_role'])

# This is the role that gets notified when keywords are triggered
keyword_role = int(config['KEYWORD']['keyword_role'])


# ------------------------- Generic Functions -----------------


async def discord_message_pages(ctx, input_list_a, input_list_b):

    if input_list_b is None:
        # Function to page through each entry instead of displaying them all at once

        # How many tables per page
        per_page = 1
        # How many total pages there should be, based on the total entries divided by entires per page, rounded up
        pages = math.ceil(len(input_list_a) / per_page)
        # Current page, always start from page 1
        cur_page = 1
        # Initial chunk of entries
        chunk = input_list_a[:per_page]
        # Linebreak (needed to define to avoid breaking some things)
        linebreak = "\n"
        # Creates the message object
        message = await ctx.send("Page " + str(cur_page) + "/" + str(pages) + ":\n" + linebreak.join(chunk))
        # Adds arrow objects to the message
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        active = True

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
            # or you can use unicodes, respectively: "\u25c0" or "\u25b6"

        while active:
            try:
                reaction, user = await client.wait_for("reaction_add", timeout=60, check=check)
            
                # If forward arrow emote is selected, advance the page by 1
                if str(reaction.emoji) == "▶️" and cur_page != pages:
                    cur_page += 1
                    # Select the new content from the table
                    if cur_page != pages:
                        chunk = input_list_a[(cur_page - 1) * per_page:cur_page * per_page]
                    else:
                        chunk = input_list_a[(cur_page - 1) * per_page:]
                    # Edit the content and remove the reaction
                    await message.edit(content="Page " + str(cur_page) + "/" + str(pages) + ":\n" + linebreak.join(chunk))
                    await message.remove_reaction(reaction, user)

                # If back arrow emote is selected, return to the previous page
                elif str(reaction.emoji) == "◀️" and cur_page > 1:
                    cur_page -= 1
                    # Select the new content from the table
                    chunk = input_list_a[(cur_page - 1) * per_page:cur_page * per_page]
                    # Edit the content and remote the reaction
                    await message.edit(content="Page " + str(cur_page) + "/" + str(pages) + ":\n" + linebreak.join(chunk))
                    await message.remove_reaction(reaction, user)
            # After a while, remove the message
            except asyncio.TimeoutError:
                await message.delete()
                active = False

    else:
        # Function to page through each entry instead of displaying them all at once

        # How many tables per page
        per_page = 1
        # How many total pages there should be, based on the total entries divided by entires per page, rounded up
        pages = math.ceil(len(input_list_a) / per_page)
        # Current page, always start from page 1
        cur_page = 1
        # Initial chunk of entries
        chunk_a = input_list_a[:per_page]
        chunk_b = input_list_b[:per_page]
        # Linebreak (needed to define to avoid breaking some things)
        linebreak = "\n"
        # Creates the message object
        message_a = await ctx.send("Page " + str(cur_page) + "/" + str(pages) + ":\n" + linebreak.join(chunk_a))
        message_b = await ctx.send(linebreak.join(chunk_b))
        # Adds arrow objects to the message
        await message_b.add_reaction("◀️")
        await message_b.add_reaction("▶️")
        active = True

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
            # or you can use unicodes, respectively: "\u25c0" or "\u25b6"

        while active:
            try:
                reaction, user = await client.wait_for("reaction_add", timeout=60, check=check)
            
                # If forward arrow emote is selected, advance the page by 1
                if str(reaction.emoji) == "▶️" and cur_page != pages:
                    cur_page += 1
                    # Select the new content from the table
                    if cur_page != pages:
                        chunk_a = input_list_a[(cur_page - 1) * per_page:cur_page * per_page]
                        chunk_b = input_list_b[(cur_page - 1) * per_page:cur_page * per_page]
                    else:
                        chunk_a = input_list_a[(cur_page - 1) * per_page:]
                        chunk_b = input_list_b[(cur_page - 1) * per_page:]
                    # Edit the content and remove the reaction
                    await message_a.edit(content="Page " + str(cur_page) + "/" + str(pages) + ":\n" + linebreak.join(chunk_a))
                    await message_b.edit(content=linebreak.join(chunk_b))
                    await message_b.remove_reaction(reaction, user)

                # If back arrow emote is selected, return to the previous page
                elif str(reaction.emoji) == "◀️" and cur_page > 1:
                    cur_page -= 1
                    # Select the new content from the table
                    chunk_a = input_list_a[(cur_page - 1) * per_page:cur_page * per_page]
                    chunk_b = input_list_b[(cur_page - 1) * per_page:cur_page * per_page]
                    # Edit the content and remote the reaction
                    await message_a.edit(content="Page " + str(cur_page) + "/" + str(pages) + ":\n" + linebreak.join(chunk_a))
                    await message_b.edit(content=linebreak.join(chunk_b))
                    await message_b.remove_reaction(reaction, user)
            # After a while, remove the message
            except asyncio.TimeoutError:
                await message_a.delete()
                await message_b.delete()
                active = False


async def get_public_ip_address():
    try:
        old_ip_address = common_lib.read_from_txt("network/ip.txt")
        old_ip_address = old_ip_address[0]
    except IndexError:
        old_ip_address = None

    # Get the channel object from discord
    channel = client.get_channel(network_logs_channel)

    # Get the message contents
    new_ip_address = network_lib.get_ip_address()

    # If the tracker is run for the first time.
    if old_ip_address is None:
        old_ip_address = new_ip_address
        message = await channel.send(":satellite: Your public ip address has been recorded.")
        # Write the new ip to the file
        common_lib.write_to_txt_overwrite("network/ip.txt", str(new_ip_address))
    # If the public ip address is the same as before
    elif old_ip_address == new_ip_address:
        message = await channel.send(":satellite: Your public ip address is still the same.")
        await asyncio.sleep(900)
        await message.delete()
    # If the public ip address has changed
    else:
        message = await channel.send("||" + old_ip_address + " -> " + new_ip_address + "|| :warning: Your public ip address appears to have changed.")
        # Write the new ip to the file
        common_lib.write_to_txt_overwrite("network/ip.txt", str(new_ip_address))


# ------------------------- Bot commands ---------------------------


@client.command()
async def ping(ctx):
    """Ping Maple to see how long it takes her to ping back"""
    pingtime = time.time()
    pingms = await ctx.send("Pinging...")
    ping = time.time() - pingtime
    await pingms.edit(content=":ping_pong:  time is `%.01f seconds`" % ping)


@client.command()
async def whoami(ctx):
    """Ask Maple what your name is."""
    name = ctx.message.author.display_name
    await ctx.send("Your name is " + name)


@client.command()
async def whereami(ctx):
    """Ask Maple where she thinks you are."""
    try:
        location = ctx.message.author.activities[0].name
    except IndexError:
        location = None

    if location is None:
        await ctx.send(":thinking: It looks like you are currently somewhere on the internet.")
    else:
        await ctx.send(":earth_americas: It looks like you are currently " + location)


@client.command()
async def nya(ctx):
    """Have Maple put on her best cat impression! Nya!"""
    await ctx.send("Nya!  (=^-ω-^=)")


@client.command(aliases=['ಠ_ಠ', 'ಠಠ', 'ಠ', 'disapproval', 'disgust'])
async def cringe(ctx):
    """Have Maple show her disgust for your cringe-worthy ways."""
    await ctx.send("Yikes.  ಠ_ಠ")


@client.command(aliases=['the_world', "stop_time"])
async def za_warudo(ctx):
    """Though, since time has stopped for you, you can neither see nor feel it happen."""

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


@client.command(aliases=['slimecicle', 'subscribe_to_charlieslimecicle'])
async def subscribe_to_slimecicle(ctx):
    """Subscribe to Charlie Slimecicle."""
    x = random.randint(1, 20)
    if x < 10:
        await ctx.send("Subscribe to Charlie Slimecicle!\nhttps://www.youtube.com/user/Slimecicle?sub_confirmation=1")
    elif x < 20:
        await ctx.send("Subscribe to Charlie Slimecicle!\nhttps://www.twitch.tv/subs/slimecicle")
    elif x == 20:
        await ctx.send("Sbscrb t Chrl Slmccl!\nhttps://www.youtube.com/@Slmccl?sub_confirmation=1")
    else:
        await ctx.send("Subscribe to Charlie Slimecicle!\nhttps://www.youtube.com/user/Slimecicle?sub_confirmation=1")


"""
@client.command(aliases=['kys', 'kill', 'die', 'murder'])
@commands.has_permissions(kick_members=True)
async def kick(ctx):
    await user.kick()
    await ctx.send(f"**{user}** has been kicked for **no reason**.")
"""

# ------------------------- Skyblock ---------------------------


@client.command()
async def skyblock(ctx, subcommand=None, arg1=None):
    """Starts the skyblock island checker"""
    if not subcommand:
        await ctx.send("Please provide a valid subcommand.\nHere is the subcommand list for the 'skyblock' command:\n    'tracker': Starts the skyblock ghast tear tracker.\n    'tracker status': Checks on the status of the tracker.\n    'tracker test': Sends a test message from the skyblock tracker.")

    # Starts the skyblock island tracker
    elif subcommand.lower() == "tracker":
        # If no arguments provided, check the status
        if not arg1:

            # If the loop is not running
            if SkyblockTrackerLoop.is_running() is False:

                # Start the tracking loop
                try: 
                    SkyblockTrackerLoop.start()
                except Exception as e:
                    print("Error attempting to launch the skyblock tracker: ", str(e))
                    await ctx.send("Oh no! I can't start the skyblock tracker right now...\nHere is the error: " + str(e))

                # Check if the loop actually started
                try:
                    if SkyblockTrackerLoop.is_running() is True:
                        await ctx.send("Process started successfully!")
                    else:
                        await ctx.send("Oh no! I wasn't able to start the skyblock tracker.")
                except Exception as e:
                    print("Error attempting to launch the skyblock tracker: ", str(e))
                    await ctx.send("Oh no! I can't start the skyblock tracker right now...\nHere is the error: " + str(e))
                return

            # If the loop is running
            elif SkyblockTrackerLoop.is_running() is True:

                # Stop the loop
                try:
                    SkyblockTrackerLoop.cancel()
                except Exception as e:
                    print("Error attempting to stop the skyblock tracker: ", str(e))
                    await ctx.send("Oh no! I can't stop the skyblock tracker right now...\nHere is the error: " + str(e))

                # Check if the loop actually stopped
                try:
                    if SkyblockTrackerLoop.is_running() is False:
                        await ctx.send("Process haulted successfully!")
                    else:
                        await ctx.send("Oh no! I wasn't able to stop the skyblock tracker.")
                except Exception as e:
                    print("Error attempting to stop the skyblock tracker: ", str(e))
                    await ctx.send("Oh no! I can't stop the skyblock tracker right now...\nHere is the error: " + str(e))
                return

        if arg1 == "status":
            try:
                if SkyblockTrackerLoop.is_running() is True:
                    await ctx.send("The Skyblock Tracker is currently running.")
                else:
                    await ctx.send("The Skyblock Tracker is currently offline. Use 'm!skyblock tracker' to start the tracker")
            except Exception as e:
                await ctx.send("Oh no! I'm not able to check the status of the skyblock tracker right now...\nHere is the error: " + str(e))
                return
        elif arg1 == "test":
            try:
                # Get the channel object from discord
                channel = client.get_channel(sb_channel)

                # Get the message contents
                msg = await skyblock_lib.SkyblockTracker()

                # Sends the final report to the tracker channel
                await channel.send(msg)

                await ctx.send("Sent a test message to the tracker channel!")

            except Exception as e:
                await ctx.send("Oh no! I'm not able to use the skyblock tracker tester right now...\nHere is the error: " + str(e))
                return

    # Starts the skyblock island tracker
    elif subcommand.lower() == "collect":
        try:
            # Define the task
            global harvest_task

            # If task already exists, cancel it
            if harvest_task in asyncio.all_tasks():
                harvest_task.cancel()

            # Get the channel object from discord
            channel = client.get_channel(sb_channel)

            last_harvest = common_lib.read_from_txt("skyblock/last_harvest.txt")
            next_harvest = common_lib.read_from_txt("skyblock/next_harvest.txt")

            # Get the date and time of the last recorded harvest
            past_harvest = datetime.datetime.strptime(last_harvest[0], "%Y-%m-%d %H:%M:%S")
            # Get the current date and time
            present_harvest = datetime.datetime.now().replace(microsecond=0)
            # Get the previously predicted best harvest time
            max_harvest = datetime.datetime.strptime(next_harvest[0], "%Y-%m-%d %H:%M:%S")

            # Check if Derpy is mayor
            mayor = await skyblock_lib.SkyblockMayorChecker()
            if mayor == "Derpy":
                # Calculate the new best harvest time
                future_harvest = present_harvest + datetime.timedelta(minutes=3957)
            else:
                # Calculate the new best harvest time
                future_harvest = present_harvest + datetime.timedelta(minutes=7915)

            # Calculate how full the minions were when harvested
            total_harvest_time_left = present_harvest - past_harvest
            total_harvest_time = max_harvest - past_harvest
            percent_completed = math.trunc((total_harvest_time_left / total_harvest_time) * 100)

            # Send a message to the Skyblock channel
            await channel.send("Collected Ghast Minions. Woohoo! Storage filled at aproximately " + str(percent_completed) + " percent.")

            # Update the past harvest value
            common_lib.write_to_txt_overwrite("skyblock/last_harvest.txt", str(present_harvest))

            # Update the predicted best harvest time
            common_lib.write_to_txt_overwrite("skyblock/next_harvest.txt", str(future_harvest))

            # Create the task
            harvest_task = asyncio.create_task(SkyblockNextHarvest())

        except Exception as e:
            print("Exception occured while collecting: ", str(e))
            return

    else:
        await ctx.send("I wasn't able to process that subcommand.\nHere is the subcommand list for the 'skyblock' command:\n    'tracker': Starts the skyblock ghast tear tracker.\n    'tracker status': Checks on the status of the tracker.\n    'tracker test': Sends a test message from the skyblock tracker.")


# ------------------------- DND ---------------------------


@client.command()
async def roll(ctx, arg1=None):
    """Roll a dice. Use '+' to add additional dice or numbers. Example: 1d20+4d4+16"""
    diceInput = []
    diceOutput = []
    result = 0

    if not arg1:
        await ctx.send("Please specify a dice to roll. Example: m!roll 1d20")

    if arg1:
        diceInput = arg1.split("+")
        for x in diceInput:
            diceOutput.append(await dnd_lib.diceRoll(x))

        for y in diceOutput:

            for value in y:

                if value == "E":  # Error
                    await ctx.send("Oops, I couldn't read that. Sorry! >_<\nYou can try again, just make sure you entered everything right.")
                    return

                elif value == "O":  # Overflow
                    await ctx.send("Whoa, that's a lot of dice! I only have about 200 dice I can use at once.\nYou can try again, just use fewer dice.")
                    return

                elif value == "S":  # Size Overflow
                    await ctx.send("Uhh, I don't think they make dice that big. The largest dice I have is a D1000.\nYou can try again, just use smaller dice.")
                    return

                else:
                    result = result + value

        # Flavor text for special d20 rolls
        if arg1 == "1d20" and result == 20:
            await ctx.send(":sparkles: CRITICAL!! For " + arg1 + ", you rolled: " + str(result))
        elif arg1 == "1d20" and result == 1:
            await ctx.send(":skull: FAILURE! For " + arg1 + ", you rolled: " + str(result))

        # Flavor text for d2 rolls
        elif arg1 == "1d2" and result == 1:
            await ctx.send(":coin: For the coin flip, you landed on Heads!")
        elif arg1 == "1d2" and result == 2:
            await ctx.send(":coin: For the coin flip, you landed on Tails!")

        # Don't show the result twice if there is only one dice
        elif "+" not in arg1 and arg1[0] == "1":
            await ctx.send(":game_die: For " + arg1 + ", you rolled: " + str(result))
        else:
            await ctx.send(":game_die: For " + arg1 + ", you rolled: " + str(diceOutput) + "\n= " + str(result))


@client.command()
async def spell(ctx, spell=None, spell_level=None, arg1=None, arg2=None, arg3=None, arg4=None):
    """Casts a spell. Use m!spell to get a list of avaliable spells."""
    summoning_spells = [
        "conjure_animals",
        "conjure_woodland_beings",
        "conjure_minor_elementals",
        "conjure_elemental",
        "conjure_fey",
        "conjure_celestial"
    ]

    if spell is None:
        msg = """Here is a list of spells:
=== Summoning Spells ===
Usage: m!spell <spell name> <spell level> <creature name> <creature amount> <creature action> <adv / dis>
    m!spell conjure_animals 3 Velociraptor 8 Multiattack adv
    m!spell conjure_woodland_beings 4
    m!spell conjure_minor_elementals 4
    m!spell conjure_elemental 5
    m!spell conjure_fey 6
    m!spell conjure_celestial 6 """

        await ctx.send(msg)

    # Use a summoning spell
    elif spell in summoning_spells:
        creature_name = arg1
        creature_amount = arg2
        creature_action = arg3
        adv = arg4

        # If spell level is not int, try setting it as the creature name
        if creature_name is None:
            try:
                spell_level = int(spell_level)
            except TypeError:
                creature_name = spell_level

        # If no creature provided, list all valid creatures for that spell
        if creature_name is None:

            # Querys the database and generates a list of messages and tables
            tables = await database_lib.dnd_SummonCreature(spell, spell_level, creature_name, creature_amount, creature_action, adv)

            # Querys the database for more informatio
            descriptions = None  # await database_lib.dnd_CreatureDescriptions(spell)

            # Creates a function that pages through all the entries
            await discord_message_pages(ctx, tables, descriptions)

        elif creature_action is None:
            
            # Querys the database and generates a list of messages and tables
            tables = await database_lib.dnd_SummonCreature(spell, spell_level, creature_name, creature_amount, creature_action, adv)

            # Querys the database for more informatio
            descriptions = None  # await database_lib.dnd_CreatureDescriptions(spell)

            # Creates a function that pages through all the entries
            await discord_message_pages(ctx, tables, descriptions)

        else:
            
            # Querys the database and generates a list of messages and tables
            tables = await database_lib.dnd_SummonCreature(spell, spell_level, creature_name, creature_amount, creature_action, adv)

            for msg in tables:
                await ctx.send(msg)

    # If no valid spell provided
    else:
        msg = "That isn't a valid spell. Use m!spell to get a list of valid spells."
        await ctx.send(msg)


@client.command()
async def summon(ctx, creature_name=None, creature_amount=None, creature_action=None, adv=None):
    """Casts a summoning spell. Allows you to quickly summon any number of any creatures in the database."""

    # If no creature provided, list all valid creatures for that spell
    if creature_name is None:

        # Querys the database and generates a list of messages and tables
        tables = await database_lib.dnd_SummonCreature("override", "10", creature_name, creature_amount, creature_action, adv)

        # Querys the database for more informatio
        descriptions = None  # await database_lib.dnd_CreatureDescriptions(spell)

        # Creates a function that pages through all the entries
        await discord_message_pages(ctx, tables, descriptions)

    elif creature_action is None:
        
        # Querys the database and generates a list of messages and tables
        tables = await database_lib.dnd_SummonCreature("override", "10", creature_name, creature_amount, creature_action, adv)

        # Querys the database for more informatio
        descriptions = None  # await database_lib.dnd_CreatureDescriptions(spell)

        # Creates a function that pages through all the entries
        await discord_message_pages(ctx, tables, descriptions)

    else:
        
        # Querys the database and generates a list of messages and tables
        tables = await database_lib.dnd_SummonCreature("override", "10", creature_name, creature_amount, creature_action, adv)

        for msg in tables:
            await ctx.send(msg)

# ------------------------- Keyword mentions ---------------------------


@client.command()
async def keyword(ctx, subcommand=None, arg1=None):
    """Lists keywords on the keyword list. Use 'add' and 'remove' to change the list."""
    keywords = common_lib.read_from_txt("keyword_check/keywords.txt")

    if not subcommand:
        keyword_output = "\n".join((line) for line in keywords)
        await ctx.send("Here is a list of all keywords that I'm watching for: \n" + keyword_output)

    elif subcommand.lower() == "add":
        if not arg1:
            await ctx.send("Please specify a keyword to add to the list.")
        else:
            keyword_match = keyword_lib.keyword_check(arg1)
            if (keyword_match[0]):
                await ctx.send("That keyword is already on the list")
            else:
                common_lib.write_to_txt("keyword_check/keywords.txt", arg1)
                keyword_match = keyword_lib.keyword_check(arg1)
                if (keyword_match[0]):
                    await ctx.send("Added " + arg1 + " to the keyword list")
                else:
                    await ctx.send("Uh oh! I was unable to add that keyword to the list")
    elif subcommand.lower() == "remove":
        if not arg1:
            await ctx.send("Please specify a keyword to remove from the list.")
        else:
            keyword_match = keyword_lib.keyword_check(arg1)
            if (keyword_match[0]):
                common_lib.remove_from_txt("keyword_check/keywords.txt", arg1)
                keyword_match = common_lib.keyword_check(arg1)
                if (keyword_match[0]):
                    await ctx.send("Uh oh! I was unable to remove that keyword to the list")
                else:
                    await ctx.send("Removed " + arg1 + " from the keyword list")
            else:
                await ctx.send("That keyword isn't on the list.")
    else:
        await ctx.send("I wasn't able to process that subcommand.\nHere is the subcommand list for the 'keyword' command:\n    'add': Adds a keyword to the list.\n    'remove': Removes a keyword from the list.")


@client.event
async def on_message(ctx):
    # Ignore messages made by the bot
    if (ctx.author == client.user):
        return

    # Ignore messages in the bot command channels
    if (ctx.channel.id == command_channel):
        await client.process_commands(ctx)
        return

    # If the message is from the deals channel
    if (ctx.channel.id == deals_channel):

        keyword_match = keyword_lib.keyword_check(ctx)
        if (keyword_match[0]):
            keyword_msg = ""
            if ctx.content:
                keyword_msg += ctx.content + " "
            if ctx.embeds:
                if ctx.embeds[0].title:
                    keyword_msg += ctx.embeds[0].title + " "
                if ctx.embeds[0].description:
                    keyword_msg += ctx.embeds[0].description

            keyword_msg = keyword_msg.partition("@Deal Notifications")[0]

            print("I found a keyword: " + keyword_match[1])
            role = discord.utils.get(ctx.guild.roles, id=keyword_role)
            channel = client.get_channel(keyword_channel)
            embed = discord.Embed(description="I found a keyword!\n" + role.mention, color=0x49cd74)
            embed.add_field(name="Keyword Matched", value=keyword_match[1])
            await channel.send(role.mention + " " + keyword_msg, embed=embed)

# ------------------ Tracker looping tasks ------------------------


def seconds_until(hours, minutes):
    given_time = datetime.time(hours, minutes)
    now = datetime.datetime.now()
    future_exec = datetime.datetime.combine(now, given_time)
    if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
        future_exec = datetime.datetime.combine(now + datetime.timedelta(days=1), given_time)  # days always >= 0

    return (future_exec - now).total_seconds()


def seconds_until_date(given_date):
    now = datetime.datetime.now()

    return (given_date - now).total_seconds()


async def SkyblockNextHarvest():

    # Get the channel object from discord
    channel = client.get_channel(sb_channel)

    next_harvest = common_lib.read_from_txt("skyblock/next_harvest.txt")

    # Get the total seconds until the next harvest
    future_harvest = seconds_until_date(datetime.datetime.strptime(next_harvest[0], "%Y-%m-%d %H:%M:%S"))

    if future_harvest > 0:

        # Wait for that many seconds
        await asyncio.sleep(int(future_harvest * 0.90))

        # Send the command to the channel
        await channel.send("Ghast Minions are aproximately 90 percent filled.")

        # Wait for that many seconds
        await asyncio.sleep(int(future_harvest * 0.10))

        # Send the command to the channel
        await channel.send("Ghast Minions have been 100 percent filled. Please run 'm!skyblock collect' to reset the timer.")


@tasks.loop(hours=23)
async def SkyblockTrackerLoop():
    await asyncio.sleep(seconds_until(18, 00))
    while True:
        try:

            # Get the channel object from discord
            channel = client.get_channel(sb_channel)

            # Get the message contents
            msg = await skyblock_lib.SkyblockTracker()

            # Sends the final report to the tracker channel
            await channel.send(msg)

        except Exception as e:
            print("Exception occured during skyblock loop: ", str(e))
            await asyncio.sleep(20)
            continue
        break
    await asyncio.sleep(60)


@tasks.loop(hours=23)
async def NetworkTrackerLoop():
    await asyncio.sleep(seconds_until(18, 00))
    while True:
        try:
            await get_public_ip_address()

        except Exception as e:
            print("Exception occured during network loop: ", str(e))
            await asyncio.sleep(20)
            continue
        break
    await asyncio.sleep(60)


# ------------------ Launch the bot ------------------------

try:
    client.run(config['BOT']['discord_bot_token'])
except Exception as e:
    print("Error attempting to launch bot: ", str(e))
    e = input("Press enter to close")
    sys.exit()
