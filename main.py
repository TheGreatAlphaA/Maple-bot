"""
This is Maple-bot"s main file, a Discord.py bot for Alpha_A.

Features:
    * Messages users when they are kicked from their Skyblock Island
    * Messages users whem keywords are spoken in the #deals channel
    * Pulls memes and fanart from the Bofuri subreddit
    * More features coming soon!
"""

import aiohttp

import random

import os

import sys
import json
import time
import datetime

try:
    import asyncio
except ModuleNotFoundError:
    print("Please install asyncio. (pip install asyncio)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    import urllib.request
except ModuleNotFoundError:
    print("Please install urllib. (pip install urllib3)")
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

# This aparently solves something discord added in 1.5.0
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# ---- importing .ini file

dir_path = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read("info.ini")

# Change only the no_category default string
help_command = commands.DefaultHelpCommand(
    no_category="Commands"
)

client = commands.Bot(
    command_prefix=commands.when_mentioned_or("m!"),
    help_command=help_command,
    intents=intents
)


# ------------------------- Read from txt files -----------------


def read_from_txt(path):

    # Initialize variables
    raw_lines = []
    lines = []

    # Load data from the txt file
    try:
        f = open(path, "r")
        raw_lines = f.readlines()
        f.close()

    except FileNotFoundError:
        print("Error! No txt file found!")
        return None

    # Parse the data
    for line in raw_lines:
        lines.append(line.strip("\n"))

    # Returns the data
    return lines


# ------------------------- Write to txt files -----------------


def write_to_txt(path, txt):

    # Opens the txt file, and appends data to it
    try:
        f = open(path, "a")
        f.write("\n")
        f.write(txt.lower())
        f.close()

    except FileNotFoundError:
        print("Error! No txt file found!")
        return None


def write_to_txt_overwrite(path, txt):

    # Opens the txt file, and writes data to it
    try:
        f = open(path, "w")
        f.write(txt)
        f.close()

    except FileNotFoundError:
        print("Error! No txt file found!")
        return None


# ------------------------- Remove data from txt files -----------------


def remove_from_txt(path, txt):

    # Initialize variables
    raw_lines = []
    lines = []

    # Load data from the txt file
    try:
        f = open(path, "r")
        raw_lines = f.readlines()
        f.close()

    except FileNotFoundError:
        print("Error! No txt file found!")
        return None

    # Parse the data
    for line in raw_lines:
        if line.lower().rstrip() != txt.lower():
            lines.append(line.lower().rstrip())

    # Checks if the data has been emptied 
    if lines:
        output_lines = "\n".join(lines)
    else:
        output_lines = ""

    # Overwrites the data with the new information
    try:
        f = open(path, "w")
        f.write(output_lines)
        f.close
    except FileNotFoundError:
        print("Error! No txt file found!")
        return None


# ------------------------- Convert char arrays to int arrays -----------------


def convert_to_int(array):
    try:
        new_array = [int(element) for element in array]
        return new_array
    except ValueError:
        print("Error! Expected ints, but got chars in convert_to_int")


# ------------------------- Checks for keywords in text -----------------

def keyword_partition(text, delim):
    if isinstance(text, str) is True:
        return text.partition(delim)[0]


def keyword_check(text):
    keywords = read_from_txt("keyword_check/keywords.txt")
    negatives = read_from_txt("keyword_check/negatives.txt")
    delim = "@Deal Notifications"

    if keywords:
        for keyword_set in keywords:
            good = False
            matches = 0
            total = len(keyword_set.split("+"))
            for keyword in keyword_set.split("+"):
                if isinstance(text, str) is True:
                    text_part = keyword_partition(text, delim)
                    if (keyword.lower() in text_part.lower()):
                        matches += 1
                if hasattr(text, "content"):
                    text_content_part = keyword_partition(text.content, delim)
                    if (keyword.lower() in text_content_part.lower()):
                        matches += 1
                    if text.embeds:
                        embed_full = ""
                        if text.embeds[0].title:
                            embed_full += text.embeds[0].title
                        if text.embeds[0].description:
                            embed_full += text.embeds[0].description
                        embed_full_part = keyword_partition(embed_full, delim)
                        if (keyword.lower() in embed_full_part.lower()):
                            matches += 1
            if (matches == total):
                good = True
                break

        if negatives:
            for negative in negatives:
                if isinstance(text, str) is True:
                    text_part = keyword_partition(text, delim)
                    if (negative.lower() in text_part.lower()):
                        good = False
                        break
                if hasattr(text, "content"):
                    text_content_part = keyword_partition(text.content, delim)
                    if (negative.lower() in text_content_part.lower()):
                        good = False
                        break
                    if text.embeds:
                        embed_full = ""
                        if text.embeds[0].title:
                            embed_full += text.embeds[0].title
                        if text.embeds[0].description:
                            embed_full += text.embeds[0].description
                        embed_full_part = keyword_partition(embed_full, delim)
                        if (negative.lower() in embed_full_part.lower()):
                            good = False
                            break

        if (good):
            return (True, keyword_set)
        else:
            return (False, None)
    else:
        return (False, None)

# ------------------------- Startup -----------------


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game("m!help"))
    print(f"Bot Is Ready. Logged in as {client.user}")
    # start the task loop that checks global vars
    # for each account to check. Default none as set above


