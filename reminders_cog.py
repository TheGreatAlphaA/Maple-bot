import sys
import datetime
import math

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

        self.RemindersTrackerLoop.start()

    def set_timed_reminder(self, weeks=0, days=0, hours=0, minutes=0, seconds=0):

        now = datetime.datetime.now()

        timed_reminder = now + datetime.timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)

        return timed_reminder

    def set_scheduled_reminder(self, year, month, day, hour=0, minute=0, second=0):

        scheduled_reminder = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=0)

        return scheduled_reminder

    async def five_minute_timer(self, ctx, name, seconds, reminder):

        timer = await ctx.send(f"I will remind you about {name} in {format_timespan(seconds)}.")

        now = datetime.datetime.now()
        time_remaining = (reminder - now).total_seconds()
        last_time_remaining = 0

        while time_remaining > 0:
            await asyncio.sleep(0.4)
            now = datetime.datetime.now()
            time_remaining = math.trunc((reminder - now).total_seconds())
            if time_remaining < 0:
                break
            elif time_remaining % 5 == 0 and time_remaining != last_time_remaining:
                await timer.edit(content=f"I will remind you about {name} in {format_timespan(time_remaining)}.")
                last_time_remaining = time_remaining
            elif time_remaining < 10 and time_remaining != last_time_remaining:
                await timer.edit(content=f"I will remind you about {name} in {format_timespan(time_remaining)}.")
                last_time_remaining = time_remaining
        
        await timer.edit(content=f"{ctx.author.mention}! Time is up! Reminder: {name}")

    @commands.hybrid_command(name="timer")
    @commands.has_role("Bot Tester")
    async def timer(self, ctx, name, seconds=0, minutes=0, hours=0, days=0, weeks=0):
        try:

            # Get the time between now and the reminder time calculated
            now = datetime.datetime.now()
            reminder = self.set_timed_reminder(weeks, days, hours, minutes, seconds)
            timer_seconds = (reminder - now).total_seconds()

            author = ctx.author.mention

            # If calculated time is less than 300 seconds (five minutes), use the fancy timer instead
            if timer_seconds <= 300:
                await self.five_minute_timer(ctx, name, timer_seconds, reminder)
                return

            else:

                # Connect to the database
                mydb = mysql.connector.connect(
                    host=self.db_host,
                    user=self.db_user,
                    password=self.db_password,
                    database=self.db_database
                )

                cursor = mydb.cursor(buffered=True)

                query = """INSERT INTO reminders (REMINDER, AUTHOR, NAME) VALUES (%(reminder)s, %(author)s, %(name)s)"""
                cursor.execute(query, {'reminder': reminder, 'author': author, 'name': name})

                # Commit changes to database
                mydb.commit()

                await ctx.send(f"I will remind you about {name} in {format_timespan(timer_seconds)}.")

        except Exception as e:
            print("Here is the error: ", str(e))
            return

    @commands.hybrid_command(name="reminder")
    @commands.has_role("Bot Tester")
    async def reminder(self, ctx, name, year, month, day, hour=0, minute=0, second=0):
        try:

            reminder = self.set_scheduled_reminder(year, month, day, hour, minute, second)

            author = ctx.author.mention

            # Connect to the database
            mydb = mysql.connector.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_database
            )

            cursor = mydb.cursor(buffered=True)

            query = """INSERT INTO reminders (REMINDER, AUTHOR, NAME) VALUES (%(reminder)s, %(author)s, %(name)s)"""
            cursor.execute(query, {'reminder': reminder, 'author': author, 'name': name})

            # Commit changes to database
            mydb.commit()

            reminder_text = f'{reminder:%B %d, %Y}'

            await ctx.send(f"I will remind you about {name} on {reminder_text}.")

        except Exception as e:
            print("Here is the error: ", str(e))
            return

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

            query = """SELECT REMINDER, AUTHOR, NAME FROM reminders ORDER BY REMINDER"""
            cursor.execute(query)

            # Checks if query is empty
            if cursor.rowcount == 0:
                return

            # Organizes the data
            data = cursor.fetchone()

            reminder = datetime.datetime.strptime(data[0], "%Y-%m-%d %H:%M:%S.%f")
            author = data[1]
            name = data[2]

            # Plan the reminder task
            now = datetime.datetime.now()
            time_until_run = (reminder - now).total_seconds()
            if time_until_run < 0:
                time_until_run = 0
            await asyncio.sleep(time_until_run)

            # Run the reminder task
            channel = self.bot.get_channel(905538463342919801)

            reminder_text = f'{reminder:%B %d, %Y}'

            embed = discord.Embed(description=f"Reminder: {name}\n{author}", color=0x49cd74)
            embed.add_field(name="Date:", value=reminder_text)
            await channel.send(author, embed=embed)

            # Remove entry once loop is finished
            query = """DELETE FROM reminders WHERE REMINDER=%(reminder)s"""
            cursor.execute(query, {'reminder': reminder})

            # Commit changes to database
            mydb.commit()

        except Exception as e:
            print("Here is the error: ", str(e))
            return

    @RemindersTrackerLoop.before_loop
    async def before_RemindersTrackerLoop(self):
        await self.bot.wait_until_ready()
