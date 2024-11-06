import sys

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


class keyword_cog(commands.Cog):
    #
    #   Definitions
    #
    def __init__(self, bot):
        self.bot = bot
        
        self.config = configparser.ConfigParser()
        self.config.read("info.ini")
        
        self.deals_channel = int(self.config['DISCORD_CHANNELS']['deals'])
        self.tracker_channel = int(self.config['DISCORD_CHANNELS']['deal_tracker'])

        self.deal_notifications = int(self.config['DISCORD_ROLES']['deal_notifications'])

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
        # Opens the txt file, and appends data to it
        try:
            f = open(path, "a")
            f.write("\n")
            f.write(txt.lower())
            f.close()

        except FileNotFoundError:
            print("Error! No txt file found!")
            return None

    def remove_from_txt(self, path, txt):
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
            if line.lower().rstrip() != txt.lower():
                lines.append(line.lower().rstrip())

        # Checks if the data has been emptied 
        if lines:
            output_lines = "\n".join(lines)
        else:
            output_lines = ""

        # Overwrites the data with the new information
        try:
            f = open(path, "w")
            f.write(output_lines)
            f.close
        except FileNotFoundError:
            print("Error! No txt file found!")
            return None

    def keyword_partition(self, text, delim):
        if isinstance(text, str) is True:
            return text.partition(delim)[0]

    def keyword_check(self, text):
        keywords = self.read_from_txt("keyword_check/keywords.txt")
        negatives = self.read_from_txt("keyword_check/negatives.txt")
        delim = "@Deal Notifications"

        if keywords:
            for keyword_set in keywords:
                good = False
                matches = 0
                total = len(keyword_set.split("+"))
                for keyword in keyword_set.split("+"):
                    if isinstance(text, str) is True:
                        text_part = self.keyword_partition(text, delim)
                        if (keyword.lower() in text_part.lower()):
                            matches += 1
                    elif hasattr(text, "content"):
                        text_content_part = self.keyword_partition(text.content, delim)
                        if (keyword.lower() in text_content_part.lower()):
                            matches += 1
                        elif text.embeds:
                            embed_full = ""
                            if text.embeds[0].title:
                                embed_full += text.embeds[0].title
                            if text.embeds[0].description:
                                embed_full += text.embeds[0].description
                            embed_full_part = self.keyword_partition(embed_full, delim)
                            if (keyword.lower() in embed_full_part.lower()):
                                matches += 1
                if (matches == total):
                    good = True
                    break

            if negatives:
                for negative in negatives:
                    if isinstance(text, str) is True:
                        text_part = self.keyword_partition(text, delim)
                        if (negative.lower() in text_part.lower()):
                            good = False
                            break
                    if hasattr(text, "content"):
                        text_content_part = self.keyword_partition(text.content, delim)
                        if (negative.lower() in text_content_part.lower()):
                            good = False
                            break
                        elif text.embeds:
                            embed_full = ""
                            if text.embeds[0].title:
                                embed_full += text.embeds[0].title
                            if text.embeds[0].description:
                                embed_full += text.embeds[0].description
                            embed_full_part = self.keyword_partition(embed_full, delim)
                            if (negative.lower() in embed_full_part.lower()):
                                good = False
                                break

            if (good):
                return (True, keyword_set)
            else:
                return (False, None)
        else:
            return (False, None)

    @commands.hybrid_group(name="keyword", aliases=["keywords", "kw"], invoke_without_command=True)
    @commands.has_role("Bot Tester")
    async def keyword(self, ctx, subcommand=None, arg1=None):
        msg = f"""
```
Sure thing boss. Please specify a subcommand to use this feature.
Here is the subcommand list for the 'keyword' command:
{self.bot.command_prefix}keyword add <keyword> - adds keywords to the keyword list
{self.bot.command_prefix}keyword remove <keyword> - removes keywords from the keyword list
{self.bot.command_prefix}keyword list - lists keywords on the keyword list
```
"""
        await ctx.send(msg)

    @keyword.command(name="add", help="adds keywords to the keyword list")
    @commands.has_role("Bot Tester")
    async def add(self, ctx, *, args):
        if not args:
            await ctx.send("Please specify a keyword to add to the list.")
        else:
            args = args.split()
            for arg in args:
                keyword_match = self.keyword_check(arg)
                if (keyword_match[0]):
                    await ctx.send(f"`{arg}` is already on the list")
                else:
                    self.write_to_txt("keyword_check/keywords.txt", arg)
                    keyword_match = self.keyword_check(arg)
                    if (keyword_match[0]):
                        await ctx.send(f"Added `{arg}` to the keyword list")
                    else:
                        await ctx.send(f"Uh oh! I was unable to add `{arg}` to the list")

    @keyword.command(name="remove", help="removes keywords from the keyword list")
    @commands.has_role("Bot Tester")
    async def remove(self, ctx, *, args):
        if not args:
            await ctx.send("Please specify a keyword to remove from the list.")
        else:
            args = args.split()
            for arg in args:
                keyword_match = self.keyword_check(arg)
                if (keyword_match[0]):
                    self.remove_from_txt("keyword_check/keywords.txt", arg)
                    keyword_match = self.keyword_check(arg)
                    if (keyword_match[0]):
                        await ctx.send(f"Uh oh! I was unable to remove `{arg}` from the list")
                    else:
                        await ctx.send(f"Removed `{arg}` from the keyword list")
                else:
                    await ctx.send(f"`{arg}` isn't on the list.")

    @keyword.command(name="list", help="lists keywords on the keyword list")
    @commands.has_role("Bot Tester")
    async def list(self, ctx):
        keywords = self.read_from_txt("keyword_check/keywords.txt")
        keyword_output = "\n".join((line) for line in keywords)
        await ctx.send(f"Here is a list of all of the keywords that I'm watching for: \n```{keyword_output}```")

    @commands.Cog.listener()
    async def on_message(self, ctx):
        # Ignore messages made by the bot
        if (ctx.author == self.bot.user):
            return

        # If the message is from the deals channel
        if (ctx.channel.id == self.deals_channel):

            keyword_match = self.keyword_check(ctx)
            if (keyword_match[0]):
                keyword_msg = ""
                if ctx.content:
                    keyword_msg += ctx.content + " "
                if ctx.embeds:
                    if ctx.embeds[0].title:
                        keyword_msg += ctx.embeds[0].title + " "
                    if ctx.embeds[0].description:
                        keyword_msg += ctx.embeds[0].description

                keyword_msg = keyword_msg.partition("@Deal Notifications")[0]

                print("I found a keyword: " + keyword_match[1])
                role = discord.utils.get(ctx.guild.roles, id=self.deal_notifications)
                channel = self.bot.get_channel(self.tracker_channel)
                embed = discord.Embed(description="I found a keyword!\n" + role.mention, color=0x49cd74)
                embed.add_field(name="Keyword Matched", value=keyword_match[1])
                await channel.send(role.mention + " " + keyword_msg, embed=embed)