# ------------- Function for account that needs to be checked -----------------

# Holds the value for whether the checker is online
sb_online = False
# Holds the value for whether the tracker is online
sb_tracker = False
# Holds the value for whether the offline message has been sent
# skyblock_msg[0] = Has the message been sent?
# skyblock_msg[1] = Why was the message sent?
sb_msg = [False, "None"]
# This is the channel that updates are sent to
sb_channel = convert_to_int(read_from_txt("skyblock/channels.txt"))
# This is the role that is pinged when users go offline
sb_role = convert_to_int(read_from_txt("skyblock/roles.txt"))
# This is the root url for all Hypixel api calls
sb_api_call = "https://api.hypixel.net/"
# This is the api key that identifies the bot
sb_api_key = read_from_txt("skyblock/hypixel_api.txt")
# This is the list of Minecraft unique user ids
sb_api_uuid = read_from_txt("skyblock/minecraft_uuids.txt")
# This is the list of Hypixel Skyblock Profile unique user ids
sb_api_profile = read_from_txt("skyblock/skyblock_profiles.txt")
# This is the list of Minecraft usernames, matches with the uuids
sb_api_username = read_from_txt("skyblock/minecraft_usernames.txt")


async def CheckAcc(ctx):
    channel = client.get_channel(sb_channel[0])
    role = discord.utils.get(ctx.guild.roles, id=sb_role[0])
    url = sb_api_call + "status?key=" + sb_api_key[0] + "&uuid=" + sb_api_uuid[0]
    resp = urllib.request.urlopen(url)
    data = json.load(resp)
    session = data["session"]
    online = session["online"]

    # Case 1: Player is online and on their private island
    if online is True:
        mode = session["mode"]
        if mode == "dynamic" and sb_msg[0] is False:
            return

    # Case 2: Player goes offline
    if online is False and sb_msg[0] is False:
        sb_msg[0] = True
        sb_msg[1] = "offline"
        await channel.send(role.mention + " Alpha_A is " + sb_msg[1])
        return
    elif online is False and sb_msg[0] is True:
        # Bot is alerting now, we don't need to process more rules
        return

    # Case 3: Player returns online
    elif online is True:
        if sb_msg[0] is True and sb_msg[1] == "offline":
            sb_msg[0] = False
            sb_msg[1] = "online"
            await channel.send(role.mention + " Alpha_A is " + sb_msg[1])
            return

        # Case 4: Player is online, but not on the private island
        elif mode != "dynamic" and sb_msg[0] is False:
            sb_msg[0] = True
            sb_msg[1] = "away"
            await channel.send(role.mention + " Alpha_A is " + sb_msg[1])
            return
        elif mode != "dynamic" and sb_msg[0] is True:
            # Bot is alerting now, we don't need to process more rules
            return

        # Case 5: Player is online, and returns to their private island
        elif mode == "dynamic" and sb_msg[0] is True and sb_msg[1] == "away":
            sb_msg[0] = False
            sb_msg[1] = "online"
            await channel.send(role.mention + " Alpha_A is " + sb_msg[1])
            return
    else:
        print("Shitfuck, something went wrong, here is the error log:")
        if online is True:
            print("online = True")
        elif online is False:
            print("online = False")
        else:
            print("Unhandled exception with online")
        if mode:
            print("mode = " + mode)
        if sb_msg[0] is True:
            print("sb_msg[0] = True")
        elif sb_msg[0] is False:
            print("sb_msg[0] = False")
        else:
            print("Unhandled exception with sb_msg")
        print("sb_msg[1] = " + sb_msg[1])


async def SkyblockGhastTearCollection(player, profile):
    url = sb_api_call + "skyblock/profile?key=" + sb_api_key[0] + "&profile=" + profile
    resp = urllib.request.urlopen(url)
    data = json.load(resp)
    ghast_collection = data["profile"]["members"][player]["collection"]["GHAST_TEAR"]
    return ghast_collection


