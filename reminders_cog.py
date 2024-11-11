
import sys
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
    import configparser
except ModuleNotFoundError:
    print("Please install configparser. (pip install configparser)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    import dateparser
except ModuleNotFoundError:
    print("Please install dateparser. (pip install dateparser)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    import discord
    from discord.ext import commands, tasks
except ModuleNotFoundError:
    print("Please install discordpy. (pip install discord.py)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    from humanfriendly import format_timespan
except ModuleNotFoundError:
    print("Please install humanfriendly. (pip install humanfriendly)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")


class reminders_cog(commands.Cog):
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

        self.RemindersTrackerLoop.start()

    # ==================================================================================== #
    #                                      FUNCTIONS                                       #
    # ==================================================================================== #

    def Reminders_ParseTime(self, time_string):
        try:
            date_time = dateparser.parse(
                time_string,
                languages=['en'],
                settings={"PREFER_DATES_FROM": 'future'})
        except Exception as e:
            date_time = None
            print("Here is the error: ", str(e))
            return

        return date_time

    def Reminders_UpdateDatabase(self, reminder, author, message):

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        query = """INSERT INTO reminders (REMINDER, AUTHOR, MESSAGE) VALUES (%(reminder)s, %(author)s, %(message)s)"""
        cursor.execute(query, {'reminder': reminder, 'author': author, 'message': message})

        # Commit changes to database
        mydb.commit()

    async def Reminders_FiveMinuteTimer(self, ctx, reminder, time_until, message):

        timer = await ctx.send(f"I will remind you in {format_timespan(time_until+1)}.")

        now = datetime.datetime.now()
        time_remaining = (reminder - now).total_seconds()
        last_time_remaining = 0

        while time_remaining > 0:
            await asyncio.sleep(0.4)
            now = datetime.datetime.now()
            time_remaining = int((reminder - now).total_seconds())
            if time_remaining < 0:
                break
            elif time_remaining % 5 == 0 and time_remaining != last_time_remaining:
                await timer.edit(content=f"I will remind you in {format_timespan(time_remaining)}.")
                last_time_remaining = time_remaining
            elif time_remaining < 10 and time_remaining != last_time_remaining:
                await timer.edit(content=f"I will remind you in {format_timespan(time_remaining)}.")
                last_time_remaining = time_remaining
        
        # Message constructor
        author = ctx.author.mention
        await timer.edit(content=f"Reminder: {message}\n{author}")

    # ==================================================================================== #
    #                                      COMMANDS                                        #
    # ==================================================================================== #

    @commands.hybrid_command(name="remindme")
    @commands.has_role("Bot Tester")
    async def remindme(self, ctx, *, args):
        message = await ctx.send("Processing...")
        try:
            # Split the args
            args_data = args.split('"', 1)

            event_time = args_data[0]

            if len(args_data) == 2:
                event_message = args_data[1].strip('"')
            else:
                event_message = "You requested a reminder at this time."

            # Get reminder datetime object
            reminder = self.Reminders_ParseTime(event_time)
            now = datetime.datetime.now()
            # Get time until reminder
            time_until = int((reminder - now).total_seconds())

            if time_until < 300:
                await self.Reminders_FiveMinuteTimer(ctx, reminder, time_until, event_message)
                return
            else:
                # Message constructor
                author = ctx.author.mention
                reminder_text = f'{reminder:%B %d, %Y}'
                await message.edit(content=f"I will remind you in {format_timespan(time_until)} on {reminder_text}.")

                self.Reminders_UpdateDatabase(reminder, author, event_message)

        except Exception as e:
            print(f"Exception occured during command: /remindme: {e}")
            await message.edit(content=f"Oops! I couldn't run the /remindme command: {e}")
            return

    # ==================================================================================== #
    #                                      MAIN LOOP                                       #
    # ==================================================================================== #

    @tasks.loop(minutes=1.0)
    async def RemindersTrackerLoop(self):

        try:

            # Connect to the database
            mydb = mysql.connector.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_database
            )

            cursor = mydb.cursor(buffered=True)

            query = """SELECT REMINDER, AUTHOR, MESSAGE FROM reminders ORDER BY REMINDER"""
            cursor.execute(query)

            # Checks if query is empty
            if cursor.rowcount == 0:
                return

            # Organizes the data
            data = cursor.fetchone()

            reminder = datetime.datetime.strptime(data[0], "%Y-%m-%d %H:%M:%S.%f")
            author = data[1]
            message = data[2]

            # Plan the reminder task
            now = datetime.datetime.now()
            time_until_run = (reminder - now).total_seconds()
            if time_until_run < 0:
                time_until_run = 0
            await asyncio.sleep(time_until_run)

            # Run the reminder task
            channel = self.bot.get_channel(905538463342919801)

            reminder_text = f'{reminder:%B %d, %Y}'

            embed = discord.Embed(description=f"Reminder: {message}\n{author}", color=0x49cd74)
            embed.add_field(name="Date:", value=reminder_text)
            await channel.send(author, embed=embed)

            # Remove entry once loop is finished
            query = """DELETE FROM reminders WHERE REMINDER=%(reminder)s"""
            cursor.execute(query, {'reminder': reminder})

            # Commit changes to database
            mydb.commit()

        except Exception as e:
            print(f"Exception occured during function: RemindersTrackerLoop(): {e}")
            return

    @RemindersTrackerLoop.before_loop
    async def before_RemindersTrackerLoop(self):
        await self.bot.wait_until_ready()
