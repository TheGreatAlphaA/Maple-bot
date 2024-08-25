
import sys
import json
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
    import mysql.connector
except ModuleNotFoundError:
    print("Please install mysql-connector. (pip install mysql-connector-python)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    import configparser
except ModuleNotFoundError:
    print("Please install asyncio. (pip install configparser)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    from discord.ext import commands, tasks
except ModuleNotFoundError:
    print("Please install discordpy. (pip install discord.py)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")


class skyblock_cog(commands.Cog):
    #
    #   Definitions
    #
    def __init__(self, bot):
        self.bot = bot
        
        self.config = configparser.ConfigParser()
        self.config.read("info.ini")

        self.db_host = self.config['DATABASE']['host']
        self.db_user = self.config['DATABASE']['user']
        self.db_password = self.config['DATABASE']['password']
        self.db_database = self.config['DATABASE']['database']

        # This is the api key that identifies the bot
        self.sb_api_key = self.config['SKYBLOCK']['hypixel_api_key']

        self.sb_channel = int(self.config['SKYBLOCK']['skyblock_tracker_channel'])

        # This is the list of player profiles
        self.sb_players = []

        self.sb_profiles()

        self.SkyblockTrackerLoop.start()

    #
    #   Standard Functions
    #

    def sb_profiles(self):
        # Creates an empty list
        result = []

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        query = """SELECT ID, MINECRAFT_USERNAME, MINECRAFT_UUID, SKYBLOCK_UUID FROM sb_players"""
        cursor.execute(query)

        # Checks if query is empty
        if cursor.rowcount == 0:
            return None

        # Creates each table body
        skyblock_players = cursor.fetchall()

        for player in skyblock_players:
            player_attr = [player[1], player[2], player[3]]
            result.append(player_attr)

        self.sb_players = result

    def seconds_until(self, hours, minutes):
        given_time = datetime.time(hours, minutes)
        now = datetime.datetime.now()
        future_exec = datetime.datetime.combine(now, given_time)
        if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
            future_exec = datetime.datetime.combine(now + datetime.timedelta(days=1), given_time)  # days always >= 0

        return (future_exec - now).total_seconds()

    def read_from_txt(self, path):
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

    def write_to_txt(self, path, txt):
        # Opens the txt file, and writes data to it
        try:
            f = open(path, "w")
            f.write(txt)
            f.close()

        except FileNotFoundError:
            print("Error! No txt file found!")
            return None

    def convert_to_int(self, array):
        try:
            new_array = [int(element) for element in array]
            return new_array
        except ValueError:
            print("Error! Expected ints, but got chars in convert_to_int")

    def human_format(self, num):
        num = float('{:.3g}'.format(num))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

    #
    #   Async Functions
    #

    async def SkyblockGhastTearCollection(self, player, profile):
        url = "https://api.hypixel.net/v2/skyblock/profile?key=" + self.sb_api_key + "&profile=" + profile
        resp = urllib.request.urlopen(url)
        data = json.load(resp)
        ghast_collection = data["profile"]["members"][player]["collection"]["GHAST_TEAR"]
        return ghast_collection

    async def SkyblockMayorChecker(self):
        url = "https://api.hypixel.net/v2/resources/skyblock/election?key=" + self.sb_api_key
        resp = urllib.request.urlopen(url)
        data = json.load(resp)

        mayor = []

        # Append the currently elected mayor
        mayor.append(data["mayor"]["name"])

        # Append the mayors up for election
        try:
            for i in range(5):
                mayor.append(data["current"]["candidates"][i]["name"])
        except KeyError:
            # Mayor election are not open yet!
            pass

        return mayor

    async def SkyblockGeneralProfitabilityChecker(self, mayor, bazaar_data):
        ghast_instant_sell = bazaar_data["products"]["ENCHANTED_GHAST_TEAR"]["quick_status"]["sellPrice"]

        # Calculated using T12 Ghast Minions + Plasma Bucket + 1 Flycatcher + Mithril Infusion
        # 475.2 Enchanted Ghast Tears per minion
        # 0.99 is for bazaar 1% tax for sellers
        if mayor == "Derpy":
            # Doubled output when Derpy is mayor
            daily_gross = 475.2 * 30 * ghast_instant_sell * 2 * 0.99
        else:
            daily_gross = 475.2 * 30 * ghast_instant_sell * 0.99
        daily_expense = 0
        daily_net = daily_gross - daily_expense
        
        return int(daily_net)

    async def SkyblockHyperCatalystProfitabilityChecker(self, mayor, bazaar_data):
        ghast_instant_sell = bazaar_data["products"]["ENCHANTED_GHAST_TEAR"]["quick_status"]["sellPrice"]
        hypercatalyst_buy_order = bazaar_data["products"]["HYPER_CATALYST"]["quick_status"]["sellPrice"]
        starfall_buy_order = bazaar_data["products"]["STARFALL"]["quick_status"]["sellPrice"]

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
        # Net profit for hypercatalysts needs to exceed baseline profit, otherwise, we would still make more money without them
        baseline = await self.SkyblockGeneralProfitabilityChecker(mayor, bazaar_data)
        daily_net = daily_gross - daily_expense - baseline
        
        return int(daily_net)

    async def SkyblockTracker(self):
        # Estimated burden of this function is 5 API calls
        url = "https://api.hypixel.net/v2/skyblock/bazaar?key=" + self.sb_api_key
        resp = urllib.request.urlopen(url)
        bazaar_data = json.load(resp)

        # Checks which mayors are elected or up for election
        mayors = await self.SkyblockMayorChecker()
        # Assigns the currently elected mayor
        mayor = mayors[0]
        # Calculates the estimates profit for today.
        profit_hyper = await self.SkyblockHyperCatalystProfitabilityChecker(mayor, bazaar_data)
        profit_gen = await self.SkyblockGeneralProfitabilityChecker(mayor, bazaar_data)

        ranking = [[] for i in range(len(self.sb_players))]

        # Compiles the ghast tear collection data for all 3 players being tracked
        for i in range(len(self.sb_players)):
            ranking[i].append(await self.SkyblockGhastTearCollection(self.sb_players[i][1], self.sb_players[i][2]))
            ranking[i].append(self.sb_players[i][0])
        ranking.sort(reverse=True)
        # This string contains the message that will be sent at the end.
        sb_tracker_msg = ""

        # Lists the ranked ghast collection leaderboard.
        for i in range(len(self.sb_players)):
            # Checks if any of the top 3 include myself
            if ranking[i][1] == "Alpha_A":
                if i == 0:
                    sb_tracker_msg += ranking[i][1] + " has a ghast collection of " + str(ranking[i][0])
                    sb_delta = ranking[i][0] - ranking[1][0]
                    sb_tracker_msg += " (+" + str(sb_delta) + " from 2nd place)"
                else:
                    sb_tracker_msg += ranking[i][1] + " has a ghast collection of " + str(ranking[i][0])
                    sb_delta = ranking[0][0] - ranking[i][0]
                    sb_tracker_msg += " (-" + str(sb_delta) + " from 1st place)"

                # Reads yesterday's delta (change)
                # Delta is a value that determines the difference between myself and first place
                sb_delta_old = self.convert_to_int(self.read_from_txt("skyblock/delta.txt"))

                # Computes delta over time. This is helpful for spotting drastic changes
                sb_delta_ot = sb_delta - sb_delta_old[0]
                if sb_delta_ot > 0:
                    sb_tracker_msg += " (+" + str(sb_delta_ot) + " \u0394)\n"
                else:
                    sb_tracker_msg += " (" + str(sb_delta_ot) + " \u0394)\n"

                # Writes down today's delta to compare tomorrow
                self.write_to_txt("skyblock/delta.txt", str(sb_delta))

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
        except IndexError:
            # No candidates avaliable
            pass

        # Total profit before adding hypercatalysts
        sb_tracker_msg += "\n:bar_chart: We made " + str(self.human_format(profit_gen)) + " coins.\n"

        # Check if the estimated profit for using hypercatalysts today was positive
        if profit_hyper > 0:
            sb_tracker_msg += "\n:chart_with_upwards_trend: Today is PROFITABLE for Hyper Catalysts (+" + str(self.human_format(profit_hyper)) + " coins)"
        else:
            sb_tracker_msg += "\n:chart_with_downwards_trend: Today is not profitable for Hyper Catalysts... (" + str(self.human_format(profit_hyper)) + " coins)"

        return sb_tracker_msg

    #
    #   Commands
    #

    @commands.group(name="skyblock", invoke_without_command=True)
    async def skyblock(self, ctx):
        await ctx.send("```Sure thing boss. Please specify a subcommand to use this feature.\nHere is the subcommand list for the 'skyblock' command:\n    'tracker': Manages the skyblock ghast minion leaderboard tracker.\n    'collect': Manages the skyblock ghast minion harvest reminder task.```")

    @skyblock.group(name="tracker", help="Manages the skyblock ghast minion leaderboard tracker.", invoke_without_command=True)
    @commands.has_role("Bot Tester")
    async def tracker(self, ctx, arg1=None):
        await ctx.send("```Sure thing boss. Please specify a subcommand to use this feature.\nHere is the subcommand list for the 'tracker' command:\n    'tracker start': Starts the skyblock ghast tear tracker.\n    'tracker stop': Stops the skyblock ghast tear tracker.\n    'tracker status': Checks on the status of the tracker.\n    'tracker test': Sends a test message from the skyblock tracker.```")
        
    @tracker.command(name="start", help="starts the skyblock ghast tear leaderboard checker")
    @commands.has_role("Bot Tester")
    async def start(self, ctx):
        try:
            if self.SkyblockTrackerLoop.is_running() is True:
                await ctx.send("The Skyblock Tracker is currently running.")
            # If the loop is not running
            elif self.SkyblockTrackerLoop.is_running() is False:

                # Start the tracking loop
                try: 
                    self.SkyblockTrackerLoop.start()
                except Exception as e:
                    print("Error attempting to launch the skyblock tracker: ", str(e))
                    await ctx.send("Oh no! I can't start the skyblock tracker right now...\nHere is the error: " + str(e))

                # Check if the loop actually started
                try:
                    if self.SkyblockTrackerLoop.is_running() is True:
                        await ctx.send("Process started successfully!")
                    else:
                        await ctx.send("Oh no! I wasn't able to start the skyblock tracker.")
                except Exception as e:
                    print("Error attempting to launch the skyblock tracker: ", str(e))
                    await ctx.send("Oh no! I can't start the skyblock tracker right now...\nHere is the error: " + str(e))
                return
        except Exception as e:
            await ctx.send("Oh no! I'm not able to check the status of the skyblock tracker right now...\nHere is the error: " + str(e))
            return
        
    @tracker.command(name="stop", help="stops the skyblock ghast tear leaderboard checker")
    @commands.has_role("Bot Tester")
    async def stop(self, ctx):
        try:
            # Check if the loop is actually stopped
            if self.SkyblockTrackerLoop.is_running() is False:
                await ctx.send("The Skyblock Tracker is currently offline. Use 'm!skyblock tracker' to start the tracker")
            # If the loop is running
            elif self.SkyblockTrackerLoop.is_running() is True:

                # Stop the loop
                try:
                    self.SkyblockTrackerLoop.cancel()
                except Exception as e:
                    print("Error attempting to stop the skyblock tracker: ", str(e))
                    await ctx.send("Oh no! I can't stop the skyblock tracker right now...\nHere is the error: " + str(e))

                # Check if the loop actually stopped
                try:
                    if self.SkyblockTrackerLoop.is_running() is False:
                        # This looks really stupid, but the error that this throws keeps bugging me. Will fix later.
                        # It's very likely that the call to check if the process is running is happening before the process acutally has a chance to stop. 
                        # The extra if/else statement buffers the check just long enough to get the result we want.
                        if self.SkyblockTrackerLoop.is_running() is False:
                            await ctx.send("Oh no! I wasn't able to stop the skyblock tracker.")
                        else:
                            await ctx.send("Process haulted successfully!")
                    else:
                        await ctx.send("Process haulted successfully!")
                except Exception as e:
                    print("Error attempting to stop the skyblock tracker: ", str(e))
                    await ctx.send("Oh no! I can't stop the skyblock tracker right now...\nHere is the error: " + str(e))
                return
        except Exception as e:
            await ctx.send("Oh no! I'm not able to check the status of the skyblock tracker right now...\nHere is the error: " + str(e))
            return

    @tracker.command(name="status", help="checks to see if the skyblock ghast tear leaderboard checker is running or not")
    @commands.has_role("Bot Tester")
    async def status(self, ctx):
        try:
            if self.SkyblockTrackerLoop.is_running() is True:
                await ctx.send("The Skyblock Tracker is currently running.")
            else:
                await ctx.send("The Skyblock Tracker is currently offline. Use 'm!skyblock tracker' to start the tracker")
        except Exception as e:
            await ctx.send("Oh no! I'm not able to check the status of the skyblock tracker right now...\nHere is the error: " + str(e))
            return

    @tracker.command(name="test", help="sends a test message to the skyblock tracker channel")
    @commands.has_role("Bot Tester")
    async def test(self, ctx):
        try:
            # Get the channel object from discord
            channel = self.bot.get_channel(self.sb_channel)

            # Get the message contents
            msg = await self.SkyblockTracker()

            # Sends the final report to the tracker channel
            await channel.send(msg)

            await ctx.send("Sent a test message to the tracker channel!")

        except Exception as e:
            await ctx.send("Oh no! I'm not able to use the skyblock tracker tester right now...\nHere is the error: " + str(e))
            return

    @skyblock.command(name="collect", help="manages the skyblock ghast minion harvest reminder task")
    @commands.has_role("Bot Tester")
    async def collect(self, ctx, arg1=None):
        await ctx.send("This command was deemed too dangerous to be left alive. I hope we can find a replacement soon...")
        """
        try:
            # Define the task
            global harvest_task

            # If task already exists, cancel it
            if harvest_task in asyncio.all_tasks():
                harvest_task.cancel()

            # Get the channel object from discord
            channel = self.bot.get_channel(self.sb_channel)

            last_harvest = self.read_from_txt("skyblock/last_harvest.txt")
            next_harvest = self.read_from_txt("skyblock/next_harvest.txt")

            # Get the date and time of the last recorded harvest
            past_harvest = datetime.datetime.strptime(last_harvest[0], "%Y-%m-%d %H:%M:%S")
            # Get the current date and time
            present_harvest = datetime.datetime.now().replace(microsecond=0)
            # Get the previously predicted best harvest time
            max_harvest = datetime.datetime.strptime(next_harvest[0], "%Y-%m-%d %H:%M:%S")

            # Check if Derpy is mayor
            mayor = await self.SkyblockMayorChecker()
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
            self.write_to_txt("skyblock/last_harvest.txt", str(present_harvest))

            # Update the predicted best harvest time
            self.write_to_txt("skyblock/next_harvest.txt", str(future_harvest))

            # Create the task
            harvest_task = asyncio.create_task(SkyblockNextHarvest())

        except Exception as e:
            print("Exception occured while collecting: ", str(e))
            return
            """

    @tasks.loop(hours=23)
    async def SkyblockTrackerLoop(self):
        await asyncio.sleep(self.seconds_until(18, 00))
        while True:
            try:

                # Get the channel object from discord
                channel = self.bot.get_channel(self.sb_channel)

                # Get the message contents
                msg = await self.SkyblockTracker()

                # Sends the final report to the tracker channel
                await channel.send(msg)

            except Exception as e:
                print("Exception occured during skyblock loop: ", str(e))
                await asyncio.sleep(20)
                continue
            break
        await asyncio.sleep(60)
