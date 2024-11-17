
import sys

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
    from discord.ext import commands
except ModuleNotFoundError:
    print("Please install discordpy. (pip install discord.py)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")


class keyword_cog(commands.Cog):
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
        
        self.deals_channel = int(self.config['DISCORD_CHANNELS']['deals'])
        self.tracker_channel = int(self.config['DISCORD_CHANNELS']['deal_tracker'])

        self.deal_notifications = int(self.config['DISCORD_ROLES']['deal_notifications'])
        
    # ==================================================================================== #
    #                                      FUNCTIONS                                       #
    # ==================================================================================== #

    def Keyword_GetOne(self, keyword, negative):

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        # Get the old values for total collection.
        query = """SELECT KEYWORD FROM keywords WHERE KEYWORD = %(keyword)s AND NEGATIVE = %(negative)s"""
        cursor.execute(query, {'keyword': keyword, 'negative': negative})

        # Checks if query is empty
        if cursor.rowcount == 0:
            return False
        else:
            return True

    def Keyword_GetAll(self, negative):

        keywords = []

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        # Get the old values for total collection.
        query = """SELECT KEYWORD FROM keywords WHERE NEGATIVE = %(negative)s"""
        cursor.execute(query, {'negative': negative})

        # Checks if query is empty
        if cursor.rowcount == 0:
            return None

        # Organizes the data
        data = cursor.fetchall()

        for row in data:
            keywords.append(row[0])

        return keywords

    def Keyword_Create(self, keyword, negative):

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        query = """INSERT INTO keywords (KEYWORD, NEGATIVE) VALUES (%(keyword)s, %(negative)s)"""
        cursor.execute(query, {'keyword': keyword, 'negative': negative})

        # Commit changes to database
        mydb.commit()

    def Keyword_Delete(self, keyword, negative):

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        query = """DELETE FROM keywords WHERE KEYWORD = %(keyword)s AND NEGATIVE = %(negative)s"""
        cursor.execute(query, {'keyword': keyword, 'negative': negative})

        # Commit changes to database
        mydb.commit()

    def Keyword_CleanText(self, ctx):

        text = []
        clean_text = ""

        # If the message is a simple discord message
        if hasattr(ctx, "content"):

            text.append(ctx.content)

        # If the message is an embeded message
        if hasattr(ctx, "embeds"):
            if ctx.embeds[0].title:
                text.append(ctx.embeds[0].title)
            if ctx.embeds[0].description:
                text.append(ctx.embeds[0].description)

        # Take all matching messages and merge into a single string
        for i in range(len(text)):
            if i == 0:
                clean_text = f"{text[i].lower()}"
            else:
                clean_text += f" {text[i].lower()}"

        return clean_text

    # ==================================================================================== #
    #                                    MAIN FUNCTION                                     #
    # ==================================================================================== #

    def Keyword_CheckIfKeywordExistsInString(self, text):
        keywords_data = self.Keyword_GetAll(False)
        n_keywords_data = self.Keyword_GetAll(True)

        match = False
        matched_keyword = ""

        if keywords_data:
            for row in keywords_data:
                # for multi-word keywords, match all of them
                keyword_set = row.split()
                number_of_keywords = len(keyword_set)
                number_of_matched_keywords = 0

                for keyword in keyword_set:
                    if keyword in text:
                        number_of_matched_keywords += 1

                if number_of_matched_keywords == number_of_keywords and number_of_matched_keywords != 0:
                    match = True
                    matched_keyword = row
                    break

        if n_keywords_data:
            for row in n_keywords_data:
                n_keyword_set = row.split()
                number_of_n_keywords = len(n_keyword_set)
                number_of_matched_n_keywords = 0

                for n_keyword in n_keyword_set:
                    if n_keyword in text:
                        number_of_matched_n_keywords += 1

                if number_of_matched_n_keywords == number_of_n_keywords and number_of_matched_n_keywords != 0:
                    match = False
                    break

        if match is True:
            return matched_keyword
        else:
            return None

    # ==================================================================================== #
    #                                      COMMANDS                                        #
    # ==================================================================================== #

    @commands.hybrid_group(name="keyword", aliases=["keywords", "kw"], invoke_without_command=True)
    @commands.has_role("Bot Tester")
    async def keyword(self, ctx):
        try:
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

        except Exception as e:
            print(f"Exception occured during command: /keyword: {e}")
            await ctx.send(f"Oops! I couldn't run the /keyword command: {e}")
            return

    @keyword.command(name="add", help="adds keywords to the keyword list")
    @commands.has_role("Bot Tester")
    async def add(self, ctx, *, args):
        message = await ctx.send("Processing...")
        try:
            if args:
                # If message is prefixed with a hyphen, add the keyword to the negative list
                if args[0] == "-":
                    list_name = "negative keyword list"
                    negative = True
                    keyword = args.lower().removeprefix("-")
                else: 
                    list_name = "keyword list"
                    negative = False
                    keyword = args.lower()

                # Check if the keyword already exists in the database.
                match = self.Keyword_GetOne(keyword, negative)

                # If the keyword exists, do not add it to the database.
                if match is True:
                    await message.edit(content=f"`{keyword}` is already on the {list_name}.")

                else:
                    # If the keyword does not exist, add it to the database.
                    self.Keyword_Create(keyword, negative)
                    await message.edit(content=f"Added `{keyword}` to the {list_name}.")

            else:
                await message.edit(content=f"Please specify a keyword to add to the {list_name}.")

        except Exception as e:
            print(f"Exception occured during command: /keyword add: {e}")
            await message.edit(content=f"Oops! I couldn't run the /keyword add command: {e}")
            return

    @keyword.command(name="remove", help="removes keywords from the keyword list")
    @commands.has_role("Bot Tester")
    async def remove(self, ctx, *, args):
        message = await ctx.send("Processing...")
        try:
            if args:
                # If message is prefixed with a hyphen, remove the keyword from the negative list
                if args[0] == "-":
                    list_name = "negative keyword list"
                    negative = True
                    keyword = args.lower().removeprefix("-")
                else: 
                    list_name = "keyword list"
                    negative = False
                    keyword = args.lower()

                # Check if the keyword already exists in the database.
                match = self.Keyword_GetOne(keyword, negative)

                # If the keyword does not exist, do not add it from database.
                if match is False:
                    await message.edit(content=f"`{keyword}` isn't on the {list_name}.")

                else:
                    # If the keyword exists, remove it from the database.
                    self.Keyword_Delete(keyword, negative)
                    await message.edit(content=f"Removed `{keyword}` from the {list_name}.")

            else:
                await message.edit(content=f"Please specify a keyword to remove from the {list_name}.")

        except Exception as e:
            print(f"Exception occured during command: /keyword remove: {e}")
            await message.edit(content=f"Oops! I couldn't run the /keyword remove command: {e}")
            return

    @keyword.command(name="list", help="lists keywords on the keyword list")
    @commands.has_role("Bot Tester")
    async def list(self, ctx):
        message = await ctx.send("Processing...")
        try:
            keywords_data = self.Keyword_GetAll(False)
            n_keywords_data = self.Keyword_GetAll(False)

            if keywords_data is None:
                await message.edit(content="I'm not currently listening for any keywords. You can add some by using /keyword add <keywords>!")
                return

            if keywords_data is not None:
                keyword_output = "\n".join((keyword) for keyword in keywords_data)
                msg = f"""Here is a list of all of the keywords that I'm listening for:\n```{keyword_output}```"""

            if n_keywords_data is not None:
                n_keyword_output = "\n".join((n_keyword) for n_keyword in n_keywords_data)
                msg += f"""\nHere is a list of all of the keywords that I've excluded:\n```{n_keyword_output}```"""

            await message.edit(content=msg)

        except Exception as e:
            print(f"Exception occured during command: /keyword list: {e}")
            await message.edit(content=f"Oops! I couldn't run the /keyword list command: {e}")
            return

    @commands.Cog.listener()
    async def on_message(self, ctx):
        # Ignore messages made by the bot
        if (ctx.author == self.bot.user):
            return

        # If the message is from the deals channel
        if (ctx.channel.id == self.deals_channel):

            text = self.Keyword_CleanText(ctx)
            matched_keyword = self.Keyword_CheckIfKeywordExistsInString(text)

            if matched_keyword:
                keyword_msg = ""
                if ctx.content:
                    keyword_msg += ctx.content + " "
                if ctx.embeds:
                    if ctx.embeds[0].title:
                        keyword_msg += ctx.embeds[0].title + " "
                    if ctx.embeds[0].description:
                        keyword_msg += ctx.embeds[0].description

                keyword_msg = keyword_msg.partition("@Deal Notifications")[0]

                print("I found a keyword: " + matched_keyword)
                role = discord.utils.get(ctx.guild.roles, id=self.deal_notifications)
                channel = self.bot.get_channel(self.tracker_channel)
                embed = discord.Embed(description="I found a keyword!\n" + role.mention, color=0x49cd74)
                embed.add_field(name="Keyword Matched", value=matched_keyword)
                await channel.send(role.mention + " " + keyword_msg, embed=embed)