async def SkyblockMayorChecker():
    url = sb_api_call + "resources/skyblock/election?key=" + sb_api_key[0]
    resp = urllib.request.urlopen(url)
    data = json.load(resp)

    mayor = []
    mayor.append(data["mayor"]["name"])
    try:
        for i in [0, 1, 2, 3, 4]:
            mayor.append(data["current"]["candidates"][i]["name"])
    except Exception:
        print("Mayor elections not open yet!")
    return mayor


async def SkyblockHyperCatalystProfitabilityChecker(mayor):
    url = sb_api_call + "skyblock/bazaar?key=" + sb_api_key[0]
    resp = urllib.request.urlopen(url)
    data = json.load(resp)
    ghast_instant_sell = data["products"]["ENCHANTED_GHAST_TEAR"]["quick_status"]["sellPrice"]
    hypercatalyst_buy_order = data["products"]["HYPER_CATALYST"]["quick_status"]["sellPrice"]
    starfall_buy_order = data["products"]["STARFALL"]["quick_status"]["sellPrice"]

    # Calculated using T12 Ghast Minions + 1 Flycatcher + Mithril Infusion + T5 Beacon Boost
    # 1612.8 Enchanted Ghast Tears per minion
    # 4 Hyper Catalysts per minion
    # 0.99 is for bazaar 1% tax for sellers
    if mayor == "Derpy":
        # Doubled output when Derpy is mayor
        daily_gross = 1612.8 * 30 * ghast_instant_sell * 2 * 0.99
    else:
        daily_gross = 1612.8 * 30 * ghast_instant_sell * 0.99
    daily_expense = (4 * 30 * hypercatalyst_buy_order) + (128 * starfall_buy_order)
    daily_net = daily_gross - daily_expense
    
    return int(daily_net)


async def SkyblockTracker(ctx):
    # Estimated burden of this function is 5 API calls

    # Checks which mayors are elected or up for election
    mayors = await SkyblockMayorChecker()
    # Assigns the currently elected mayor
    mayor = mayors[0]
    # Calculates the estimates profit for today.
    profit = await SkyblockHyperCatalystProfitabilityChecker(mayor)

    ranking = [[] for i in range(3)]
    channel = client.get_channel(sb_channel[1])

    # Compiles the ghast tear collection data for all 3 players being tracked
    for i in range(3):
        ranking[i].append(await SkyblockGhastTearCollection(sb_api_uuid[i], sb_api_profile[i]))
        ranking[i].append(sb_api_username[i])
    ranking.sort(reverse=True)
    # This string contains the message that will be sent at the end.
    sb_tracker_msg = ""

    # Lists the ranked ghast collection leaderboard.
    for i in range(3):
        # Checks if any of the top 3 include myself
        if ranking[i][1] == "Alpha_A":
            sb_tracker_msg += ranking[i][1] + " has a ghast collection of " + str(ranking[i][0])
            sb_delta = ranking[0][0] - ranking[i][0]
            sb_tracker_msg += " (-" + str(sb_delta) + " from 1st place)"

            # Reads yesterday's delta
            # Delta is a vaule that determines the difference between myself and first place
            sb_delta_old = convert_to_int(read_from_txt("skyblock/delta.txt"))

            # Computes delta over time. This is helpful for spotting drastic changes
            sb_delta_ot = sb_delta - sb_delta_old[0]
            if sb_delta_ot > 0:
                sb_tracker_msg += " (+" + str(sb_delta_ot) + " \u0394)\n"
            else:
                sb_tracker_msg += " (" + str(sb_delta_ot) + " \u0394)\n"

            # Writes down today's delta to compare tomorrow
            write_to_txt_overwrite("skyblock/delta.txt", str(sb_delta))

        else:
            # Lists the ghast collections for everyone else
            sb_tracker_msg += str(ranking[i][1]) + " has a ghast collection of " + str(ranking[i][0]) + "\n"

    # Check if a special mayor has been elected
    if mayor not in {"Aatrox", "Cole", "Diana", "Diaz", "Finnegan", "Foxy", "Marina", "Paul"}:
        sb_tracker_msg += "\n:person_in_tuxedo: Special Mayor " + mayor + " is in office today.\n"

    # Check if a special mayor is up for election
    try:
        # Assigns all the mayoral candidates
        candidates = []
        for i in [1, 2, 3, 4, 5]:
            candidates.append(mayors[i])
        for candidate in candidates:
            if candidate not in {"Aatrox", "Cole", "Diana", "Diaz", "Finnegan", "Foxy", "Marina", "Paul"}:
                sb_tracker_msg += "\n:person_in_tuxedo: Special Mayor " + candidate + " is up for election.\n"
    except Exception:
        print("No candidates avaliable")

    # Check if the estimated profit for today was positive
    if profit > 0:
        sb_tracker_msg += "\n:chart_with_upwards_trend: Today is PROFITABLE (+" + str(profit) + " coins)"
    else:
        sb_tracker_msg += "\n:chart_with_downwards_trend: Today is not profitable... (" + str(profit) + " coins)"

    # Sends the final report to the tracker channel
    await channel.send(sb_tracker_msg)


