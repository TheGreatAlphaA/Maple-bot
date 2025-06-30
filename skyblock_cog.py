
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
    # ==================================================================================== #
    #                                     DEFINITIONS                                      #
    # ==================================================================================== #
    def __init__(self, bot):
        self.bot = bot
        
        # Config File
        self.config = configparser.ConfigParser()
        self.config.read("info.ini")

        # MySQL Database
        self.db_host = self.config['DATABASE']['host']
        self.db_user = self.config['DATABASE']['user']
        self.db_password = self.config['DATABASE']['password']
        self.db_database = self.config['DATABASE']['database']

        # This is the api key for accessing the Hypixel API
        self.sb_api_key = self.config['SKYBLOCK']['hypixel_api_key']

        # This is the item data for the tracked collection
        self.sb_item_name = self.config['SKYBLOCK']['item_name']
        self.sb_e_item_name = self.config['SKYBLOCK']['enchanted_item_name']

        # This is the minion harvest tracking data
        self.minion_output = float(self.config['SKYBLOCK']['minion_output'])
        self.minion_storage = float(self.config['SKYBLOCK']['minion_storage_slots'])
        self.minion_fuel_boost = int(self.config['SKYBLOCK']['minion_fuel_boost'])
        self.minion_upgrade_slot_boost = int(self.config['SKYBLOCK']['minion_upgrade_slot_boost'])
        self.minion_beacon_boost = int(self.config['SKYBLOCK']['minion_beacon_boost'])
        self.minion_infusion_boost = int(self.config['SKYBLOCK']['minion_infusion_boost'])

        if self.minion_fuel_boost > 100:
            self.minion_total_boost = (self.minion_fuel_boost / 100) * ((100 + self.minion_upgrade_slot_boost + self.minion_beacon_boost + self.minion_infusion_boost) / 100)
        else:
            self.minion_total_boost = (self.minion_fuel_boost + 100 + self.minion_upgrade_slot_boost + self.minion_beacon_boost + self.minion_infusion_boost) / 100

        self.number_of_minions = int(self.config['SKYBLOCK']['number_of_minions'])

        # This is the channel that our notifications will be posted to.
        self.sb_channel = int(self.config['DISCORD_CHANNELS']['skyblock_tracker'])

        # Start the loop
        self.enabled = self.config['BOT']['enable_skyblock_tracker']

        if self.enabled == "TRUE":
            self.SkyblockTrackerLoop.start()

    # ==================================================================================== #
    #                                      FUNCTIONS                                       #
    # ==================================================================================== #

    def seconds_until(self, hours, minutes):
        given_time = datetime.time(hours, minutes)
        now = datetime.datetime.now()
        future_exec = datetime.datetime.combine(now, given_time)
        if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
            future_exec = datetime.datetime.combine(now + datetime.timedelta(days=1), given_time)  # days always >= 0

        return (future_exec - now).total_seconds()

    def human_format(self, num):
        num = float('{:.3g}'.format(num))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

    def SkyblockGetPlayerDatabaseData(self):
        # Creates an empty list
        players_data = []

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        query = """SELECT MINECRAFT_USERNAME, MINECRAFT_UUID, SKYBLOCK_UUID, COLLECTION FROM sb_players"""
        cursor.execute(query)

        # Checks if query is empty
        if cursor.rowcount == 0:
            return None

        # Creates each table body
        player_data = cursor.fetchall()

        for i in range(len(player_data)):
            # Assign friendly names to the data
            minecraft_username = player_data[i][0]
            minecraft_uuid = player_data[i][1]
            skyblock_uuid = player_data[i][2]
            collection = player_data[i][3]

            player_dict = {
                "minecraft_username": minecraft_username,
                "minecraft_uuid": minecraft_uuid,
                "skyblock_uuid": skyblock_uuid,
                "collection": collection

            }

            players_data.append(player_dict)

        return players_data

    def SkyblockUpdatePlayerDatabaseData(self, username, collection_total):

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        # Get the old values for total collection.
        query = """SELECT COLLECTION FROM sb_players WHERE MINECRAFT_USERNAME = %(username)s"""
        cursor.execute(query, {'username': username})

        # Checks if query is empty
        if cursor.rowcount == 0:
            print("Error! Unexpected value in SkyblockUpdatePlayerDatabaseData function!")
            return None

        # Organizes the data
        yesterdays_harvest = cursor.fetchall()

        yesterdays_collection_total = yesterdays_harvest[0][0]

        # If today's total collection is higher than yesterday's, update the total collection and days since last harvest
        if collection_total > yesterdays_collection_total:

            # Update the player's current total collection
            query = """UPDATE sb_players SET COLLECTION = %(collection_total)s WHERE MINECRAFT_USERNAME = %(username)s"""
            cursor.execute(query, {'username': username, 'collection_total': collection_total})

            # Reset the days since last harvest
            days_since_last_harvest = 0

            query = """UPDATE sb_players SET DAYS_SINCE = %(days_since_last_harvest)s WHERE MINECRAFT_USERNAME = %(username)s"""
            cursor.execute(query, {'username': username, 'days_since_last_harvest': days_since_last_harvest})

            # Commit changes to database
            mydb.commit()

        elif collection_total < yesterdays_collection_total:
            print("Error! Unexpected value in SkyblockUpdatePlayerDatabaseData function!")

    def SkyblockGetItemCollection(self, player, profile):
        url = f"https://api.hypixel.net/v2/skyblock/profile?key={self.sb_api_key}&profile={profile}"
        resp = urllib.request.urlopen(url)
        data = json.load(resp)

        try:
            # Get the item collection data for the requested player.
            collection = data["profile"]["members"][player]["collection"][self.sb_item_name]
        except KeyError:
            collection = -1

        return collection

    def SkyblockGetBazaarData(self):
        url = f"https://api.hypixel.net/v2/skyblock/bazaar?key={self.sb_api_key}"
        resp = urllib.request.urlopen(url)
        bazaar_data = json.load(resp)

        return bazaar_data

    def SkyblockGetMayorData(self):
        url = f"https://api.hypixel.net/v2/resources/skyblock/election?key={self.sb_api_key}"
        resp = urllib.request.urlopen(url)
        data = json.load(resp)

        mayor_data = []

        # Append the currently elected mayor
        mayor_data.append(data["mayor"]["name"])

        # Append the mayors up for election
        try:
            for i in range(5):
                mayor_data.append(data["current"]["candidates"][i]["name"])
        except KeyError:
            # Mayor election are not open yet!
            pass

        return mayor_data

    def SkyblockGeneralProfitabilityChecker(self, mayor, bazaar_data):
        instant_sell_price = bazaar_data["products"][self.sb_e_item_name]["quick_status"]["sellPrice"]
        hypercatalyst_buy_order = bazaar_data["products"]["HYPER_CATALYST"]["quick_status"]["buyPrice"]
        catalyst_buy_order = bazaar_data["products"]["CATALYST"]["quick_status"]["buyPrice"]
        tasty_cheese_buy_order = bazaar_data["products"]["CHEESE_FUEL"]["quick_status"]["buyPrice"]
        foul_flesh_buy_order = bazaar_data["products"]["FOUL_FLESH"]["quick_status"]["buyPrice"]
        hamster_wheel_buy_order = bazaar_data["products"]["HAMSTER_WHEEL"]["quick_status"]["buyPrice"]
        scorched_power_crystal_buy_order = bazaar_data["products"]["SCORCHED_POWER_CRYSTAL"]["quick_status"]["buyPrice"]
        power_crystal_buy_order = bazaar_data["products"]["POWER_CRYSTAL"]["quick_status"]["buyPrice"]

        if mayor == "Derpy":
            # Doubled output when Derpy is mayor
            daily_gross = self.minion_output * self.minion_total_boost * self.number_of_minions * instant_sell_price * 2 * 0.99
        else:
            daily_gross = self.minion_output * self.minion_total_boost * self.number_of_minions * instant_sell_price * 0.99

        if (self.minion_beacon_boost % 2 != 0) and (self.minion_beacon_boost > 0):
            if self.minion_fuel_boost == 400:
                daily_expense = (4 * self.number_of_minions * hypercatalyst_buy_order) + (scorched_power_crystal_buy_order / 2)
            elif self.minion_fuel_boost == 300:
                daily_expense = (8 * self.number_of_minions * catalyst_buy_order) + (scorched_power_crystal_buy_order / 2)
            elif self.minion_fuel_boost == 200:
                daily_expense = (24 * self.number_of_minions * tasty_cheese_buy_order) + (scorched_power_crystal_buy_order / 2)
            elif self.minion_fuel_boost == 90:
                daily_expense = (5 * self.number_of_minions * foul_flesh_buy_order) + (scorched_power_crystal_buy_order / 2)
            elif self.minion_fuel_boost == 50:
                daily_expense = (1 * self.number_of_minions * hamster_wheel_buy_order) + (scorched_power_crystal_buy_order / 2)
            else:
                daily_expense = scorched_power_crystal_buy_order / 2
        elif (self.minion_beacon_boost % 2 == 0) and (self.minion_beacon_boost > 0):
            if self.minion_fuel_boost == 400:
                daily_expense = (4 * self.number_of_minions * hypercatalyst_buy_order) + (power_crystal_buy_order / 2)
            elif self.minion_fuel_boost == 300:
                daily_expense = (8 * self.number_of_minions * catalyst_buy_order) + (power_crystal_buy_order / 2)
            elif self.minion_fuel_boost == 200:
                daily_expense = (24 * self.number_of_minions * tasty_cheese_buy_order) + (power_crystal_buy_order / 2)
            elif self.minion_fuel_boost == 90:
                daily_expense = (5 * self.number_of_minions * foul_flesh_buy_order) + (power_crystal_buy_order / 2)
            elif self.minion_fuel_boost == 50:
                daily_expense = (1 * self.number_of_minions * hamster_wheel_buy_order) + (power_crystal_buy_order / 2)
            else:
                daily_expense = power_crystal_buy_order / 2
        else:
            if self.minion_fuel_boost == 400:
                daily_expense = 4 * self.number_of_minions * hypercatalyst_buy_order
            elif self.minion_fuel_boost == 300:
                daily_expense = 8 * self.number_of_minions * catalyst_buy_order
            elif self.minion_fuel_boost == 200:
                daily_expense = 24 * self.number_of_minions * tasty_cheese_buy_order
            elif self.minion_fuel_boost == 90:
                daily_expense = 5 * self.number_of_minions * foul_flesh_buy_order
            elif self.minion_fuel_boost == 50:
                daily_expense = 1 * self.number_of_minions * hamster_wheel_buy_order
            else:
                daily_expense = 0

        daily_net = daily_gross - daily_expense
        
        return int(daily_net)

    def SkyblockBaselineProfitabilityChecker(self, mayor, bazaar_data):
        instant_sell_price = bazaar_data["products"][self.sb_e_item_name]["quick_status"]["sellPrice"]
        scorched_power_crystal_buy_order = bazaar_data["products"]["SCORCHED_POWER_CRYSTAL"]["quick_status"]["buyPrice"]
        power_crystal_buy_order = bazaar_data["products"]["POWER_CRYSTAL"]["quick_status"]["buyPrice"]

        minion_fuel_boost = 35

        boost = (minion_fuel_boost + 100 + self.minion_upgrade_slot_boost + self.minion_beacon_boost + self.minion_infusion_boost) / 100

        if mayor == "Derpy":
            # Doubled output when Derpy is mayor
            daily_gross = self.minion_output * boost * self.number_of_minions * instant_sell_price * 2 * 0.99
        else:
            daily_gross = self.minion_output * boost * self.number_of_minions * instant_sell_price * 0.99

        if (self.minion_beacon_boost % 2 != 0) and (self.minion_beacon_boost > 0):
            daily_expense = scorched_power_crystal_buy_order / 2
        elif (self.minion_beacon_boost % 2 == 0) and (self.minion_beacon_boost > 0):
            daily_expense = power_crystal_buy_order / 2
        else:
            daily_expense = 0

        daily_net = daily_gross - daily_expense
        
        return int(daily_net)

    def SkyblockHyperCatalystProfitabilityChecker(self, mayor, bazaar_data):
        instant_sell_price = bazaar_data["products"][self.sb_e_item_name]["quick_status"]["sellPrice"]
        hypercatalyst_buy_order = bazaar_data["products"]["HYPER_CATALYST"]["quick_status"]["buyPrice"]
        scorched_power_crystal_buy_order = bazaar_data["products"]["SCORCHED_POWER_CRYSTAL"]["quick_status"]["buyPrice"]
        power_crystal_buy_order = bazaar_data["products"]["POWER_CRYSTAL"]["quick_status"]["buyPrice"]

        minion_fuel_boost = 400

        boost = (minion_fuel_boost / 100) * ((100 + self.minion_upgrade_slot_boost + self.minion_beacon_boost + self.minion_infusion_boost) / 100)

        if mayor == "Derpy":
            # Doubled output when Derpy is mayor
            daily_gross = self.minion_output * boost * self.number_of_minions * instant_sell_price * 2 * 0.99
        else:
            daily_gross = self.minion_output * boost * self.number_of_minions * instant_sell_price * 0.99

        if (self.minion_beacon_boost % 2 != 0) and (self.minion_beacon_boost > 0):
            daily_expense = (4 * self.number_of_minions * hypercatalyst_buy_order) + (scorched_power_crystal_buy_order / 2)
        elif (self.minion_beacon_boost % 2 == 0) and (self.minion_beacon_boost > 0):
            daily_expense = (4 * self.number_of_minions * hypercatalyst_buy_order) + (power_crystal_buy_order / 2)
        else:
            daily_expense = 4 * self.number_of_minions * hypercatalyst_buy_order

        # Net profit for hypercatalysts needs to exceed baseline profit, otherwise, we would still make more money without them
        baseline = self.SkyblockBaselineProfitabilityChecker(mayor, bazaar_data)
        daily_net = daily_gross - daily_expense - baseline
        
        return int(daily_net)

    # ==================================================================================== #
    #                                    MAIN FUNCTION                                     #
    # ==================================================================================== #

    def SkyblockTracker(self):
        # This string contains the message that will be sent at the end.
        sb_tracker_msg = ""

        # Get the player data from the database
        players_data = self.SkyblockGetPlayerDatabaseData()

        # If no players in database
        if players_data is None:
            sb_tracker_msg += "Not tracking any players currently. Please set up at least one player in the database before enabling the skyblock tracker."
            return sb_tracker_msg

        # Request API Data
        bazaar_data = self.SkyblockGetBazaarData()
        mayor_data = self.SkyblockGetMayorData()

        # Assigns the currently elected mayor
        elected_mayor = mayor_data[0]

        # Calculates the estimates profit for today.
        daily_profit_gen = self.SkyblockGeneralProfitabilityChecker(elected_mayor, bazaar_data)
        daily_profit_hyper = self.SkyblockHyperCatalystProfitabilityChecker(elected_mayor, bazaar_data)

        # List of players to be ranked
        players = []

        # Compiles the collection data for all players being tracked
        for i in range(len(players_data)):
            # Assign friendly names to the data
            minecraft_username = players_data[i]["minecraft_username"]
            minecraft_uuid = players_data[i]["minecraft_uuid"]
            skyblock_uuid = players_data[i]["skyblock_uuid"]
            yesterdays_collection = players_data[i]["collection"]

            # Request API Data
            collection = self.SkyblockGetItemCollection(minecraft_uuid, skyblock_uuid)

            player_dict = {
                "minecraft_username": minecraft_username,
                "collection": collection,
                "yesterdays_collection": yesterdays_collection
            }

            players.append(player_dict)

        # Sort the list of players by their collection
        player_ranking = sorted(players, key=lambda d: d['collection'], reverse=True)

        # Lists the ranked collection leaderboard.
        for j in range(len(player_ranking)):
            # Assign friendly names to the data
            minecraft_username = player_ranking[j]['minecraft_username']
            collection = player_ranking[j]['collection']
            yesterdays_collection = player_ranking[j]['yesterdays_collection']
            sb_delta = collection - yesterdays_collection

            collection_name_pretty = self.sb_item_name.lower().replace("_", " ")

            # Lists the collections
            if j == 0:
                sb_tracker_msg += f":first_place: {minecraft_username} has a {collection_name_pretty} collection total of {collection} (+{sb_delta})\n"
            elif j == 1:
                sb_tracker_msg += f":second_place: {minecraft_username} has a {collection_name_pretty} collection total of {collection} (+{sb_delta})\n"
            elif j == 2:
                sb_tracker_msg += f":third_place: {minecraft_username} has a {collection_name_pretty} collection total of {collection} (+{sb_delta})\n\n"
            elif collection > 0:
                sb_tracker_msg += f"{minecraft_username} has a {collection_name_pretty} collection total of {collection} (+{sb_delta})\n"
            else:
                sb_tracker_msg += f":bangbang: {minecraft_username} has turned off their API! Last known collection is {yesterdays_collection}\n"

            if collection > 0:
                # Update the SQL Database
                self.SkyblockUpdatePlayerDatabaseData(minecraft_username, collection)

        # Check if a special mayor has been elected
        if elected_mayor not in {"Aatrox", "Cole", "Diana", "Diaz", "Finnegan", "Foxy", "Marina", "Paul"}:
            sb_tracker_msg += f"\n:person_in_tuxedo: Special Mayor {elected_mayor} is in office today.\n"

        # Check if a special mayor is up for election
        try:
            # Assigns all the mayoral candidates
            candidates = []
            for i in [1, 2, 3, 4, 5]:
                candidates.append(mayor_data[i])
            for candidate in candidates:
                if candidate not in {"Aatrox", "Cole", "Diana", "Diaz", "Finnegan", "Foxy", "Marina", "Paul"}:
                    sb_tracker_msg += f"\n:person_in_tuxedo: Special Mayor {candidate} is up for election.\n"
        except IndexError:
            # No candidates avaliable
            pass

        # Track the first account in the database when updating the minion harvest tracker
        minion_owner = players_data[0]["minecraft_username"]

        # Estimate the time until the next harvest
        if elected_mayor is "Derpy":
            days_between = int((((self.minion_storage * 64) - 128) / (self.minion_output * self.minion_total_boost)) / 2)
        else:
            days_between = int(((self.minion_storage * 64) - 128) / (self.minion_output * self.minion_total_boost))


        # Check the days since the last harvest
        try:
            # Connect to the database
            mydb = mysql.connector.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_database
            )

            cursor = mydb.cursor(buffered=True)

            # Get how many days have passed since the last harvest.
            query = """SELECT DAYS_SINCE FROM sb_players WHERE MINECRAFT_USERNAME = %(username)s"""
            cursor.execute(query, {'username': minion_owner})

            # Organizes the data
            data = cursor.fetchall()

            days_since = data[0][0]

            number_of_days_remaining = int(days_between - days_since)

        except IndexError:
            days_since = None
            number_of_days_remaining = None

        # If there is more than one day until harvest
        if days_since == 0 and number_of_days_remaining > 1:
            sb_tracker_msg = f":corn: Minions have been harvested recently ({number_of_days_remaining} days until harvest).\n\n" + sb_tracker_msg
        elif number_of_days_remaining > 1:
            sb_tracker_msg = f"\n:seedling: Minions are busy harvesting items. ({number_of_days_remaining} days until harvest).\n\n" + sb_tracker_msg

        # If there is one day until harvest
        elif days_since == 0 and number_of_days_remaining == 1:
            sb_tracker_msg = f"\n:corn: Minions have been harvested recently ({number_of_days_remaining} day until harvest).\n\n" + sb_tracker_msg
        elif number_of_days_remaining == 1:
            sb_tracker_msg = f"\n:seedling: Minions are busy harvesting items. ({number_of_days_remaining} day until harvest).\n\n" + sb_tracker_msg

        # If the harvest date is today:
        elif number_of_days_remaining == 0:
            sb_tracker_msg = "\n:sunflower: Items are ready to be collected! (Filled recently!).\n\n" + sb_tracker_msg

        # If the harvest date was yesterday
        elif number_of_days_remaining == -1:
            sb_tracker_msg = f"\n:sunflower: Items are ready to be collected! ({abs(number_of_days_remaining)} day since filled).\n\n" + sb_tracker_msg

        # If the harvest date is past the expected date
        elif number_of_days_remaining < -1:
            sb_tracker_msg = f"\n:sunflower: Items are ready to be collected! ({abs(number_of_days_remaining)} days since filled).\n\n" + sb_tracker_msg

        # Total profit based on the provided parameters
        sb_tracker_msg += f"\n:bar_chart: We made {self.human_format(daily_profit_gen)} coins.\n"

        # Check if the estimated profit for using hypercatalysts today was positive
        if daily_profit_hyper > 0:
            sb_tracker_msg += f"\n:chart_with_upwards_trend: Today is PROFITABLE for Hyper Catalysts (+{self.human_format(daily_profit_hyper)} coins)"
        else:
            sb_tracker_msg += f"\n:chart_with_downwards_trend: Today is not profitable for Hyper Catalysts... ({self.human_format(daily_profit_hyper)} coins)"

        return sb_tracker_msg

    # ==================================================================================== #
    #                                      COMMANDS                                        #
    # ==================================================================================== #

    @commands.hybrid_group(name="skyblock", invoke_without_command=True)
    async def skyblock(self, ctx):
        try:
            msg = f"""
```
Sure thing boss. Please specify a subcommand to use this feature.
Here is the subcommand list for the 'skyblock' command:
{self.bot.command_prefix}skyblock tracker - Manages the skyblock collection leaderboard tracker.
```
"""
            await ctx.send(msg)

        except Exception as e:
            print(f"Exception occured during command: /skyblock: {e}")
            await ctx.send(f"Oops! I couldn't run the /skyblock command: {e}")
            return

    @skyblock.group(name="tracker", help="manages the skyblock collection leaderboard tracker.", invoke_without_command=True)
    @commands.has_role("Bot Tester")
    async def tracker(self, ctx):
        try:
            msg = f"""
```
Sure thing boss. Please specify a subcommand to use this feature.
Here is the subcommand list for the 'tracker' command:
{self.bot.command_prefix}skyblock tracker status - checks on the status of the tracker
{self.bot.command_prefix}skyblock tracker test - sends a test message from the skyblock tracker
```
"""
            await ctx.send(msg)

        except Exception as e:
            print(f"Exception occured during command: /skyblock tracker: {e}")
            await ctx.send(f"Oops! I couldn't run the /skyblock tracker command: {e}")
            return

    @tracker.command(name="status", help="checks to see if the skyblock collection leaderboard checker is running or not")
    @commands.has_role("Bot Tester")
    async def status(self, ctx):
        message = await ctx.send("Processing...")
        try:
            if self.SkyblockTrackerLoop.is_running() is True:
                await message.edit(content="The Skyblock Tracker is currently running.")
            else:
                await message.edit(content="The Skyblock Tracker is currently offline.")

        except Exception as e:
            print(f"Exception occured during command: /skyblock tracker status: {e}")
            await message.edit(content=f"Oops! I couldn't run the /skyblock tracker status command: {e}")
            return

    @tracker.command(name="test", help="sends a test message to the skyblock tracker channel")
    @commands.has_role("Bot Tester")
    async def test(self, ctx):
        message = await ctx.send("Processing...")
        try:
            # Get the channel object from discord
            channel = self.bot.get_channel(self.sb_channel)

            # Get the message contents
            msg = self.SkyblockTracker()

            # Sends the final report to the tracker channel
            await channel.send(msg)

            await message.edit(content="Sent a test message to the tracker channel!")

        except Exception as e:
            print(f"Exception occured during command: /skyblock tracker test: {e}")
            await message.edit(content=f"Oops! I couldn't run the /skyblock tracker test command: {e}")
            return

    # ==================================================================================== #
    #                                      MAIN LOOP                                       #
    # ==================================================================================== #

    @tasks.loop(hours=23)
    async def SkyblockTrackerLoop(self):
        await asyncio.sleep(self.seconds_until(18, 00))

        attempts = 0

        try:
            # Connect to the database
            mydb = mysql.connector.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_database
            )

            cursor = mydb.cursor(buffered=True)

            # Increment the days since last harvest by 1.
            query = """UPDATE sb_players SET DAYS_SINCE = DAYS_SINCE + 1"""
            cursor.execute(query)

            # Commit changes to database
            mydb.commit()

        except Exception as e:
            print(f"Exception occured during function: SkyblockTrackerLoop(): {e}")

        # Loop until successfully run.
        while True:
            try:

                # Get the channel object from discord
                channel = self.bot.get_channel(self.sb_channel)

                # Get the message contents
                msg = self.SkyblockTracker()

                # Sends the final report to the tracker channel
                await channel.send(msg)

            except Exception as e:
                print(f"Exception occured during function: SkyblockTrackerLoop(): {e}")
                await asyncio.sleep(20)

                # Quit if more than 30 attempts fail
                if attempts < 30:
                    attempts += 1
                    continue
                else:
                    break

            break

        await asyncio.sleep(60)

    @SkyblockTrackerLoop.before_loop
    async def before_SkyblockTrackerLoop(self):
        await self.bot.wait_until_ready()
