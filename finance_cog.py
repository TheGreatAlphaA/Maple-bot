
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

        self.av_api_key = str(self.config['FINANCE']['alpha_vantage_api_key'])
        self.gold_api_key = str(self.config['FINANCE']['gold_api_key'])

        self.stock_channel = int(self.config['DISCORD_CHANNELS']['stock_tracker'])

        self.stock_tickers = ["GME", "TSM"]
        # "GME", "NVDA", "MSFT", "IBM", "TSM", "AMD", "MU", "FSLR", "IONQ"

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

    # ==================================================================================== #
    #                                      COMMANDS                                        #
    # ==================================================================================== #

    @commands.hybrid_command(name="stock", help="gets the daily stock price for the selected stock ticker")
    @commands.is_owner()
    async def stock(self, ctx, stock_ticker=None):
        message = await ctx.send("Processing...")
        try:

            if stock_ticker is None:
                stock_ticker = "MSFT"

            # Get the message contents
            stock_info = await self.StockTracker(stock_ticker)

            # stock_symbol = stock_info["Global Quote"]["01. symbol"]
            # stock_open = stock_info["Global Quote"]["02. open"]
            # stock_high = stock_info["Global Quote"]["03. high"]
            # stock_low = stock_info["Global Quote"]["04. low"]
            stock_price = float(stock_info["Global Quote"]["05. price"])
            # stock_volume = stock_info["Global Quote"]["06. volume"]
            # stock_lastest_trade_day = stock_info["Global Quote"]["07. latest trading day"]
            # stock_previous_close = stock_info["Global Quote"]["08. previous close"]
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
            await message.edit(msg)

        except Exception as e:
            print(f"Exception occured during command: /stock: {e}")
            await message.edit(content=f"Oops! I couldn't run the /stock command: {e}")
            return

    @commands.hybrid_command(name="metal", help="gets the daily market price for the selected metal type")
    @commands.is_owner()
    async def metal(self, ctx, metal=None):
        message = await ctx.send("Processing...")
        try:

            if metal is None:
                metal = "gold"

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
            await message.edit(msg)

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
                    stock_ticker = "GME"

                    # Get the message contents
                    stock_info = await self.StockTracker(stock_ticker)

                    stock_price = float(stock_info["Global Quote"]["05. price"])

                    target_min = 36.62

                    # Check if the current investment is positive for Gamestop
                    if stock_price > target_min:
                        msg += f":chart_with_upwards_trend: Target goal REACHED for {stock_ticker.upper()}! Current price is (+${stock_price})\n\n"

                except Exception as e:
                    print(f"Exception occured during function: StockTrackerLoop(): {e}")

                try:
                    metal = "silver"

                    # Get the message contents
                    metal_info = await self.GoldSilverTracker(metal)

                    metal_price = float(metal_info["price"])

                    target_min = 50.00

                    if metal_price > target_min:
                        msg += f":chart_with_upwards_trend: Target goal REACHED for {metal.title()}! Current price is (+${metal_price})\n\n"

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
