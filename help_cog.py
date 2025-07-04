
import sys
import random
import subprocess

try:
    import asyncio
except ModuleNotFoundError:
    print("Please install asyncio. (pip install asyncio)")
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
    from discord.ext import commands
except ModuleNotFoundError:
    print("Please install discordpy. (pip install discord.py)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")


class help_cog(commands.Cog):
    # ==================================================================================== #
    #                                     DEFINITIONS                                      #
    # ==================================================================================== #
    def __init__(self, bot):
        self.bot = bot
        
        # Config File
        self.config = configparser.ConfigParser()
        self.config.read("info.ini")

        self.help_message = ""
        self.set_message()

    # ==================================================================================== #
    #                                      FUNCTIONS                                       #
    # ==================================================================================== #

    def set_message(self):
        self.help_message = f"""
**General commands:**
```
{self.bot.command_prefix}help - displays all the available commands
{self.bot.command_prefix}whoami - tells the user what their name is
{self.bot.command_prefix}whereami - tells the user what their status is
```
**Music commands:**
```
{self.bot.command_prefix}m q - displays the current music queue
{self.bot.command_prefix}m p <keywords> - plays a selected song from youtube
{self.bot.command_prefix}m skip - skips the current song being played
{self.bot.command_prefix}m clear - stops the music and clears the queue
{self.bot.command_prefix}m stop - disconnects the bot from the voice channel
{self.bot.command_prefix}m pause - pauses the current song being played or resumes if already paused
{self.bot.command_prefix}m resume - resumes playing the current song
{self.bot.command_prefix}m remove - removes last song from the queue
```
**Dungeons & Dragons commands:**
```
{self.bot.command_prefix}roll <dice> - rolls a dice. Use '+' to add additional dice or numbers. Example: 1d20+4d4+16
{self.bot.command_prefix}dnd spell <args> - casts a spell
{self.bot.command_prefix}dnd summon <creature> <amount> <action> [adv/dis] - summons a creature to perform an action
{self.bot.command_prefix}dnd colin <weapon name> [ammo type] [feats] [spells] [adv/dis] - perform an attack action as colin rahu
```
**Hypixel Skyblock commands:**
```
{self.bot.command_prefix}skyblock tracker status - checks on the status of the tracker
{self.bot.command_prefix}skyblock tracker test - sends a test message from the skyblock tracker
```
**Keyword commands:**
```
{self.bot.command_prefix}keyword add <keyword> - adds keywords to the keyword list
{self.bot.command_prefix}keyword remove <keyword> - removes keywords from the keyword list
{self.bot.command_prefix}keyword list - lists keywords on the keyword list
```
**Notification commands:**
```
{self.bot.command_prefix}remindme <date/time> "[message]" - creates a reminder message to send later.
```
**Finance commands:**
```
{self.bot.command_prefix}stock <stock ticker> - gets the daily stock price for the selected stock ticker
{self.bot.command_prefix}metal <metal type> - gets the daily market price for the selected metal type
```
**Networking commands:**
```
{self.bot.command_prefix}ping [hostname/ip address] - sends a ping to test network latency
{self.bot.command_prefix}wakeonlan <hostname/ip address> - sends a magic packet to wake a local device
```
"""

    # Changes discord presence to hint the bot's help command
    @commands.Cog.listener()
    async def on_ready(self):
        print("\nMaple-Bot v6.4\nCreated by Alpha_A [2021-2024]\n")
        await self.bot.change_presence(activity=discord.Game(f"{self.bot.command_prefix}help"))
        print(f"Bot Is Ready. Logged in as {self.bot.user}")

    # ==================================================================================== #
    #                                      COMMANDS                                        #
    # ==================================================================================== #
    # ---------------------------------- Admin Commands ---------------------------------- #

    # Command to force-exit the bot
    @commands.command(name="exit")
    @commands.is_owner()
    async def exit(self, ctx):
        sys.exit()

    # Command to reboot the host container
    @commands.command(name="reboot")
    @commands.is_owner()
    async def reboot(self, ctx):
        command = ['reboot']
        subprocess.call(command)

    # Command to sync the bot's command tree
    @commands.hybrid_command(name="sync", help="sync the bot command tree with Discord.")
    @commands.is_owner()
    async def sync(self, ctx: commands.Context) -> None:
        message = await ctx.send("Processing...")
        try:
            # Sync the command tree
            synced = await ctx.bot.tree.sync()
            await message.edit(content=f"Synced {len(synced)} commands globally.")

        except Exception as e:
            print(f"Exception occured during command: /sync: {e}")
            await message.edit(content=f"Oops! I couldn't run the /sync command: {e}")
            return

    # --------------------------------- Generic Commands --------------------------------- #

    # Command to display the help text
    @commands.hybrid_command(name="help", help="displays all the available commands")
    async def help(self, ctx):
        try:
            await ctx.send(self.help_message)

        except Exception as e:
            print(f"Exception occured during command: /help: {e}")
            await ctx.send(f"Oops! I couldn't run the /help command: {e}")
            return

    # Command to tells the user what their name is
    @commands.hybrid_command(name="whoami", help="tells the user what their name is")
    async def whoami(self, ctx):
        try:
            name = ctx.message.author.display_name
            true_name = ctx.message.author.name
            # Check if the user has the same name as the author
            if name == 'Alpha A':
                # If the user is the author, send a specical message
                if true_name == 'the_great_alpha_a':
                    await ctx.send(f"Hi {name}. How are you doing today?")
                # If the user is not the author, but shares their name, send a special message
                else:
                    await ctx.send(f"Your name is {name}. But... you know you can't fool me, right? I know you aren't really him.")
            # Otherwise, send the user their name
            else:
                await ctx.send(f"Your name is {name}.")

        except Exception as e:
            print(f"Exception occured during command: /whoami: {e}")
            await ctx.send(f"Oops! I couldn't run the /whoami command: {e}")
            return

    # Command to tell the user what their status is
    @commands.hybrid_command(name="whereami", help="tells the user what their status is")
    async def whereami(self, ctx):
        try:
            # Check if the user actually has a status set
            try:
                # If a status is set, set the variable to that status
                location = ctx.message.author.activities[0].name
            except IndexError:
                # If no status is set, set the variable to none
                location = None

            # If no status is set, send a generic message
            if location is None:
                await ctx.send(":thinking: It looks like you are currently somewhere on the internet.")
            # If a status is set, send the user their status
            else:
                await ctx.send(f":earth_americas: It looks like you are currently {location}")

        except Exception as e:
            print(f"Exception occured during command: /whereami: {e}")
            await ctx.send(f"Oops! I couldn't run the /whereami command: {e}")
            return

    # ---------------------------------- Secret Commands --------------------------------- #

    # Command to make the bot say 'nya'
    @commands.command(name="nya")
    async def nya(self, ctx):
        try:
            await ctx.send("Nya!  (=^-ω-^=)")

        except Exception as e:
            print(f"Exception occured during command: /nya: {e}")
            await ctx.send(f"Oops! I couldn't run the /nya command: {e}")
            return

    # Command to make the bot cringe
    @commands.command(name="cringe", aliases=['ಠ_ಠ', 'ಠಠ', 'ಠ', 'disapproval', 'disgust'])
    async def cringe(self, ctx):
        try:
            await ctx.send("Yikes.  ಠ_ಠ")

        except Exception as e:
            print(f"Exception occured during command: /cringe: {e}")
            await ctx.send(f"Oops! I couldn't run the /cringe command: {e}")
            return

    # Command to make the bot say a jojo reference
    @commands.command(name="za_warudo", aliases=['the_world', "stop_time"])
    async def za_warudo(self, ctx):
        message = await ctx.send(content=":clock2: Za Warudo! Toki yo tomare!")
        try:     
            await asyncio.sleep(5)
            await message.edit(content=":clock3: Ichi-byō keika.")
            await asyncio.sleep(7 - 5)
            await message.edit(content=":clock4: Ni-byō keika.")
            await asyncio.sleep(9 - 7)
            await message.edit(content=":clock5: San-byō keika.")
            await asyncio.sleep(16 - 9)
            await message.edit(content=":clock6: Yon-byō keika.")
            await asyncio.sleep(36 - 16)
            await message.edit(content=":clock7: Go-byō keika.")
            await asyncio.sleep(48 - 36)
            await message.edit(content=":clock8: Roku-byō keika.")
            await asyncio.sleep(53 - 48)
            await message.edit(content=":clock9: Nana-byō keika.")
            await asyncio.sleep(57 - 53)
            await message.edit(content=":truck: ROAD ROLLER DA!")
            await asyncio.sleep(72 - 57)
            await message.edit(content=":truck: MUDA! MUDA! MUDA! MUDA! MUDA! MUDA! MUDA! MUDA! MUDA! MUDA! :punch: :punch: :punch:")
            await asyncio.sleep(80 - 72)
            await message.edit(content=":truck: Hachi-byō keika! WRYYYYY!! :punch: :punch: :punch:")
            await asyncio.sleep(93 - 80)
            await message.edit(content=":truck: Kyu-byō keika.")
            await asyncio.sleep(135 - 93)
            await message.edit(content=":truck: Ju-byō keika.")
            await asyncio.sleep(5)
            await message.edit(content="Ehehe, did you like my impression of DIO?")
            await asyncio.sleep(5)
            await message.edit(content="Ehehe, did you like my impression of DIO?\nI can't actually stop time though.")
            await asyncio.sleep(5)
            await message.edit(content="Ehehe, did you like my impression of DIO?\nI can't actually stop time though.\n...at least, not yet anyway :wink:")
            await asyncio.sleep(5)
            await message.delete()

        except Exception as e:
            print(f"Exception occured during command: /za_warudo: {e}")
            await message.edit(content=f"Oops! I couldn't run the /za_warudo command: {e}")
            return

    # Command to make the bot send a subscribe link for Charlie Slimecicle
    @commands.command(name="subscribe_to_slimecicle", aliases=['slimecicle', 'subscribe_to_charlieslimecicle'])
    async def subscribe_to_slimecicle(self, ctx):
        try:
            x = random.randint(1, 20)
            if x < 10:
                await ctx.send("Subscribe to Charlie Slimecicle!\nhttps://www.youtube.com/user/Slimecicle?sub_confirmation=1")
            elif x < 20:
                await ctx.send("Subscribe to Charlie Slimecicle!\nhttps://www.twitch.tv/subs/slimecicle")
            elif x == 20:
                await ctx.send("Sbscrb t Chrl Slmccl!\nhttps://www.youtube.com/@Slmccl?sub_confirmation=1")
            else:
                await ctx.send("Subscribe to Charlie Slimecicle!\nhttps://www.youtube.com/user/Slimecicle?sub_confirmation=1")
                
        except Exception as e:
            print(f"Exception occured during command: /subscribe_to_slimecicle: {e}")
            await ctx.send(f"Oops! I couldn't run the /subscribe_to_slimecicle command: {e}")
            return
