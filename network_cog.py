
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


class network_cog(commands.Cog):
    #
    #   Definitions
    #
    def __init__(self, bot):
        self.bot = bot
        
        self.config = configparser.ConfigParser()
        self.config.read("info.ini")

        self.network_logs_channel = int(self.config['NETWORK']['network_logs_channel'])

        self.NetworkTrackerLoop.start()

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

    def get_ip_address(self):
        url = 'https://ipinfo.io/json'
        resp = urllib.request.urlopen(url)
        data = json.load(resp)

        return data['ip']

    def seconds_until(self, hours, minutes):
        given_time = datetime.time(hours, minutes)
        now = datetime.datetime.now()
        future_exec = datetime.datetime.combine(now, given_time)
        if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
            future_exec = datetime.datetime.combine(now + datetime.timedelta(days=1), given_time)  # days always >= 0

        return (future_exec - now).total_seconds()

    async def get_public_ip_address(self):
        try:
            old_ip_address = self.read_from_txt("network/ip.txt")
            old_ip_address = old_ip_address[0]
        except IndexError:
            old_ip_address = None

        # Get the channel object from discord
        channel = self.bot.get_channel(self.network_logs_channel)

        # Get the message contents
        new_ip_address = self.get_ip_address()

        # If the tracker is run for the first time.
        if old_ip_address is None:
            old_ip_address = new_ip_address
            message = await channel.send(":satellite: Your public ip address has been recorded.")
            # Write the new ip to the file
            self.write_to_txt("network/ip.txt", str(new_ip_address))
        # If the public ip address is the same as before
        elif old_ip_address == new_ip_address:
            message = await channel.send(":satellite: Your public ip address is still the same.")
            await asyncio.sleep(900)
            await message.delete()
        # If the public ip address has changed
        else:
            message = await channel.send("||" + old_ip_address + " -> " + new_ip_address + "|| :warning: Your public ip address appears to have changed.")
            # Write the new ip to the file
            self.write_to_txt("network/ip.txt", str(new_ip_address))

    @tasks.loop(hours=23)
    async def NetworkTrackerLoop(self):
        await asyncio.sleep(self.seconds_until(18, 00))
        while True:
            try:
                await self.get_public_ip_address()

            except Exception as e:
                print("Exception occured during network loop: ", str(e))
                await asyncio.sleep(20)
                continue
            break
        await asyncio.sleep(60)
