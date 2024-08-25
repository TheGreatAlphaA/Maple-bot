
import random
import sys
import math

try:
    import asyncio
except ModuleNotFoundError:
    print("Please install asyncio. (pip install asyncio)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    from table2ascii import table2ascii, Merge, Alignment
except ModuleNotFoundError:
    print("Please install table2ascii. (pip install table2ascii)")
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
    print("Please install asyncio. (pip install configparser)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    from discord.ext import commands
except ModuleNotFoundError:
    print("Please install discordpy. (pip install discord.py)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")


class dnd_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.config = configparser.ConfigParser()
        self.config.read("info.ini")

        self.db_host = self.config['DATABASE']['host']
        self.db_user = self.config['DATABASE']['user']
        self.db_password = self.config['DATABASE']['password']
        self.db_database = self.config['DATABASE']['database']

    async def discord_message_pages(self, ctx, input_list_a, input_list_b):

        if input_list_b is None:
            # Function to page through each entry instead of displaying them all at once

            # How many tables per page
            per_page = 1
            # How many total pages there should be, based on the total entries divided by entires per page, rounded up
            pages = math.ceil(len(input_list_a) / per_page)
            # Current page, always start from page 1
            cur_page = 1
            # Initial chunk of entries
            chunk = input_list_a[:per_page]
            # Linebreak (needed to define to avoid breaking some things)
            linebreak = "\n"
            # Creates the message object
            message = await ctx.send("Page " + str(cur_page) + "/" + str(pages) + ":\n" + linebreak.join(chunk))
            # Adds arrow objects to the message
            await message.add_reaction("◀️")
            await message.add_reaction("▶️")
            active = True

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
                # or you can use unicodes, respectively: "\u25c0" or "\u25b6"

            while active:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                
                    # If forward arrow emote is selected, advance the page by 1
                    if str(reaction.emoji) == "▶️" and cur_page != pages:
                        cur_page += 1
                        # Select the new content from the table
                        if cur_page != pages:
                            chunk = input_list_a[(cur_page - 1) * per_page:cur_page * per_page]
                        else:
                            chunk = input_list_a[(cur_page - 1) * per_page:]
                        # Edit the content and remove the reaction
                        await message.edit(content="Page " + str(cur_page) + "/" + str(pages) + ":\n" + linebreak.join(chunk))
                        await message.remove_reaction(reaction, user)

                    # If back arrow emote is selected, return to the previous page
                    elif str(reaction.emoji) == "◀️" and cur_page > 1:
                        cur_page -= 1
                        # Select the new content from the table
                        chunk = input_list_a[(cur_page - 1) * per_page:cur_page * per_page]
                        # Edit the content and remote the reaction
                        await message.edit(content="Page " + str(cur_page) + "/" + str(pages) + ":\n" + linebreak.join(chunk))
                        await message.remove_reaction(reaction, user)
                # After a while, remove the message
                except asyncio.TimeoutError:
                    await message.delete()
                    active = False

        else:
            # Function to page through each entry instead of displaying them all at once

            # How many tables per page
            per_page = 1
            # How many total pages there should be, based on the total entries divided by entires per page, rounded up
            pages = math.ceil(len(input_list_a) / per_page)
            # Current page, always start from page 1
            cur_page = 1
            # Initial chunk of entries
            chunk_a = input_list_a[:per_page]
            chunk_b = input_list_b[:per_page]
            # Linebreak (needed to define to avoid breaking some things)
            linebreak = "\n"
            # Creates the message object
            message_a = await ctx.send("Page " + str(cur_page) + "/" + str(pages) + ":\n" + linebreak.join(chunk_a))
            message_b = await ctx.send(linebreak.join(chunk_b))
            # Adds arrow objects to the message
            await message_b.add_reaction("◀️")
            await message_b.add_reaction("▶️")
            active = True

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
                # or you can use unicodes, respectively: "\u25c0" or "\u25b6"

            while active:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                
                    # If forward arrow emote is selected, advance the page by 1
                    if str(reaction.emoji) == "▶️" and cur_page != pages:
                        cur_page += 1
                        # Select the new content from the table
                        if cur_page != pages:
                            chunk_a = input_list_a[(cur_page - 1) * per_page:cur_page * per_page]
                            chunk_b = input_list_b[(cur_page - 1) * per_page:cur_page * per_page]
                        else:
                            chunk_a = input_list_a[(cur_page - 1) * per_page:]
                            chunk_b = input_list_b[(cur_page - 1) * per_page:]
                        # Edit the content and remove the reaction
                        await message_a.edit(content="Page " + str(cur_page) + "/" + str(pages) + ":\n" + linebreak.join(chunk_a))
                        await message_b.edit(content=linebreak.join(chunk_b))
                        await message_b.remove_reaction(reaction, user)

                    # If back arrow emote is selected, return to the previous page
                    elif str(reaction.emoji) == "◀️" and cur_page > 1:
                        cur_page -= 1
                        # Select the new content from the table
                        chunk_a = input_list_a[(cur_page - 1) * per_page:cur_page * per_page]
                        chunk_b = input_list_b[(cur_page - 1) * per_page:cur_page * per_page]
                        # Edit the content and remote the reaction
                        await message_a.edit(content="Page " + str(cur_page) + "/" + str(pages) + ":\n" + linebreak.join(chunk_a))
                        await message_b.edit(content=linebreak.join(chunk_b))
                        await message_b.remove_reaction(reaction, user)
                # After a while, remove the message
                except asyncio.TimeoutError:
                    await message_a.delete()
                    await message_b.delete()
                    active = False

    async def diceRoll(self, dice):
        diceInput = dice.split("d", 1)
        diceOutput = []

        try:
            numberOfDice = int(diceInput[0])
        # Return an error if nothing is submitted
        except IndexError:
            # print("Error: diceRoll - no valid inputs recieved")
            result = "E"
            return result
        # Return an error if no valid number is recieved
        except ValueError:
            # print("Error: diceRoll - diceInput[0] is not an integer")
            result = "E"
            return result

        try:
            typeOfDice = int(diceInput[1])
        # If the user entered a number without selecting a dice, return that number
        except IndexError:
            diceOutput.append(numberOfDice)
            return diceOutput

        # Return an error if the user selected an invalid type of dice
        except ValueError:
            # print("Error: diceRoll - diceInput[1] is not an integer")
            result = "E"
            return result

        # Checks if the user entered zero or a negative number as any number
        if numberOfDice <= 0 or typeOfDice <= 0:
            result = 0
            return result

        # Prevent users from rolling obscenely large amounts of dice at once
        if numberOfDice > 200:
            result = "O"
            return result

        # Prevent users from rolling obscenely large dice
        if typeOfDice > 1000:
            result = "S"
            return result

        for x in range(numberOfDice):
            diceOutput.append(random.randint(1, typeOfDice))

        return diceOutput

    async def diceRoll_crunchyCrits(self, dice):
        diceInput = dice.split("d", 1)
        diceOutput = []

        try:
            numberOfDice = int(diceInput[0])
        # Return an error if nothing is submitted
        except IndexError:
            # print("Error: diceRoll - no valid inputs recieved")
            result = "E"
            return result
        # Return an error if no valid number is recieved
        except ValueError:
            # print("Error: diceRoll - diceInput[0] is not an integer")
            result = "E"
            return result

        try:
            typeOfDice = int(diceInput[1])
        # If the user entered a number without selecting a dice, return that number
        except IndexError:
            diceOutput.append(numberOfDice)
            return diceOutput

        # Return an error if the user selected an invalid type of dice
        except ValueError:
            # print("Error: diceRoll - diceInput[1] is not an integer")
            result = "E"
            return result

        # Checks if the user entered zero or a negative number as any number
        if numberOfDice <= 0 or typeOfDice <= 0:
            result = 0
            return result

        # Prevent users from rolling obscenely large amounts of dice at once
        if numberOfDice > 200:
            result = "O"
            return result

        # Prevent users from rolling obscenely large dice
        if typeOfDice > 1000:
            result = "S"
            return result

        for x in range(numberOfDice):
            diceOutput.append(typeOfDice)

        return diceOutput

    async def multi_diceRoll(self, dice):
        diceInput = []
        diceOutput = []
        result = 0

        diceInput = dice.split("+")
        for x in diceInput:
            diceOutput.append(await self.diceRoll(x))

        for y in diceOutput:
            for value in y:
                result = result + value

        return result

    async def multi_diceRoll_crunchyCrits(self, dice):
        diceInput = []
        diceOutput = []
        result = 0

        diceInput = dice.split("+")
        for x in diceInput:
            diceOutput.append(await self.diceRoll_crunchyCrits(x))

        for y in diceOutput:
            for value in y:
                result = result + value

        return result

    async def dnd_CreatureStatBlocks(self, spell):

        # Creates empty message list
        creatures_msgs = []

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        if spell == "conjure_animals":
            # Query the database for information
            query = """SELECT * FROM dnd_creatures WHERE TYPE = 'Beast' AND CR <= '2.00' ORDER BY `CR` ASC"""
            cursor.execute(query)
        elif spell == "conjure_woodland_beings":
            # Query the database for information
            query = """SELECT * FROM dnd_creatures WHERE TYPE = 'Fey' AND CR <= '2.00'"""
            cursor.execute(query)
        elif spell == "conjure_fey":
            # Query the database for information
            query = """SELECT * FROM dnd_creatures WHERE (TYPE = 'Fey' AND CR > '2.00' AND CR <= '9.00') OR (TYPE = 'Beast' AND CR > '2.00' AND CR <= '9.00') ORDER BY `CR` ASC"""
            cursor.execute(query)
        elif spell == "conjure_celestial":
            # Query the database for information
            query = """SELECT * FROM dnd_creatures WHERE TYPE = 'Celestial' AND CR <= '5.00' ORDER BY `CR` ASC"""
            cursor.execute(query)
        elif spell == "conjure_minor_elementals":
            # Query the database for information
            query = """SELECT * FROM dnd_creatures WHERE TYPE = 'Elemental' AND CR <= '2.00' ORDER BY `CR` ASC"""
            cursor.execute(query)
        elif spell == "conjure_elemental":
            # Query the database for information
            query = """SELECT * FROM dnd_creatures WHERE TYPE = 'Elemental' AND CR > '2.00' AND CR <= '9.00' ORDER BY `CR` ASC"""
            cursor.execute(query)
        else:
            # Query the database for information
            query = """SELECT * FROM dnd_creatures LIMIT 50"""
            cursor.execute(query)

        # Checks if query is empty
        if cursor.rowcount == 0:
            creatures_msgs.append("Uh oh, I couldn't find anything in the database!")
            return creatures_msgs

        # Creates each table body
        dnd_creatures_table = cursor.fetchall()

        for creature in dnd_creatures_table:

            creature_name = str(creature[1])
            creature_type = str(creature[2])
            creature_cr = str(creature[3])
            creature_size = str(creature[4])
            creature_ac = str(creature[5])

            hp_dice = str(creature[6])
            hp_flat = str(creature[7])
            hp_total = str(creature[7] + creature[8])

            hp_total_table = hp_flat + " (" + hp_total + ")"

            walk_speed = str(creature[9])
            swim_speed = str(creature[10])
            fly_speed = str(creature[11])
            burrow_speed = str(creature[12])

            speed_table = walk_speed
            if swim_speed != "0":
                speed_table += ", (" + swim_speed + " swim)"
            if fly_speed != "0":
                speed_table += ", (" + fly_speed + " fly)"
            if burrow_speed != "0":
                speed_table += ", (" + burrow_speed + " burrow)"

            str_stat = str(creature[13])
            dex_stat = str(creature[14])
            con_stat = str(creature[15])
            int_stat = str(creature[16])
            wis_stat = str(creature[17])
            cha_stat = str(creature[18])

            source = str(creature[20])
            description = str(creature[21])
            special_feats = str(creature[22])

            # Creates empty table body
            creatures_table_body = []

            # Data
            creatures_table_row_a = [creature_name, creature_type, creature_cr, creature_size, creature_ac, hp_dice, hp_total_table, speed_table, str_stat, dex_stat, con_stat, int_stat, wis_stat, cha_stat]
            creatures_table_body.append(creatures_table_row_a)

            # Builds the table
            creatures_table = table2ascii(
                header=["Name", "Type", "CR", "Size", "AC", "Hit Dice", "Average HP", "Speed", "STR", "DEX", "CON", "INT", "WIS", "CHA"],
                body=creatures_table_body,
                column_widths=[25, 15, 6, 15, 5, 15, 15, 20, 5, 5, 5, 5, 5, 5],
                alignments=[Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.LEFT],
            )

            # Use alternative table if standard table is too long
            if len(creatures_table) + len(special_feats) + len(description) + len(source) > 1975:
                creatures_table_length = str(len(creatures_table))
                creatures_table = "Error: DND Creatures Table row for" + creature_name + "longer than allowed amount: " + creatures_table_length

            # Adds the body table to the end of the message
            creatures_msgs.append("```" + creatures_table + "\nFeats:\n" + special_feats + "\n\nNotes:\n" + description + "\n\n" + source + "```")

        # Returns completed message
        return creatures_msgs

    async def dnd_isCreatureValidSummon(self, spell, creature_name):

        # Creature is assumed invalid until proven otherwise
        valid_creature = False

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        if spell == "conjure_animals":
            # Query the database for information
            query = """SELECT NAME FROM dnd_creatures WHERE TYPE = 'Beast' AND CR <= '2.00' AND NAME = %(creature_name)s"""
            cursor.execute(query, {'creature_name': creature_name})
        elif spell == "conjure_woodland_beings":
            # Query the database for information
            query = """SELECT NAME FROM dnd_creatures WHERE TYPE = 'Fey' AND CR <= '2.00' AND NAME = %(creature_name)s"""
            cursor.execute(query, {'creature_name': creature_name})
        elif spell == "conjure_fey":
            # Query the database for information
            query = """SELECT NAME FROM dnd_creatures WHERE (TYPE = 'Fey' AND CR <= '9.00') OR (TYPE = 'Beast' AND CR <= '9.00') AND NAME = %(creature_name)s"""
            cursor.execute(query, {'creature_name': creature_name})
        elif spell == "conjure_celestial":
            # Query the database for information
            query = """SELECT NAME FROM dnd_creatures WHERE TYPE = 'Celestial' AND CR <= '5.00' AND NAME = %(creature_name)s"""
            cursor.execute(query, {'creature_name': creature_name})
        elif spell == "conjure_minor_elementals":
            # Query the database for information
            query = """SELECT NAME FROM dnd_creatures WHERE TYPE = 'Elemental' AND CR <= '2.00' AND NAME = %(creature_name)s"""
            cursor.execute(query, {'creature_name': creature_name})
        elif spell == "conjure_elemental":
            # Query the database for information
            query = """SELECT NAME FROM dnd_creatures WHERE TYPE = 'Elemental' AND CR <= '9.00' AND NAME = %(creature_name)s"""
            cursor.execute(query, {'creature_name': creature_name})
        else:
            # Query the database for information
            query = """SELECT NAME FROM dnd_creatures WHERE NAME = %(creature_name)s"""
            cursor.execute(query, {'creature_name': creature_name})

        # If creature not found, return false
        if cursor.rowcount == 0:
            valid_creature = False

        # If one match found, return true
        elif cursor.rowcount == 1: 
            valid_creature = True

        # If more than one match found, return false
        elif cursor.rowcount > 1:
            print("Error: dnd_isCreatureValidSummon: Rowcount higher than expected")
            valid_creature = False
        
        return valid_creature

    async def dnd_CreatureActionStatBlocks(self, spell, creature_name):

        # Creates empty message list
        creatures_msgs = []

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        # Query the database for information
        query = """SELECT CREATURE_ACTION, ATTACK_HIT_TOTAL, ATTACK_DAMAGE_DICE, ATTACK_DAMAGE_TYPE, ATTACK_DESCRIPTION FROM dnd_creatures_attacks WHERE CREATURE_NAME = %(creature_name)s"""
        cursor.execute(query, {'creature_name': creature_name})

        # Checks if query is empty
        if cursor.rowcount == 0:
            creatures_msgs.append("Could not find any creatures with that name. Please try again.")
            return creatures_msgs

        # Checks if this spell can actually summon this creature
        if await self.dnd_isCreatureValidSummon(spell, creature_name) is False:
            creatures_msgs.append("Couldn't find that creature on this spell's summoning list. Please try again.")
            return creatures_msgs

        # Fetches all of the rows from the table
        dnd_creature_actions_table = cursor.fetchall()

        # Create each row in the table body
        for action in dnd_creature_actions_table:

            action_name = str(action[0])
            action_hit_bonus = str(action[1])
            action_damage_dice = str(action[2])
            action_damage_type = str(action[3])
            action_description = str(action[4])

            # If attack contains this character, skip it
            # This is used for special effects, like bonus damage, that isn't a seperate attack
            if '~' in action_name:
                continue

            # Creates empty table body list
            creatures_table_body = []

            # Data
            creatures_table_row_a = [action_name, "(+" + action_hit_bonus + ")", action_damage_dice, action_damage_type]
            creatures_table_body.append(creatures_table_row_a)

            # Build the table
            creatures_table = table2ascii(
                header=[creature_name, "To Hit", "Damage", "Damage Type"],
                body=creatures_table_body,
                column_widths=[25, 15, 15, 15],
                alignments=[Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.LEFT],
            )

            # Adds the table to the end of the message
            creatures_msgs.append("```" + creatures_table + "\n\nDescription:\n" + action_description + "```")

        # Returns completed message
        return creatures_msgs

    async def dnd_isCreatureAmoutValid(self, spell, spell_level, creature_name, creature_amount):

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        # Query the database for information
        query = """SELECT CR FROM dnd_creatures WHERE NAME = %(creature_name)s"""
        cursor.execute(query, {'creature_name': creature_name})

        # Checks if query is empty
        if cursor.rowcount == 0:
            result = None
            return result

        # Checks if this spell can actually summon this creature
        if await self.dnd_isCreatureValidSummon(spell, creature_name) is False:
            result = None
            return result

        # Fetches all of the rows from the table
        dnd_creature_cr = cursor.fetchall()

        for creature_cr in dnd_creature_cr:
            cr = creature_cr[0]

        if spell == "conjure_animals":
            # If there is no spell level, assume the minimum to cast the spell
            if spell_level is None:
                spell_level = 3
            # Determine the maximum number of creatures that can be summoned with a spell
            if spell_level < 3:
                maxCreatureAmount = None
            elif spell_level < 5:
                maxCreatureAmount = 2 / cr
            elif spell_level < 7:
                maxCreatureAmount = 4 / cr
            elif spell_level < 9:
                maxCreatureAmount = 6 / cr
            elif spell_level < 10:
                maxCreatureAmount = 8 / cr
            elif spell_level > 9:
                maxCreatureAmount = 32

        elif spell == "conjure_woodland_beings":
            # If there is no spell level, assume the minimum to cast the spell
            if spell_level is None:
                spell_level = 4
            # Determine the maximum number of creatures that can be summoned with a spell
            if spell_level < 4:
                maxCreatureAmount = None
            elif spell_level < 6:
                maxCreatureAmount = 2 / cr
            elif spell_level < 8:
                maxCreatureAmount = 4 / cr
            elif spell_level < 10:
                maxCreatureAmount = 6 / cr
            elif spell_level > 9:
                maxCreatureAmount = 32

        elif spell == "conjure_minor_elementals":
            # If there is no spell level, assume the minimum to cast the spell
            if spell_level is None:
                spell_level = 4
            # Determine the maximum number of creatures that can be summoned with a spell
            if spell_level < 4:
                maxCreatureAmount = None
            elif spell_level < 6:
                maxCreatureAmount = 2 / cr
            elif spell_level < 8:
                maxCreatureAmount = 4 / cr
            elif spell_level < 10:
                maxCreatureAmount = 6 / cr
            elif spell_level > 9:
                maxCreatureAmount = 32

        elif spell == "conjure_elemental":
            # If there is no spell level, assume the minimum to cast the spell
            if spell_level is None:
                spell_level = 5
            # Determine the maximum number of creatures that can be summoned with a spell
            if spell_level < 5:
                maxCreatureAmount = None
            elif cr > spell_level:
                maxCreatureAmount = None
            elif cr <= spell_level < 9:
                maxCreatureAmount = 1
            elif spell_level > 9:
                maxCreatureAmount = 32

        elif spell == "conjure_fey":
            # If there is no spell level, assume the minimum to cast the spell
            if spell_level is None:
                spell_level = 6
            # Determine the maximum number of creatures that can be summoned with a spell
            if spell_level < 6:
                maxCreatureAmount = None
            elif cr > spell_level:
                maxCreatureAmount = None
            elif cr <= spell_level < 9:
                maxCreatureAmount = 1
            elif spell_level > 9:
                maxCreatureAmount = 32

        elif spell == "conjure_celestial":
            # If there is no spell level, assume the minimum to cast the spell
            if spell_level is None:
                spell_level = 7
            # Determine the maximum number of creatures that can be summoned with a spell
            if spell_level < 7:
                maxCreatureAmount = None
            elif spell_level < 9 and cr > 4:
                maxCreatureAmount = None
            elif spell_level < 9 and cr < 4:
                maxCreatureAmount = 1
            elif spell_level < 10 and cr > 5:
                maxCreatureAmount = None
            elif spell_level < 10 and cr < 5:
                maxCreatureAmount = 1
            elif spell_level > 9:
                maxCreatureAmount = 32

        else:
            maxCreatureAmount = 32

        # If there is no creature amount, assume one creature is summoned
        if creature_amount is None:
            creature_amount = 1

        # If there is no max creature amount, assume nothing happens
        if maxCreatureAmount is None:
            result = maxCreatureAmount
        # If too many creatures have been summoned, reset it down to the highest maximum
        elif creature_amount > maxCreatureAmount:
            result = int(maxCreatureAmount)
        else:
            result = creature_amount

        return result

    async def dnd_CreatureActionCalculator(self, spell, spell_level, creature_name, creature_amount_req, creature_action, adv):

        # Creates empty message list
        creatures_msgs = []

        # Connect to the database
        mydb = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_database
        )

        cursor = mydb.cursor(buffered=True)

        # Checks if this spell can actually summon this creature
        if await self.dnd_isCreatureValidSummon(spell, creature_name) is False:
            creatures_msgs.append("Couldn't find that creature on this spell's summoning list. Please try again.")
            return creatures_msgs

        # Checks if the creature amount is a valid number:
        creature_amount = await self.dnd_isCreatureAmoutValid(spell, spell_level, creature_name, creature_amount_req)
        # If creatures amount is zero
        if creature_amount is None:
            creatures_msgs.append("Couldn't summon that creature with this spell level. Please try a higher spell level.")
            return creatures_msgs
        elif creature_amount < creature_amount_req:
            creatures_msgs.append("Too many creatures summoned for spell level. Summoning " + str(creature_amount) + " instead.")

        # Creates an empty attack list
        creature_attack_actions = []

        # Grabs the attack stats for the creature
        creature_attack_stats = []

        # Creates empty attack rolls list
        creature_attack_rolls = []

        # Grabs the possible attack damage types for the creature
        creature_attack_damage_types = [["total", 0, 0, 0]]

        # Multiple attacks for multiattack
        if creature_action == "Multiattack":
            query = """SELECT CREATURE_ACTION, CREATURE_ACTION_BONUS, ATTACK_HIT_TOTAL, ATTACK_DAMAGE_DICE, ATTACK_DAMAGE_TYPE FROM dnd_creatures_attacks WHERE CREATURE_NAME = %(creature_name)s"""
            cursor.execute(query, {'creature_name': creature_name})

            # Checks if query is empty
            if cursor.rowcount == 0:
                creatures_msgs.append("Could not find that creature. Please try again.")
                return creatures_msgs

            # Append the attacks in the bonus action column
            for (CREATURE_ACTION, CREATURE_ACTION_BONUS, ATTACK_HIT_TOTAL, ATTACK_DAMAGE_DICE, ATTACK_DAMAGE_TYPE) in cursor:
                # When Multiattack is found, split the bonus attacks and add them to the attack actions
                if CREATURE_ACTION == "Multiattack":
                    creature_attack_actions = CREATURE_ACTION_BONUS.split(",")
                else:
                    # Take the stats for the attacks that aren't multiattack and save them
                    creature_attack_stat = [CREATURE_ACTION, ATTACK_HIT_TOTAL, ATTACK_DAMAGE_DICE, ATTACK_DAMAGE_TYPE]
                    creature_attack_stats.append(creature_attack_stat)

                    # If the damage type for the attack hasn't been entered, enter it
                    if ATTACK_DAMAGE_TYPE not in creature_attack_damage_types:
                        creature_attack_damage_types.append([ATTACK_DAMAGE_TYPE, 0, 0, 0])

            # Checks if Multiattack was not found
            if creature_attack_actions == []:
                creatures_msgs.append("Could not find that attack for that creature. Please try again.")
                return creatures_msgs

        else:
            # For all attacks that aren't Multiattack
            query = """SELECT CREATURE_ACTION, CREATURE_ACTION_BONUS, ATTACK_HIT_TOTAL, ATTACK_DAMAGE_DICE, ATTACK_DAMAGE_TYPE FROM dnd_creatures_attacks WHERE CREATURE_NAME = %(creature_name)s AND CREATURE_ACTION = %(creature_action)s"""
            cursor.execute(query, {'creature_name': creature_name, 'creature_action': creature_action})

            # Checks if query is empty
            if cursor.rowcount == 0:
                creatures_msgs.append("Could not find that attack for that creature. Please try again.")
                return creatures_msgs

            # Append the attack in the action column
            for (CREATURE_ACTION, CREATURE_ACTION_BONUS, ATTACK_HIT_TOTAL, ATTACK_DAMAGE_DICE, ATTACK_DAMAGE_TYPE) in cursor:
                creature_attack_actions.append(CREATURE_ACTION)

                # Take the stats for the attack and save it
                creature_attack_stat = [CREATURE_ACTION, ATTACK_HIT_TOTAL, ATTACK_DAMAGE_DICE, ATTACK_DAMAGE_TYPE]
                creature_attack_stats.append(creature_attack_stat)

                # Enter the damage type
                if ATTACK_DAMAGE_TYPE not in creature_attack_damage_types:
                    creature_attack_damage_types.append([ATTACK_DAMAGE_TYPE, 0, 0, 0])

        # For all of the creatures summoned
        for creatures in range(creature_amount):
            # For each attack each creature performs
            for action in creature_attack_actions:
                for action_stats in creature_attack_stats:
                    CREATURE_ACTION = action_stats[0]
                    ATTACK_HIT_TOTAL = action_stats[1]
                    ATTACK_DAMAGE_DICE = action_stats[2]
                    ATTACK_DAMAGE_TYPE = action_stats[3]

                    if str(CREATURE_ACTION) == str(action):
                        # Creates empty single attack list
                        creature_attack = []

                        # Always use 1d20 to roll for attacks (before modifiers)
                        dice_to_hit = "1d20"

                        # Roll to attack
                        to_hit = await self.multi_diceRoll(dice_to_hit)

                        # If the attack has advantage, roll again and take the higher number
                        if adv == "adv":
                            to_hit_adv = await self.multi_diceRoll(dice_to_hit)
                            if to_hit < to_hit_adv:
                                to_hit = to_hit_adv
                        # If the attack has disadvantage, roll again and take the lower number
                        elif adv == "dis":
                            to_hit_dis = await self.multi_diceRoll(dice_to_hit)
                            if to_hit > to_hit_dis:
                                to_hit = to_hit_dis

                        # Add the hit modifiers and append to the list
                        creature_attack.append(to_hit + int(ATTACK_HIT_TOTAL))

                        # Assume critical faliure always misses
                        if to_hit == 1:
                            damage = 0

                        # Roll regular damage for regular hits
                        elif to_hit < 20:
                            damage = await self.multi_diceRoll(ATTACK_DAMAGE_DICE)

                        # Roll regular crits for critical damage
                        # elif to_hit == 20:
                        #    damage = dnd_lib.multi_diceRoll(ATTACK_DAMAGE_DICE) + dnd_lib.multi_diceRoll(ATTACK_DAMAGE_DICE)

                        # Roll crunchy crits for critical damage
                        elif to_hit == 20:
                            damage = await self.multi_diceRoll_crunchyCrits(ATTACK_DAMAGE_DICE) + await self.multi_diceRoll(ATTACK_DAMAGE_DICE)

                        # Append the damage to the damage array
                        creature_attack.append(damage)

                        # Append the damage type to the damage array
                        creature_attack.append(ATTACK_DAMAGE_TYPE)

                        # Append the damage done of that type to the damage type array
                        for damage_type in creature_attack_damage_types:
                            # Adds the damage to the damage total
                            if damage_type[0] == "total":
                                damage_type[1] += damage
                            # Adds the type damages to the damage total
                            elif damage_type[0] == ATTACK_DAMAGE_TYPE:
                                damage_type[1] += damage

                        # If everything checks out, add the rolls to the list
                        if len(creature_attack):
                            creature_attack_rolls.append(creature_attack)
                        else:
                            creatures_msgs.append("Error: did not recieve the correct number of arguments")
                            return creatures_msgs

        # One all of the data has been collected, sort it
        creature_attack_rolls.sort()

        previous_attack_to_hit = [creature_attack_rolls[0][0], creature_attack_rolls[0][2]]

        # For items in the attack rolls list
        for attacks in creature_attack_rolls:

            if int(attacks[0]) - int(ATTACK_HIT_TOTAL) == 1:
                attacks[0] = str(attacks[0]) + " ✘"
            elif int(attacks[0]) - int(ATTACK_HIT_TOTAL) == 20:
                attacks[0] = str(attacks[0]) + " ★"

            # For each type of damage listed
            for types in creature_attack_damage_types:
                if previous_attack_to_hit[0] == attacks[0] and previous_attack_to_hit[0] == attacks[2]:
                    if types[0] == attacks[2]:
                        # Add to damage type
                        attacks.append(types[1] - types[2])
                        types[3] += attacks[1]
                else:
                    if types[0] == attacks[2]:
                        # Add to damage type
                        types[2] = types[3]
                        attacks.append(types[1] - types[2])
                        types[3] += attacks[1]
                        # If the next attack is the same attack hit and damage type as this one, don't change the damage number
                        previous_attack_to_hit[0] = attacks[0]
                        previous_attack_to_hit[1] = attacks[2]

        previous_attack_to_hit = creature_attack_rolls[0][0]

        # For items in the attack rolls list
        for attacks in creature_attack_rolls:
            if previous_attack_to_hit == attacks[0]:
                # Add to damage total
                attacks.append(creature_attack_damage_types[0][1] - creature_attack_damage_types[0][2])
                creature_attack_damage_types[0][3] += attacks[1]
            else:
                # Add to damage total
                creature_attack_damage_types[0][2] = creature_attack_damage_types[0][3]
                attacks.append(creature_attack_damage_types[0][1] - creature_attack_damage_types[0][2])
                creature_attack_damage_types[0][3] += attacks[1]
                # If the next attack is the same attack hit as this one, don't change the damage number
                previous_attack_to_hit = attacks[0]

        # Query information for the table
        query = """SELECT NAME, HP_AVG, HP_BONUS, SOURCE FROM dnd_creatures WHERE NAME = %(creature_name)s"""
        cursor.execute(query, {'creature_name': creature_name})

        for (NAME, HP_AVG, HP_BONUS, SOURCE) in cursor:
            creature_name = NAME
            creature_hp = (HP_AVG + HP_BONUS)
            creature_source = SOURCE

        # Creates empty table body
        creatures_table_body = []

        # Counts how many rows have been iterated
        n = 0

        # Counts how many pages
        cur_page = 0

        # While there are still rows to iterate
        while n < len(creature_attack_rolls):
            # Append the next row to the body
            creatures_table_body.append(creature_attack_rolls[n])
            # Count the row that has been appended
            n += 1

            if n % 16 == 0:
                # Define the current page
                footer = creature_name + ", HP: " + str(creature_hp * creature_amount) + " (Base HP:" + str(creature_hp) + " x " + str(creature_amount) + ")"
                cur_page += 1
                page_number = str(cur_page) + "/" + str(math.ceil(len(creature_attack_rolls) / 16))
                # Build the table
                creatures_table = table2ascii(
                    header=["To Hit", "Damage", "Damage Type", "Type Damage", "Total Damage"],
                    body=creatures_table_body,
                    footer=[footer, Merge.LEFT, Merge.LEFT, Merge.LEFT, page_number],
                    column_widths=[8, 8, 15, 14, 14],
                    alignments=[Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.LEFT],

                )

                # Adds the table to the end of the message
                creatures_msgs.append("```" + creatures_table + "```")

                # Clears the table body
                creatures_table_body = []

        if creatures_table_body != []:
            # Define the current page
            footer = creature_name + ", HP: " + str(creature_hp * creature_amount) + " (Base HP:" + str(creature_hp) + " x " + str(creature_amount) + ")"
            cur_page += 1
            page_number = str(cur_page) + "/" + str(math.ceil(len(creature_attack_rolls) / 16))
            # Build the table
            creatures_table = table2ascii(
                header=["To Hit", "Damage", "Damage Type", "Type Damage", "Total Damage"],
                body=creatures_table_body,
                footer=[footer, Merge.LEFT, Merge.LEFT, Merge.LEFT, page_number],
                column_widths=[8, 8, 15, 14, 14],
                alignments=[Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.LEFT],

            )

            # Adds the table to the end of the message
            creatures_msgs.append("```" + creatures_table + "```")

        # Adds the source to the end of the message
        if len(creature_attack_rolls) == 1:
            creatures_msgs.append("```Generated " + str(creature_amount) + " " + creature_name + " creature making " + str(len(creature_attack_rolls)) + " " + creature_action + " action. Source: " + creature_source + "```")
        elif creature_amount == 1:
            creatures_msgs.append("```Generated " + str(creature_amount) + " " + creature_name + " creature making " + str(len(creature_attack_rolls)) + " " + creature_action + " actions. Source: " + creature_source + "```")
        else:
            creatures_msgs.append("```Generated " + str(creature_amount) + " " + creature_name + " creatures making " + str(len(creature_attack_rolls)) + " " + creature_action + " actions. Source: " + creature_source + "```")

        # Returns completed message
        return creatures_msgs

    async def dnd_SummonCreature(self, spell, spell_level, creature_name, creature_amount, creature_action, adv):

        # Function to normalize user inputs
        def clean_input(s):
            return ' '.join(w[:1].upper() + w[1:] for w in s.split('_'))
        
        if creature_name is None:

            # Get a table of creatures that can be summoned with Conjure Animals
            creatures_msgs = await self.dnd_CreatureStatBlocks(spell)

            return creatures_msgs

        elif creature_action is None:

            # Clean creature name input
            creature_name = clean_input(creature_name)
            
            # Get a table of actions that this creature can perform
            creatures_msgs = await self.dnd_CreatureActionStatBlocks(spell, creature_name)

            return creatures_msgs

        else:

            # Clean creature name input
            creature_name = clean_input(creature_name)

            # Clean creature action input
            creature_action = clean_input(creature_action)

            # If creature amount is not int, set it to None
            if creature_amount:
                try:
                    creature_amount = int(creature_amount)
                except TypeError:
                    creature_amount = None

            # If spell level is not int, set it to None
            if spell_level:
                try:
                    spell_level = int(spell_level)
                except TypeError:
                    spell_level = None

            # If advantage is not adv or dis, set it to None
            if adv:
                if adv != "adv" and adv != "dis":
                    adv = None

            # Get a table of actions that this creature can perform
            creatures_msgs = await self.dnd_CreatureActionCalculator(spell, spell_level, creature_name, creature_amount, creature_action, adv)

            return creatures_msgs

    async def player_ammo(self, args, critical):

        player_table = []

        for arg in args:

            if arg in ("water", "water_arrow"): 

                name = "Water Arrow"
                damage = await self.multi_diceRoll("1d6")
                if critical is True:
                    damage += await self.multi_diceRoll_crunchyCrits("1d6")
                damage_type = "cold"

                player_subtable = [name, damage, damage_type]

                player_table.append(player_subtable)

                break

            elif arg in ("earth", "earth_arrow"): 

                name = "Earth Arrow"
                damage = await self.multi_diceRoll("1d6")
                if critical is True:
                    damage += await self.multi_diceRoll_crunchyCrits("1d6")
                damage_type = "acid"

                player_subtable = [name, damage, damage_type]

                player_table.append(player_subtable)

                break

            elif arg in ("fire", "fire_arrow"): 

                name = "Fire Arrow"
                damage = await self.multi_diceRoll("1d6")
                if critical is True:
                    damage += await self.multi_diceRoll_crunchyCrits("1d6")
                damage_type = "fire"

                player_subtable = [name, damage, damage_type]

                player_table.append(player_subtable)

                break

            elif arg in ("wind", "wind_arrow"): 

                name = "Wind Arrow"
                damage = await self.multi_diceRoll("1d6")
                if critical is True:
                    damage += await self.multi_diceRoll_crunchyCrits("1d6")
                damage_type = "lightning"

                player_subtable = [name, damage, damage_type]

                player_table.append(player_subtable)

                break

            elif arg in ("acid", "acid_arrow"): 

                name = "Weak Acid Arrow"
                damage = await self.multi_diceRoll("1d6")
                if critical is True:
                    damage += await self.multi_diceRoll_crunchyCrits("1d6")
                damage_type = "piercing"

                player_subtable = [name, damage, damage_type]

                player_table.append(player_subtable)

                name = "Weak Acid"
                damage = await self.multi_diceRoll("1d4")
                if critical is True:
                    damage += await self.multi_diceRoll_crunchyCrits("1d4")
                damage_type = "acid"

                player_subtable = [name, damage, damage_type]

                player_table.append(player_subtable)

                break

            elif arg in ("pwp", "purple_worm_poison_arrow"): 

                name = "Purple Worm Poison Arrow"
                damage = await self.multi_diceRoll("1d6")
                if critical is True:
                    damage += await self.multi_diceRoll_crunchyCrits("1d6")
                damage_type = "poison"

                player_subtable = [name, damage, damage_type]

                player_table.append(player_subtable)

                name = "Purple Worm Poison (DC 19 CON)"
                damage = await self.multi_diceRoll("12d6")
                if critical is True:
                    damage += await self.multi_diceRoll_crunchyCrits("12d6")
                damage_type = "poison"

                player_subtable = [name, damage, damage_type]

                player_table.append(player_subtable)

                break

            elif arg in ("exhaustion", "exhaustion_arrow", "spider_poison_arrow"): 

                name = "Exhaustion Poison Arrow"
                damage = await self.multi_diceRoll("1d6")
                if critical is True:
                    damage += await self.multi_diceRoll_crunchyCrits("1d6")
                damage_type = "piercing"

                player_subtable = [name, damage, damage_type]

                player_table.append(player_subtable)

                name = "Exhaustion Poison (DC 11 CON)"
                damage = await self.multi_diceRoll("2d8")
                if critical is True:
                    damage += await self.multi_diceRoll_crunchyCrits("2d8")
                damage_type = "poison"

                player_subtable = [name, damage, damage_type]

                player_table.append(player_subtable)

                break

            elif arg in ("adamantine", "adamantine_arrow"): 

                name = "Adamantine Arrow"
                damage = await self.multi_diceRoll("1d8")
                if critical is True:
                    damage += await self.multi_diceRoll_crunchyCrits("1d8")
                damage_type = "piercing"

                player_subtable = [name, damage, damage_type]

                player_table.append(player_subtable)

                break

        return player_table

    async def dnd_PlayerActionCalculator(self, args):

        try:

            # player_tables - List of all attack rolls
            #   -> player_table - List of all dice for single attack roll
            #       -> player_subtables - List of dice for single attack component

            player_tables = []

            # Determine the number of attacks
            number_of_rounds = 0
            number_of_attacks = 2
            for arg in args:
                if arg in ("1st", "first", "1"):
                    number_of_attacks = 3

            # Determine minimum critical hit
            minimum_crit = 20
            for arg in args:
                if arg in ("adamantine", "adamantine_arrow", "adamantine_bow"): 
                    minimum_crit = 19
                    break

            # Once per turn attacks
            used_Sneak_Attack = False
            used_Favored_Foe = False
            used_Zephyr_Strike = False
            used_Dread_Ambusher = False

            while number_of_rounds < number_of_attacks:
                number_of_rounds += 1

                # Stores all of the attack varriables
                player_table = []

                # Always use 1d20 to roll for attacks (before modifiers)
                dice_to_hit = "1d20"

                # Roll to attack
                to_hit = await self.multi_diceRoll(dice_to_hit)

                for arg in args:
                    # If the attack has advantage, roll again and take the higher number
                    if arg == "adv":
                        to_hit_adv = await self.multi_diceRoll(dice_to_hit)
                        if to_hit < to_hit_adv:
                            to_hit = to_hit_adv
                        break
                    # If the attack has disadvantage, roll again and take the lower number
                    elif arg == "dis":
                        to_hit_dis = await self.multi_diceRoll(dice_to_hit)
                        if to_hit > to_hit_dis:
                            to_hit = to_hit_dis
                        break

                # If the attack rolled a one, re-roll it (Halfling Lucky)
                if to_hit == 1:
                    to_hit = await self.multi_diceRoll(dice_to_hit)

                # If the attack rolled a one again, damage equals zero
                if to_hit == 1:
                    name = "Critical failure!"
                    damage = 0
                    damage_type = "none"

                    player_subtable = [name, damage, damage_type]

                    player_table.append(player_subtable)

                    player_tables.append(player_table)

                    continue

                # If the attack rolled higher than the minimum crit threshold, apply critical damage
                if to_hit >= minimum_crit:
                    critical = True
                else:
                    critical = False

                #
                # Weapon choice
                #

                for arg in args:

                    if arg == "spectre":
                        # do spectre attack rolls
                        to_hit_total = to_hit + 15

                        if critical is True:
                            name = "★ " + str(to_hit_total)
                        else:
                            name = str(to_hit_total)
                        damage = ""
                        damage_type = ""

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        # do spectre damage rolls
                        name = "Spectre Shortbow"
                        damage = await self.multi_diceRoll("1d6+8")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("1d6+8")
                        damage_type = "piercing"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        name = "Spectre Arrows"
                        damage = await self.multi_diceRoll("2d4")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("2d4")
                        damage_type = "force"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        player_ammo = await self.player_ammo(args, critical)
                        for x in player_ammo:
                            player_table.append(x)

                        name = "Weapon Pre-Ignitor"
                        damage = await self.multi_diceRoll("1d6")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("1d6")
                        damage_type = "fire"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        break

                    elif arg == "markv":
                        # do mark v attack rolls
                        to_hit_total = to_hit + 12

                        if critical is True:
                            name = "★ " + str(to_hit_total)
                        else:
                            name = str(to_hit_total)
                        damage = ""
                        damage_type = ""

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        # do mark v damage rolls
                        name = "Mark V Shortbow (Left)"
                        damage = await self.multi_diceRoll("1d6+5")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("1d6+5")
                        damage_type = "piercing"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        player_ammo = await self.player_ammo(args, critical)
                        for x in player_ammo:
                            player_table.append(x)

                        name = "Mark V Shortbow (Right)"
                        damage = await self.multi_diceRoll("1d6+5")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("1d6+5")
                        damage_type = "piercing"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        player_ammo = await self.player_ammo(args, critical)
                        for x in player_ammo:
                            player_table.append(x)

                        name = "Weapon Pre-Ignitor"
                        damage = await self.multi_diceRoll("1d6")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("1d6")
                        damage_type = "fire"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        break

                    elif arg == "marksman":
                        # do marksman attack rolls
                        to_hit_total = to_hit + 12

                        if critical is True:
                            name = "★ " + str(to_hit_total)
                        else:
                            name = str(to_hit_total)
                        damage = ""
                        damage_type = ""

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        # do marksman damage rolls
                        name = "Marksman Shortbow (Left)"
                        damage = await self.multi_diceRoll("1d6+5")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("1d6+5")
                        damage_type = "piercing"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        player_ammo = await self.player_ammo(args, critical)
                        for x in player_ammo:
                            player_table.append(x)

                        name = "Marksman Shortbow (Center)"
                        damage = await self.multi_diceRoll("1d6+5")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("1d6+5")
                        damage_type = "piercing"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        player_ammo = await self.player_ammo(args, critical)
                        for x in player_ammo:
                            player_table.append(x)

                        name = "Marksman Shortbow (Right)"
                        damage = await self.multi_diceRoll("1d6+5")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("1d6+5")
                        damage_type = "piercing"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        player_ammo = await self.player_ammo(args, critical)
                        for x in player_ammo:
                            player_table.append(x)

                        name = "Weapon Pre-Ignitor"
                        damage = await self.multi_diceRoll("1d6")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("1d6")
                        damage_type = "fire"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        break

                    elif arg == "chargeup":
                        # do charge up attack rolls
                        to_hit_total = to_hit + 12

                        if critical is True:
                            name = "★ " + str(to_hit_total)
                        else:
                            name = str(to_hit_total)
                        damage = ""
                        damage_type = ""

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        # do charge up damage rolls
                        name = "Charge Up Shortbow"
                        damage = await self.multi_diceRoll("1d6+5")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("1d6+5")
                        damage_type = "piercing"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        player_ammo = await self.player_ammo(args, critical)
                        for x in player_ammo:
                            player_table.append(x)

                        name = "Weapon Pre-Ignitor"
                        damage = await self.multi_diceRoll("1d6")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("1d6")
                        damage_type = "fire"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        break

                    elif arg in ("usp", "usp9"): 
                        # do usp attack rolls
                        to_hit_total = to_hit + 12

                        if critical is True:
                            name = "★ " + str(to_hit_total)
                        else:
                            name = str(to_hit_total)
                        damage = ""
                        damage_type = ""

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        # do usp damage rolls
                        name = "USP9"
                        damage = await self.multi_diceRoll("2d6+5")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("2d6+5")
                        damage_type = "piercing"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        break

                # if no valid weapon return an error
                if player_table == []:
                    name = "Error!"
                    damage = 0
                    damage_type = "No valid weapon!"

                    player_subtable = [name, damage, damage_type]

                    player_table.append(player_subtable)

                    player_tables.append(player_table)

                    continue

                #
                # Charge-Up Shortbow
                #

                for arg in args:

                    if arg in ("c1", "charge1"): 

                        name = "Charge (1)"
                        damage = await self.multi_diceRoll("1d6")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("1d6")
                        damage_type = "lightning"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        break

                    elif arg in ("c2", "charge2"): 

                        name = "Charge (2)"
                        damage = await self.multi_diceRoll("2d6")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("2d6")
                        damage_type = "lightning"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        break

                    elif arg in ("c3", "charge3"): 

                        name = "Charge (3)"
                        damage = await self.multi_diceRoll("3d6")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("3d6")
                        damage_type = "lightning"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        break

                    elif arg in ("c4", "charge4"): 

                        name = "Charge (4)"
                        damage = await self.multi_diceRoll("4d6")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("4d6")
                        damage_type = "lightning"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        break

                    elif arg in ("c5", "charge5"): 

                        name = "Charge (5)"
                        damage = await self.multi_diceRoll("5d6")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("5d6")
                        damage_type = "lightning"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        break

                #
                # Sharpshooter
                #

                for arg in args:

                    if arg in ("sharpshooter", "ss"): 
                        to_hit_total -= 5

                        name = "Sharpshooter"
                        damage = await self.multi_diceRoll("10")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("10")
                        damage_type = "piercing"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        break

                #
                # Spells
                #

                for arg in args:

                    if arg in ("hunters_mark", "hm"): 

                        name = "Hunters Mark"
                        damage = await self.multi_diceRoll("1d6")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("1d6")
                        damage_type = "piercing"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        break

                    if arg in ("favored_foe", "ff"): 

                        if used_Favored_Foe is False:
                            name = "Favored Foe"
                            damage = await self.multi_diceRoll("1d6")
                            if critical is True:
                                damage += await self.multi_diceRoll_crunchyCrits("1d6")
                            damage_type = "piercing"

                            player_subtable = [name, damage, damage_type]

                            player_table.append(player_subtable)

                            used_Favored_Foe = True

                        break

                    if arg in ("zephyr_strike", "zephyr", "zs"): 

                        if used_Zephyr_Strike is False:
                            name = "Zephyr Strike"
                            damage = await self.multi_diceRoll("1d8")
                            if critical is True:
                                damage += await self.multi_diceRoll_crunchyCrits("1d8")
                            damage_type = "force"

                            player_subtable = [name, damage, damage_type]

                            player_table.append(player_subtable)

                            used_Zephyr_Strike = True

                        break

                #
                # Sneak Attack
                #

                if used_Sneak_Attack is False:

                    name = "Sneak Attack"
                    damage = await self.multi_diceRoll("1d6")
                    if critical is True:
                        damage += await self.multi_diceRoll_crunchyCrits("1d6")
                    damage_type = "piercing"

                    player_subtable = [name, damage, damage_type]

                    player_table.append(player_subtable)

                    used_Sneak_Attack = True

                #
                # Dread Ambusher
                #

                if number_of_rounds == 3:

                    if used_Dread_Ambusher is False:

                        name = "Dread Ambusher"
                        damage = await self.multi_diceRoll("1d8")
                        if critical is True:
                            damage += await self.multi_diceRoll_crunchyCrits("1d8")
                        damage_type = "piercing"

                        player_subtable = [name, damage, damage_type]

                        player_table.append(player_subtable)

                        used_Dread_Ambusher = True

                player_tables.append(player_table)

            return player_tables
        except Exception as e:
            print(e)

# ------------------------- DND COMMANDS ---------------------------

    @commands.hybrid_command(name="roll", help="rolls a dice")
    @commands.has_role("Bot Tester")
    async def roll(self, ctx, dice=None):
        diceInput = []
        diceOutput = []
        result = 0

        if not dice:
            await ctx.send("Please specify a dice to roll. Example: /roll 1d20")

        if dice:
            diceInput = dice.split("+")
            for x in diceInput:
                diceOutput.append(await self.diceRoll(x))

            for y in diceOutput:

                for value in y:

                    if value == "E":  # Error
                        await ctx.send("Oops, I couldn't read that. Sorry! >_<\nYou can try again, just make sure you entered everything right.")
                        return

                    elif value == "O":  # Overflow
                        await ctx.send("Whoa, that's a lot of dice! I only have about 200 dice I can use at once.\nYou can try again, just use fewer dice.")
                        return

                    elif value == "S":  # Size Overflow
                        await ctx.send("Uhh, I don't think they make dice that big. The largest dice I have is a D1000.\nYou can try again, just use smaller dice.")
                        return

                    else:
                        result = result + value

            # Flavor text for special d20 rolls
            if dice == "1d20" and result == 20:
                await ctx.send(":sparkles: CRITICAL!! For " + dice + ", you rolled: " + str(result))
            elif dice == "1d20" and result == 1:
                await ctx.send(":skull: FAILURE! For " + dice + ", you rolled: " + str(result))

            # Flavor text for d2 rolls
            elif dice == "1d2" and result == 1:
                await ctx.send(":coin: For the coin flip, you landed on Heads!")
            elif dice == "1d2" and result == 2:
                await ctx.send(":coin: For the coin flip, you landed on Tails!")

            # Don't show the result twice if there is only one dice
            elif "+" not in dice and dice[0] == "1":
                await ctx.send(":game_die: For " + dice + ", you rolled: " + str(result))
            else:
                await ctx.send(":game_die: For " + dice + ", you rolled: " + str(diceOutput) + "\n= " + str(result))

    @commands.hybrid_group(name="dnd", invoke_without_command=True)
    @commands.has_role("Bot Tester")
    async def dnd(self, ctx):
        await ctx.send("```Sure thing boss. Please specify a subcommand to use this feature.\nHere is the subcommand list for the 'dnd' command:\n    'spell': casts a spell.\n    'summon': quickly summon any number of any creatures in the database.\n    'colin': roleplay as the luckiest(?) ranger(?) alive(???).'''")

    @dnd.command(name="spell", help="casts a spell")
    @commands.has_role("Bot Tester")
    async def spell(self, ctx, *, args=None):

        summoning_spells = [
            "conjure_animals",
            "conjure_woodland_beings",
            "conjure_minor_elementals",
            "conjure_elemental",
            "conjure_fey",
            "conjure_celestial"
        ]

        if args is None:
            msg = """Here is a list of spells:
    === Summoning Spells ===
    Usage: /spell <spell name> <spell level> <creature name> <creature amount> <creature action> <adv / dis>
        /dnd spell conjure_animals 3 Velociraptor 8 Multiattack adv
        /dnd spell conjure_woodland_beings 4
        /dnd spell conjure_minor_elementals 4
        /dnd spell conjure_elemental 5
        /dnd spell conjure_fey 6
        /dnd spell conjure_celestial 6 """

            await ctx.send(msg)

        else:

            args = args.split()
            
            spell = args[0]

        # Use a summoning spell
        if spell in summoning_spells:
            try:
                spell_level = args[1]
            except IndexError:
                spell_level = None
            try:
                creature_name = args[2]
            except IndexError:
                creature_name = None
            try:
                creature_amount = args[3]
            except IndexError:
                creature_amount = None
            try:
                creature_action = args[4]
            except IndexError:
                creature_action = None
            try:
                adv = args[5]
            except IndexError:
                adv = None

            # If spell level is not int, try setting it as the creature name
            if creature_name is None:
                try:
                    spell_level = int(spell_level)
                except TypeError:
                    creature_name = spell_level

            # If no creature provided, list all valid creatures for that spell
            if creature_name is None:

                # Querys the database and generates a list of messages and tables
                tables = await self.dnd_SummonCreature(spell, spell_level, creature_name, creature_amount, creature_action, adv)

                # Querys the database for more informatio
                descriptions = None  # await database_lib.dnd_CreatureDescriptions(spell)

                # Creates a function that pages through all the entries
                await self.discord_message_pages(ctx, tables, descriptions)

            elif creature_action is None:
                
                # Querys the database and generates a list of messages and tables
                tables = await self.dnd_SummonCreature(spell, spell_level, creature_name, creature_amount, creature_action, adv)

                # Querys the database for more informatio
                descriptions = None  # await database_lib.dnd_CreatureDescriptions(spell)

                # Creates a function that pages through all the entries
                await self.discord_message_pages(ctx, tables, descriptions)

            else:
                # Querys the database and generates a list of messages and tables
                tables = await self.dnd_SummonCreature(spell, spell_level, creature_name, creature_amount, creature_action, adv)

                for msg in tables:
                    await ctx.send(msg)

        # If no valid spell provided
        else:
            msg = "That isn't a valid spell. Use /spell to get a list of valid spells."
            await ctx.send(msg)

    @dnd.command(name="summon", help="summons a creature to perform an action")
    @commands.has_role("Bot Tester")
    async def summon(self, ctx, creature_name=None, creature_amount=None, creature_action=None, adv=None):

        # If no creature provided, list all valid creatures for that spell
        if creature_name is None:

            # Querys the database and generates a list of messages and tables
            tables = await self.dnd_SummonCreature("override", "10", creature_name, creature_amount, creature_action, adv)

            # Querys the database for more informatio
            descriptions = None  # await database_lib.dnd_CreatureDescriptions(spell)

            # Creates a function that pages through all the entries
            await self.discord_message_pages(ctx, tables, descriptions)

        elif creature_action is None:
            
            # Querys the database and generates a list of messages and tables
            tables = await self.dnd_SummonCreature("override", "10", creature_name, creature_amount, creature_action, adv)

            # Querys the database for more informatio
            descriptions = None  # await database_lib.dnd_CreatureDescriptions(spell)

            # Creates a function that pages through all the entries
            await self.discord_message_pages(ctx, tables, descriptions)

        else:
            
            # Querys the database and generates a list of messages and tables
            tables = await self.dnd_SummonCreature("override", "10", creature_name, creature_amount, creature_action, adv)

            for msg in tables:
                await ctx.send(msg)

    @dnd.command(name="colin", help="perform an attack action as colin rahu")
    @commands.has_role("Bot Tester")
    async def colin(self, ctx, *, args):

        try:

            player_tables_msg = []

            args = args.split()

            # Get all of the attack data
            player_actions = await self.dnd_PlayerActionCalculator(args)

            # Counts how many rows have been iterated
            m = 0

            # While there are still rows to iterate
            for action in player_actions:
                # Creates empty table body
                player_tables_body = []
                # Tracks the total damage of all attacks
                player_damage_total = 0

                # Counts how many rows have been iterated
                n = 0
                m += 1

                # While there are still rows to iterate
                player_tables_body.append(["Attack #" + str(m), "", ""])

                while n < len(action):
                    # Append the next row to the body
                    player_tables_body.append(action[n])
                    # Adds the damage to the total damage
                    if action[n][1] != "":
                        player_damage_total += action[n][1]
                    n += 1

                footer = "Total Damage: " + str(player_damage_total)

                # Build the table
                player_tables = table2ascii(
                    header=["Damage Source", "Damage", "Damage Type"],
                    body=player_tables_body,
                    footer=[footer, Merge.LEFT, Merge.LEFT,],
                    alignments=[Alignment.LEFT, Alignment.LEFT, Alignment.LEFT],

                )

                player_tables_msg.append("```" + player_tables + "```")

            for msg in player_tables_msg:
                await ctx.send(msg)

        except Exception as e:
            print(e)
