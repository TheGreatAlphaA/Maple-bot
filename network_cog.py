
import sys
import json
import time
import datetime
import subprocess  # For executing a shell command

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
    from wakeonlan import send_magic_packet
except ModuleNotFoundError:
    print("Please install wakeonlan. (pip install wakeonlan)")
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

        self.db_host = self.config['DATABASE']['host']
        self.db_user = self.config['DATABASE']['user']
        self.db_password = self.config['DATABASE']['password']
        self.db_database = self.config['DATABASE']['database']

        self.network_tracker = int(self.config['DISCORD_CHANNELS']['network_tracker'])

        self.NetworkTrackerLoop.start()

    def get_ip_address(self):
        url = 'https://ipinfo.io/json'
        resp = urllib.request.urlopen(url)
        data = json.load(resp)

        return data['ip']

    def get_old_ip_address(self):

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        query = """SELECT IP FROM network_public_ip"""
        cursor.execute(query)

        # Checks if query is empty
        if cursor.rowcount == 0:
            return None

        # Organizes the data
        data = cursor.fetchone()

        old_ip_address = data[0]

        return old_ip_address

    def update_ip_address(self, ip_address):

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        query = """UPDATE network_public_ip SET IP = '%(ip_address)s' WHERE ID = 1"""
        cursor.execute(query, {'ip_address': ip_address})

        # Commit changes to database
        mydb.commit()

        return

    def seconds_until(self, hours, minutes):
        given_time = datetime.time(hours, minutes)
        now = datetime.datetime.now()
        future_exec = datetime.datetime.combine(now, given_time)
        if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
            future_exec = datetime.datetime.combine(now + datetime.timedelta(days=1), given_time)  # days always >= 0

        return (future_exec - now).total_seconds()

    def get_ping(self, host):
        # Returns True if host responds to a ping request.
        # Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.

        # Building the command. Ex: "ping -c 1 google.com"
        command = ['ping', '-c', '1', host]

        return subprocess.call(command) == 0

    def get_mac(self, arg):

        result = None

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        query = """SELECT ID, MAC, HOSTNAME, IP_ADDRESS FROM network_mac"""
        cursor.execute(query)

        # Checks if query is empty
        if cursor.rowcount == 0:
            return None

        # Creates each table body
        network = cursor.fetchall()

        for host in network:
            mac = host[1].lower()
            hostname = host[2].lower()
            ip_address = host[3]

            if arg == hostname:
                result = mac
            elif arg == ip_address:
                result = mac

        return result

    async def get_public_ip_address(self):

        old_ip_address = self.get_old_ip_address()

        # Get the channel object from discord
        channel = self.bot.get_channel(self.network_tracker)

        # Get the message contents
        new_ip_address = self.get_ip_address()

        # If the tracker is run for the first time.
        if old_ip_address is None:
            old_ip_address = new_ip_address
            message = await channel.send(":satellite: Your public ip address has been recorded.")
            # Write the new ip to the file
            self.update_ip_address(new_ip_address)
        # If the public ip address is the same as before
        elif old_ip_address == new_ip_address:
            message = await channel.send(":satellite: Your public ip address is still the same.")
            await asyncio.sleep(900)
            await message.delete()
        # If the public ip address has changed
        else:
            message = await channel.send(f"||{old_ip_address} -> {new_ip_address}|| :warning: Your public ip address appears to have changed.")
            # Write the new ip to the file
            self.update_ip_address(new_ip_address)