# ------------------------- Bot commands ---------------------------


command_channel = convert_to_int(read_from_txt("channels.txt"))


@client.command()
async def nya(ctx):
    """Have Maple put on her best cat impression! Nya!"""
    await ctx.send("Nya!  (=^-ω-^=)")


@client.command()
async def ping(ctx):
    """Ping Maple to see how long it takes her to ping back"""
    pingtime = time.time()
    pingms = await ctx.send("Pinging...")
    ping = time.time() - pingtime
    await pingms.edit(content=":ping_pong:  time is `%.01f seconds`" % ping)


@client.command()
async def skyblock(ctx, subcommand=None, arg1=None):
    """Starts the skyblock island checker"""
    global sb_online
    global sb_msg
    global sb_tracker

    if not subcommand:
        await ctx.send("Please provide a valid subcommand.\nHere is the subcommand list for the 'skyblock' command:\n    'start': Starts the skyblock checker.\n     'stop': Stops the skyblock checker.\n    'status': Checks the status of the skyblock checker")

    elif subcommand.lower() == "start":
        if sb_online is False:
            try: 
                sb_msg = [False, "None"]
                CheckOffline.start(ctx)
                sb_online = True
                await ctx.send("Process started successfully!")
            except Exception as e:
                print("Error attempting to launch the skyblock checker: ", str(e))
                await ctx.send("Oh no! I can't start the checker right now...\nHere is the error: " + str(e))
            return
        elif sb_online is True:
            await ctx.send("Process has already started!")

    # Stops the skyblock island checker
    elif subcommand.lower() == "stop":
        if sb_online is True:
            try:
                CheckOffline.stop()
                sb_online = False
                sb_msg = [False, "None"]
                await ctx.send("Process haulted successfully!")
            except Exception as e:
                print("Error attempting to stop the skyblock checker: ", str(e))
                await ctx.send("Oh no! I can't stop the checker right now...\nHere is the error: " + str(e))
            return
        elif sb_online is False: 
            await ctx.send("Process is not currently running!")

    # Checks the status of the skyblock island checker
    elif subcommand.lower() == "status":
        if sb_online is False:
            await ctx.send(":warning: Looks like the checker is offline, run m!start to turn it on.")
        elif sb_msg[1] == "online":
            await ctx.send(":thumbup: Everything seems to be running just fine!")
        elif sb_msg[1] == "offline":
            await ctx.send(":signal_strength: Alpha_A is no longer online!")
        elif sb_msg[1] == "away":
            await ctx.send(":island: Alpha_A is no longer on the island!")
        else:
            await ctx.send("Oh no! Some kind of error happened!")

    # Starts the skyblock island tracker
    elif subcommand.lower() == "tracker":
        if not arg1:
            if sb_tracker is False:
                try: 
                    SkyblockTrackerLoop.start(ctx)
                    sb_tracker = True
                    await ctx.send("Process started successfully!")
                except Exception as e:
                    print("Error attempting to launch the skyblock tracker: ", str(e))
                    await ctx.send("Oh no! I can't start the tracker right now...\nHere is the error: " + str(e))
                return
            elif sb_tracker is True:
                try:
                    SkyblockTrackerLoop.cancel(ctx)
                    sb_tracker = False
                    await ctx.send("Process haulted successfully!")
                except Exception as e:
                    print("Error attempting to stop the skyblock tracker: ", str(e))
                    await ctx.send("Oh no! I can't stop the tracker right now...\nHere is the error: " + str(e))
                return
        if arg1 == "test":
            try:
                await SkyblockTracker(ctx)
                await ctx.send("Sent a test message to the tracker channel!")
            except Exception as e:
                await ctx.send("Oh no! I'm not able to use the tracker tester right now...\nHere is the error: " + str(e))
                return
    else:
        await ctx.send("I wasn't able to process that subcommand.\nHere is the subcommand list for the 'skyblock' command:\n    'start': Starts the skyblock checker.\n     'stop': Stops the skyblock checker.\n    'status': Checks the status of the skyblock checker")


