
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
    import mysql.connector
except ModuleNotFoundError:
    print("Please install mysql-connector. (pip install mysql-connector-python)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    import urllib.request
except ModuleNotFoundError:
    print("Please install urllib. (pip install urllib3)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    from discord.ext import commands, tasks
except ModuleNotFoundError:
    print("Please install discordpy. (pip install discord.py)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    import configparser
except ModuleNotFoundError:
    print("Please install configparser. (pip install configparser)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")


class finance_cog(commands.Cog):
    # ==================================================================================== #
    #                                     DEFINITIONS                                      #
    # ==================================================================================== #
    def __init__(self, bot):
        self.bot = bot
        
        self.config = configparser.ConfigParser()
        self.config.read("info.ini")

        self.db_host = self.config['DATABASE']['host']
        self.db_user = self.config['DATABASE']['user']
        self.db_password = self.config['DATABASE']['password']
        self.db_database = self.config['DATABASE']['database']

        self.av_api_key = str(self.config['FINANCE']['alpha_vantage_api_key'])
        self.gold_api_key = str(self.config['FINANCE']['gold_api_key'])

        self.stock_channel = int(self.config['DISCORD_CHANNELS']['stock_tracker'])

        # Start the loop
        self.enabled = self.config['BOT']['enable_finance_tracker']
        
        if self.enabled == "TRUE":
            self.StockTrackerLoop.start()

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

    async def StockTracker(self, stock_ticker):

        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock_ticker}&apikey={self.av_api_key}"
        resp = urllib.request.urlopen(url)
        stock_info = json.load(resp)

        return stock_info

    async def GoldSilverTracker(self, metal):

        if metal.lower() in ("gold", "xau"):
            symbol = "XAU"
        elif metal.lower() in ("silver", "xag"):
            symbol = "XAG"
        elif metal.lower() in ("platinum", "xpt"):
            symbol = "XPT"
        elif metal.lower() in ("palladium", "xpd"):
            symbol = "XPD"

        currency = "USD"
        date = ""

        url = f"https://www.goldapi.io/api/{symbol}/{currency}{date}"
        req = urllib.request.Request(url)
        req.add_header('x-access-token', self.gold_api_key)
        req.add_header('Content-Type', 'application/json')
        resp = urllib.request.urlopen(req)
        metal_info = json.load(resp)

        return metal_info

    def Stock_GetAll(self, type):

        stock_data = []

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        # Get the old values for total collection.
        query = """SELECT TICKER, TARGET_BUY, TARGET_SELL FROM finance_stocks WHERE TYPE = %(type)s"""
        cursor.execute(query, {'type': type})

        # Checks if query is empty
        if cursor.rowcount == 0:
            return stock_data

        # Organizes the data
        data = cursor.fetchall()

        for i in range(len(data)):
            # Assign friendly names to the data
            ticker = data[i][0]
            target_buy = data[i][1]
            target_sell = data[i][2]

            # Defines the list of youtube channels
            stock_dict = {
                "ticker": ticker,
                "target_buy": target_buy,
                "target_sell": target_sell
            }

            stock_data.append(stock_dict)

        return stock_data

    # ==================================================================================== #
    #                                      COMMANDS                                        #
    # ==================================================================================== #

    @commands.hybrid_command(name="stock", help="gets the daily stock price for the selected stock ticker")
    @commands.is_owner()
    async def stock(self, ctx, stock_ticker):
        message = await ctx.send("Processing...")
        try:

            # Get the message contents
            stock_info = await self.StockTracker(stock_ticker)

            stock_price = float(stock_info["Global Quote"]["05. price"])
            stock_change_price = float(stock_info["Global Quote"]["09. change"])
            stock_change_percent = stock_info["Global Quote"]["10. change percent"]

            # This string contains the message that will be sent at the end.
            msg = ""

            msg += f"{stock_ticker.upper()} is currently trading at ${stock_price}\n\n"

            if stock_change_price > 0.00:
                msg += f":chart_with_upwards_trend: Daily trend is positive (+{stock_change_price}) (+{stock_change_percent})"
            elif stock_change_price < 0.00:
                msg += f":chart_with_downwards_trend: Daily trend is negative ({stock_change_price}) ({stock_change_percent})"
            else:
                msg += f":bar_chart: Daily trend is neutral (+{stock_change_price}) (+{stock_change_percent})"

            msg += f" [Yahoo Finance](<https://finance.yahoo.com/quote/{stock_ticker}/>)"

            # Sends the final report
            await message.edit(content=msg)

        except Exception as e:
            print(f"Exception occured during command: /stock: {e}")
            await message.edit(content=f"Oops! I couldn't run the /stock command: {e}")
            return

    @commands.hybrid_command(name="metal", help="gets the daily market price for the selected metal type")
    @commands.is_owner()
    async def metal(self, ctx, metal):
        message = await ctx.send("Processing...")
        try:

            # Get the message contents
            metal_info = await self.GoldSilverTracker(metal)

            metal_price = float(metal_info["price"])
            metal_change_price = float(metal_info["ch"])
            metal_change_percent = metal_info["chp"]

            # This string contains the message that will be sent at the end.
            msg = ""

            msg += f"{metal.title()} is currently trading at ${metal_price}\n\n"

            if metal_change_price > 0.00:
                msg += f":chart_with_upwards_trend: Daily trend is positive (+{metal_change_price}) (+{metal_change_percent}%)"
            elif metal_change_price < 0.00:
                msg += f":chart_with_downwards_trend: Daily trend is negative ({metal_change_price}) ({metal_change_percent}%)"
            else:
                msg += f":bar_chart: Daily trend is neutral (+{metal_change_price}) (+{metal_change_percent}%)"

            # Sends the final report
            await message.edit(content=msg)

        except Exception as e:
            print(f"Exception occured during command: /metal: {e}")
            await message.edit(content=f"Oops! I couldn't run the /metal command: {e}")
            return

    # ==================================================================================== #
    #                                      MAIN LOOP                                       #
    # ==================================================================================== #

    @tasks.loop(hours=23)
    async def StockTrackerLoop(self):
        await asyncio.sleep(self.seconds_until(18, 00))
        while True:
            try:

                # This string contains the message that will be sent at the end.
                msg = ""

                # Get the channel object from discord
                channel = self.bot.get_channel(self.stock_channel)

                try:

                    stock_data = self.Stock_GetAll("stock")

                    for i in range(len(stock_data)):

                        stock_ticker = stock_data[i]["ticker"]
                        target_buy = stock_data[i]["target_buy"]
                        target_sell = stock_data[i]["target_sell"]

                        # Get the most recent stock information
                        stock_info = await self.StockTracker(stock_ticker)

                        stock_price = float(stock_info["Global Quote"]["05. price"])

                        # Check if the stock has reached the target buy price
                        if stock_price < target_buy:
                            msg += f":chart_with_downwards_trend: {stock_ticker.upper()} has reached the target buy price! Current price is (+${stock_price})\n\n"

                        # Check if the stock has reached the target sell price
                        elif stock_price > target_sell:
                            msg += f":chart_with_upwards_trend: {stock_ticker.upper()} has reached the target sell price! Current price is (+${stock_price})\n\n"

                except Exception as e:
                    print(f"Exception occured during function: StockTrackerLoop(): {e}")

                try:

                    metal_data = self.Stock_GetAll("metal")

                    for i in range(len(metal_data)):

                        metal = metal_data[i]["ticker"]
                        target_buy = metal_data[i]["target_buy"]
                        target_sell = metal_data[i]["target_sell"]

                        # Get the most recent stock information
                        metal_info = await self.GoldSilverTracker(metal)

                        metal_price = float(metal_info["price"])

                        # Check if the stock has reached the target buy price
                        if metal_price < target_buy:
                            msg += f":chart_with_downwards_trend: {metal.title()} has reached the target buy price! Current price is (+${metal_price})\n\n"

                        # Check if the stock has reached the target sell price
                        elif metal_price > target_sell:
                            msg += f":chart_with_upwards_trend: {metal.title()} has reached the target sell price! Current price is (+${metal_price})\n\n"

                except Exception as e:
                    print(f"Exception occured during function: StockTrackerLoop(): {e}")

                # Sends the final report to the tracker channel
                if msg != "":
                    await channel.send(msg)

            except Exception as e:
                print(f"Exception occured during function: StockTrackerLoop(): {e}")
                await asyncio.sleep(600)
                continue
            break
        await asyncio.sleep(60)