#                         - NETWORK COMMANDS                           -

    # Command to send a ping to test network latency
    @commands.hybrid_command(name="ping", help="send a ping to test network latency")
    async def ping(self, ctx, host="localhost"):

        # Get the start time
        pingtime = time.time()
        # Send a message to the channel
        pingms = await ctx.send("Pinging...")

        for i in range(3):
            if self.get_ping(host) is True:
                # Subtract the start time from the current time
                ping = time.time() - pingtime
                # Return the ping delay time
                await pingms.edit(content=f"`maple-bot.lan ===> {host}` :ping_pong: time is `{ping:.01f} seconds`")
                return

            # Return the ping delay time
            await pingms.edit(content=f"`maple-bot.lan ===> {host}` :x: Unable to reach `{host}`")

    # Command to wake a local computer
    @commands.hybrid_command(name="wakeonlan", help="tells a computer on the network to turn on")
    async def wakeonlan(self, ctx, host):

        mac = self.get_mac(host.lower())

        if (mac is not None):

            if self.get_ping(host) is True:
                await ctx.send(f"`{host}` appears to already be online and responding to pings. Please check your connection.")
                return

            message = await ctx.send(":magic_wand: Sending the magic packet... Please wait.")

            send_magic_packet(mac)

            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[                              ] 0% \nAttempt(1/6) 2min 54sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[█                             ] 3% \nAttempt(1/6) 2min 48sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[██                            ] 7% \nAttempt(1/6) 2min 42sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[███                           ] 10% \nAttempt(1/6) 2min 36sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Attempting connection...\n`[████                          ] 13% \nAttempt(1/6) 2min 30sec`")

            if self.get_ping(host) is True:
                await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Success! :white_check_mark:\n`[██████████████████████████████] SYSTEM ONLINE`")
                return

            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[█████                         ] 17% \nAttempt(2/6) 2min 24sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[██████                        ] 20% \nAttempt(2/6) 2min 18sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[███████                       ] 23% \nAttempt(2/6) 2min 12sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[████████                      ] 27% \nAttempt(2/6) 2min 6sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Attempting connection...\n`[█████████                     ] 30% \nAttempt(2/6) 2min`")

            if self.get_ping(host) is True:
                await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Success! :white_check_mark:\n`[██████████████████████████████] SYSTEM ONLINE`")
                return

            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[██████████                    ] 33% \nAttempt(3/6) 1min 54sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[███████████                   ] 37% \nAttempt(3/6) 1min 48sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[████████████                  ] 40% \nAttempt(3/6) 1min 42sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[█████████████                 ] 43% \nAttempt(3/6) 1min 36sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Attempting connection...\n`[██████████████                ] 47% \nAttempt(3/6) 1min 30sec`")

            if self.get_ping(host) is True:
                await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Success! :white_check_mark:\n`[██████████████████████████████] SYSTEM ONLINE`")
                return

            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[███████████████               ] 50% \nAttempt(4/6) 1min 24sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[████████████████              ] 53% \nAttempt(4/6) 1min 18sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[█████████████████             ] 57% \nAttempt(4/6) 1min 12sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[██████████████████            ] 60% \nAttempt(4/6) 1min 6sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Attempting connection...\n`[███████████████████           ] 63% \nAttempt(4/6) 1min`")

            if self.get_ping(host) is True:
                await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Success! :white_check_mark:\n`[██████████████████████████████] SYSTEM ONLINE`")
                return

            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[████████████████████          ] 67% \nAttempt(5/6) 54sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[█████████████████████         ] 70% \nAttempt(5/6) 48sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[██████████████████████        ] 73% \nAttempt(5/6) 42sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[███████████████████████       ] 77% \nAttempt(5/6) 36sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[████████████████████████      ] 80% \nAttempt(5/6) 30sec`")

            if self.get_ping(host) is True:
                await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Success! :white_check_mark:\n`[██████████████████████████████] SYSTEM ONLINE`")
                return

            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[█████████████████████████     ] 83% \nAttempt(6/6) 24sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[██████████████████████████    ] 87% \nAttempt(6/6) 18sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[███████████████████████████   ] 90% \nAttempt(6/6) 12sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[████████████████████████████  ] 93% \nAttempt(6/6) 6sec`")
            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Please wait.\n`[█████████████████████████████ ] 97% \nAttempt(6/6) 1sec`")

            if self.get_ping(host) is True:
                await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Success! :white_check_mark:\n`[██████████████████████████████] SYSTEM ONLINE`")
                return

            await asyncio.sleep(6)
            await message.edit(content=f":magic_wand: Magic packet has been sent to {host}. Failed. :x:\n`[██████████████████████████████] UNABLE TO CONNECT`")
        else:
            await ctx.send(f"{host} isn't a valid hostname or IP address.")

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
