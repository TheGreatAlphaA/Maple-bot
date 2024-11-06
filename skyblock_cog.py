
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
    print("Please install configparser. (pip install configparser)")
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

        self.sb_channel = int(self.config['DISCORD_CHANNELS']['skyblock_tracker'])

        # This is the list of player profiles
        self.sb_players = []

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

        query = """SELECT ID, MINECRAFT_USERNAME, MINECRAFT_UUID, SKYBLOCK_UUID, GHAST_TEARS FROM sb_players"""
        cursor.execute(query)

        # Checks if query is empty
        if cursor.rowcount == 0:
            return None

        # Creates each table body
        skyblock_players = cursor.fetchall()

        for player in skyblock_players:
            player_attr = [player[1], player[2], player[3], player[4]]
            result.append(player_attr)

        self.sb_players = result

    async def sb_harvest(self, username, ghast_tears):

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        # Get the old values for ghast tears, and how many days have passed.
        query = """SELECT GHAST_TEARS FROM sb_players WHERE MINECRAFT_USERNAME = %(username)s"""
        cursor.execute(query, {'username': username})

        # Checks if query is empty
        if cursor.rowcount == 0:
            print("Error! Unexpected value in sb_harvest function!")
            return None

        # Organizes the data
        yesterdays_harvest = cursor.fetchall()

        yesterdays_ghast_tears = yesterdays_harvest[0][0]

        # If today's ghast tears are higher than yesterday's, update the ghast tear collection and days since last harvest
        if ghast_tears > yesterdays_ghast_tears:

            # Update the player's current ghast tear collection
            query = """UPDATE sb_players SET GHAST_TEARS = %(ghast_tears)s WHERE MINECRAFT_USERNAME = %(username)s"""
            cursor.execute(query, {'username': username, 'ghast_tears': ghast_tears})

            # Reset the days since last harvest
            days_since_last_harvest = 0

            query = """UPDATE sb_players SET DAYS_SINCE = %(days_since_last_harvest)s WHERE MINECRAFT_USERNAME = %(username)s"""
            cursor.execute(query, {'username': username, 'days_since_last_harvest': days_since_last_harvest})

            # Commit changes to database
            mydb.commit()

        elif ghast_tears < yesterdays_ghast_tears:
            print("Error! Unexpected value in sb_harvest function!")

    async def sb_increment_days_since(self):

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        query = """UPDATE sb_players SET DAYS_SINCE = DAYS_SINCE + 1"""
        cursor.execute(query)

        # Commit changes to database
        mydb.commit()

    async def sb_get_days_since(self, username):

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        # Get the old values for ghast tears, and how many days have passed.
        query = """SELECT DAYS_SINCE FROM sb_players WHERE MINECRAFT_USERNAME = %(username)s"""
        cursor.execute(query, {'username': username})

        # Checks if query is empty
        if cursor.rowcount == 0:
            print("Error! Unexpected value in sb_get_days_since function!")
            return None

        # Organizes the data
        data = cursor.fetchall()

        return data[0][0]

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
        url = f"https://api.hypixel.net/v2/skyblock/profile?key={self.sb_api_key}&profile={profile}"
        resp = urllib.request.urlopen(url)
        data = json.load(resp)
        ghast_collection = data["profile"]["members"][player]["collection"]["GHAST_TEAR"]
        return ghast_collection

    async def SkyblockMayorChecker(self):
        url = f"https://api.hypixel.net/v2/resources/skyblock/election?key={self.sb_api_key}"
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
        # Update the skyblock profiles
        self.sb_profiles()

        # Estimated burden of this function is 5 API calls
        url = f"https://api.hypixel.net/v2/skyblock/bazaar?key={self.sb_api_key}"
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
            ranking[i].append(self.sb_players[i][3])
        ranking.sort(reverse=True)
        # This string contains the message that will be sent at the end.
        sb_tracker_msg = ""

        # Lists the ranked ghast collection leaderboard.
        for i in range(len(self.sb_players)):
            # Lists the ghast collections
            sb_tracker_msg += f"{ranking[i][1]} has a ghast collection of {ranking[i][0]}"
            sb_delta = ranking[i][0] - ranking[i][2]
            sb_tracker_msg += f" (+{sb_delta})\n"

            await self.sb_harvest(ranking[i][1], ranking[i][0])

        # Check if a special mayor has been elected
        if mayor not in {"Aatrox", "Cole", "Diana", "Diaz", "Finnegan", "Foxy", "Marina", "Paul"}:
            sb_tracker_msg += f"\n:person_in_tuxedo: Special Mayor {mayor} is in office today.\n"

        # Check if a special mayor is up for election
        try:
            # Assigns all the mayoral candidates
            candidates = []
            for i in [1, 2, 3, 4, 5]:
                candidates.append(mayors[i])
            for candidate in candidates:
                if candidate not in {"Aatrox", "Cole", "Diana", "Diaz", "Finnegan", "Foxy", "Marina", "Paul"}:
                    sb_tracker_msg += f"\n:person_in_tuxedo: Special Mayor {candidate} is up for election.\n"
        except IndexError:
            # No candidates avaliable
            pass

        # Check the days since the last harvest
        days_since = await self.sb_get_days_since("Alpha_A")

        if days_since == 0:
            sb_tracker_msg += "\n:corn: Minions have been harvested recently (< 1 day).\n"
        elif days_since == 1:
            sb_tracker_msg += "\n:seedling: Minions are busy harvesting ghast tears. (1 day).\n"
        elif days_since < 5:
            sb_tracker_msg += f"\n:seedling: Minions are busy harvesting ghast tears. ({days_since} days).\n"
        elif days_since >= 5:
            sb_tracker_msg += f"\n:sunflower: Ghast tears are ready to be harvested! ({days_since} days).\n"

        # Total profit before adding hypercatalysts
        sb_tracker_msg += f"\n:bar_chart: We made {self.human_format(profit_gen)} coins.\n"

        # Check if the estimated profit for using hypercatalysts today was positive
        if profit_hyper > 0:
            sb_tracker_msg += f"\n:chart_with_upwards_trend: Today is PROFITABLE for Hyper Catalysts (+{self.human_format(profit_hyper)} coins)"
        else:
            sb_tracker_msg += f"\n:chart_with_downwards_trend: Today is not profitable for Hyper Catalysts... ({self.human_format(profit_hyper)} coins)"

        return sb_tracker_msg

    #
    #   Commands
    #

    @commands.hybrid_group(name="skyblock", invoke_without_command=True)
    async def skyblock(self, ctx):
        msg = f"""
```
Sure thing boss. Please specify a subcommand to use this feature.
Here is the subcommand list for the 'skyblock' command:
{self.bot.command_prefix}skyblock tracker - Manages the skyblock ghast minion leaderboard tracker.
```
"""
        await ctx.send(msg)

    @skyblock.group(name="tracker", help="manages the skyblock ghast minion leaderboard tracker.", invoke_without_command=True)
    @commands.has_role("Bot Tester")
    async def tracker(self, ctx):
        msg = f"""
```
Sure thing boss. Please specify a subcommand to use this feature.
Here is the subcommand list for the 'tracker' command:
{self.bot.command_prefix}skyblock tracker status - checks on the status of the tracker
{self.bot.command_prefix}skyblock tracker test - sends a test message from the skyblock tracker
```
"""
        await ctx.send(msg)

    @tracker.command(name="status", help="checks to see if the skyblock ghast tear leaderboard checker is running or not")
    @commands.has_role("Bot Tester")
    async def status(self, ctx):
        try:
            if self.SkyblockTrackerLoop.is_running() is True:
                await ctx.send("The Skyblock Tracker is currently running.")
            else:
                await ctx.send("The Skyblock Tracker is currently offline.")
        except Exception as e:
            await ctx.send(f"Oh no! I'm not able to check the status of the skyblock tracker right now...\nHere is the error: {e}")
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

        except Exception as e:
            await ctx.send(f"Oh no! I'm not able to use the skyblock tracker tester right now...\nHere is the error: {e}")
            return

        await ctx.send("Sent a test message to the tracker channel!")

    @tasks.loop(hours=23)
    async def SkyblockTrackerLoop(self):
        await asyncio.sleep(self.seconds_until(18, 00))

        attempts = 0

        try:
            # Increment the days since last harvest by 1.
            await self.sb_increment_days_since()

        except Exception as e:
            print("Exception occured during skyblock loop: ", str(e))

        # Loop until successfully run.
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

                # Quit if more than 30 attempts fail
                if attempts < 30:
                    attempts += 1
                    continue
                else:
                    break

            break

        await asyncio.sleep(60)