@client.command(pass_context=True)
async def meme(ctx):
    """Posts a funny meme from the BoFuri subreddit"""
    embed = discord.Embed(title="", description="")

    async with aiohttp.ClientSession() as cs:
        async with cs.get("https://www.reddit.com/r/BoFuri/search.json?q=flair%3AMeme&restrict_sr=1&sr_nsfw=&sort=hot") as r:
            res = await r.json()
            embed.set_image(url=res["data"]["children"] [random.randint(0, 24)]["data"]["url"])
            await ctx.send(embed=embed)


@client.command(pass_context=True)
async def fanart(ctx):
    """Posts a cool fanart from the BoFuri subreddit"""
    embed = discord.Embed(title="", description="")

    async with aiohttp.ClientSession() as cs:
        async with cs.get("https://www.reddit.com/r/BoFuri/search.json?q=flair%3A%22Fan%20Content%22&restrict_sr=1&sr_nsfw=&sort=hot") as r:
            res = await r.json()
            embed.set_image(url=res["data"]["children"][random.randint(0, 24)]["data"]["url"])
            await ctx.send(embed=embed)

# ------------------------- Keyword mentions ---------------------------
keyword_channel = convert_to_int(read_from_txt("keyword_check/channels.txt"))
keyword_role = convert_to_int(read_from_txt("keyword_check/roles.txt"))


@client.command()
async def keyword(ctx, subcommand=None, arg1=None):
    """Lists keywords on the keyword list. Use 'add' and 'remove' to change the list."""
    keywords = read_from_txt("keyword_check/keywords.txt")

    if not subcommand:
        keyword_output = "\n".join((line) for line in keywords)
        await ctx.send("Here is a list of all keywords that I'm watching for: \n" + keyword_output)

    elif subcommand.lower() == "add":
        if not arg1:
            await ctx.send("Please specify a keyword to add to the list.")
        else:
            keyword_match = keyword_check(arg1)
            if (keyword_match[0]):
                await ctx.send("That keyword is already on the list")
            else:
                write_to_txt("keyword_check/keywords.txt", arg1)
                keyword_match = keyword_check(arg1)
                if (keyword_match[0]):
                    await ctx.send("Added " + arg1 + " to the keyword list")
                else:
                    await ctx.send("Uh oh! I was unable to add that keyword to the list")
    elif subcommand.lower() == "remove":
        if not arg1:
            await ctx.send("Please specify a keyword to remove from the list.")
        else:
            keyword_match = keyword_check(arg1)
            if (keyword_match[0]):
                remove_from_txt("keyword_check/keywords.txt", arg1)
                keyword_match = keyword_check(arg1)
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
    if (ctx.channel.id in command_channel):
        await client.process_commands(ctx)
        return

    # Ignore messages not in one of the specified channels
    if (ctx.channel.id not in keyword_channel):
        return

    keyword_match = keyword_check(ctx)
    if (keyword_match[0]):
        keyword_msg = ""
        if ctx.content:
            keyword_msg += ctx.content + " "
        if ctx.embeds:
            if ctx.embeds[0].title:
                keyword_msg += ctx.embeds[0].title + " "
            if ctx.embeds[0].description:
                keyword_msg += ctx.embeds[0].description
        print("I found a keyword: " + keyword_match[1])
        role = discord.utils.get(ctx.guild.roles, id=keyword_role[0])
        channel = client.get_channel(keyword_channel[1])
        embed = discord.Embed(description="I found a keyword!\n" + role.mention, color=0x49cd74)
        embed.add_field(name="Keyword Matched", value=keyword_match[1])
        await channel.send(role.mention + " " + keyword_msg, embed=embed)


# ------------------ Tracker looping tasks ------------------------


def seconds_until(hours, minutes):
    given_time = datetime.time(hours, minutes)
    now = datetime.datetime.now()
    future_exec = datetime.datetime.combine(now, given_time)
    if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
        future_exec = datetime.datetime.combine(now + datetime.timedelta(days=1), given_time) # days always >= 0

    return (future_exec - now).total_seconds()
  

@tasks.loop(hours=23)
async def SkyblockTrackerLoop(ctx):
    await asyncio.sleep(seconds_until(18, 00))
    while True:
        try:
            await SkyblockTracker(ctx)
        except Exception as e:
            print("Exception occured during loop: ", str(e))
            await asyncio.sleep(20)
            continue
        break
    await asyncio.sleep(60)


# ------------------ Checking the account listed above ------------------------


@tasks.loop(seconds=60)
async def CheckOffline(ctx):
    await CheckAcc(ctx)

try:
    client.run(config["INFO"]["discordBotToken"])
except Exception as e:
    print("Error attempting to launch bot: ", str(e))
    e = input("Press enter to close")
    sys.exit()
