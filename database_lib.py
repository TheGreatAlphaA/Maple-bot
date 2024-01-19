
import sys
import json
import math

import dnd_lib

try:
    from table2ascii import table2ascii, Merge, Alignment
except ModuleNotFoundError:
    print("Please install table2ascii. (pip install table2ascii)")
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
    print("Please install asyncio. (pip install configparser)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")


# ---- importing .ini file

config = configparser.ConfigParser()
config.read("info.ini")


# ------------------------- Database Definitions ---------------------------

db_host = config['DATABASE']['host']
db_user = config['DATABASE']['user']
db_password = config['DATABASE']['password']
db_database = config['DATABASE']['database']


"""
async def skyblockMinionMatterialsDatabaseUpdate():

    mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_database
    )

    mycursor = mydb.cursor()

    url = "https://api.hypixel.net/resources/skyblock/items?key=f19bbecb-b2d4-4c17-8d94-17ab678e033e"
    resp = urllib.request.urlopen(url)
    data = json.load(resp)

    sql_material_uuid = "SELECT MATERIAL_UUID FROM minion_materials"
    mycursor.execute(sql_material_uuid)
    material_uuid = mycursor.fetchall()

    # TODO - add additional check that matches the MATERIAL_ID from the database to the ID from skyblock before committing any changes
    for y in material_uuid:
        x = int(y[0])
        s = data["items"][x]["name"]
        material_name = s.replace("'", "")
        sql_material_name = "UPDATE minion_materials SET MATERIAL_NAME = '" + material_name + "' WHERE MATERIAL_UUID = '" + str(x) + "'"
        print(sql_material_name)
        mycursor.execute(sql_material_name)

        material_id = data["items"][x]["id"]
        sql_material_id = "UPDATE minion_materials SET MATERIAL_ID = '" + material_id + "' WHERE MATERIAL_UUID = '" + str(x) + "'"
        print(sql_material_id)
        mycursor.execute(sql_material_id)

        if "npc_sell_price" in data["items"][x]:
            material_sell_npc = data["items"][x]["npc_sell_price"]
        else:
            material_sell_npc = 0
        sql_material_sell_npc = "UPDATE minion_materials SET SELL_NPC = '" + str(material_sell_npc) + "' WHERE MATERIAL_UUID = '" + str(x) + "'"
        print(sql_material_sell_npc)
        mycursor.execute(sql_material_sell_npc)

    mydb.commit()
"""


def sb_profiles():

    # Creates an empty list
    result = []

    # Connect to the database
    mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_database
    )

    cursor = mydb.cursor(buffered=True)

    query = """SELECT ID, MINECRAFT_USERNAME, MINECRAFT_UUID, SKYBLOCK_UUID FROM sb_players"""
    cursor.execute(query)

    # Checks if query is empty
    if cursor.rowcount == 0:
        return None

    # Creates each table body
    skyblock_players = cursor.fetchall()

    for player in skyblock_players:
        player_attr = [player[1], player[2], player[3]]
        result.append(player_attr)

    return result


async def dnd_CreatureStatBlocks(spell):

    # Creates empty message list
    creatures_msgs = []

    # Connect to the database
    mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_database
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


async def dnd_isCreatureValidSummon(spell, creature_name):

    # Creature is assumed invalid until proven otherwise
    valid_creature = False

    # Connect to the database
    mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_database
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


async def dnd_CreatureActionStatBlocks(spell, creature_name):

    # Creates empty message list
    creatures_msgs = []

    # Connect to the database
    mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_database
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
    if await dnd_isCreatureValidSummon(spell, creature_name) is False:
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


async def dnd_isCreatureAmoutValid(spell, spell_level, creature_name, creature_amount):

    # Connect to the database
    mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_database
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
    if await dnd_isCreatureValidSummon(spell, creature_name) is False:
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


async def dnd_CreatureActionCalculator(spell, spell_level, creature_name, creature_amount_req, creature_action, adv):

    # Creates empty message list
    creatures_msgs = []

    # Connect to the database
    mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_database
    )

    cursor = mydb.cursor(buffered=True)

    # Checks if this spell can actually summon this creature
    if await dnd_isCreatureValidSummon(spell, creature_name) is False:
        creatures_msgs.append("Couldn't find that creature on this spell's summoning list. Please try again.")
        return creatures_msgs

    # Checks if the creature amount is a valid number:
    creature_amount = await dnd_isCreatureAmoutValid(spell, spell_level, creature_name, creature_amount_req)
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
                    to_hit = await dnd_lib.multi_diceRoll(dice_to_hit)

                    # If the attack has advantage, roll again and take the higher number
                    if adv == "adv":
                        to_hit_adv = await dnd_lib.multi_diceRoll(dice_to_hit)
                        if to_hit < to_hit_adv:
                            to_hit = to_hit_adv
                    # If the attack has disadvantage, roll again and take the lower number
                    elif adv == "dis":
                        to_hit_dis = await dnd_lib.multi_diceRoll(dice_to_hit)
                        if to_hit > to_hit_dis:
                            to_hit = to_hit_dis

                    # Add the hit modifiers and append to the list
                    creature_attack.append(to_hit + int(ATTACK_HIT_TOTAL))

                    # Assume critical faliure always misses
                    if to_hit == 1:
                        damage = 0

                    # Roll regular damage for regular hits
                    elif to_hit < 20:
                        damage = await dnd_lib.multi_diceRoll(ATTACK_DAMAGE_DICE)

                    # Roll regular crits for critical damage
                    # elif to_hit == 20:
                    #    damage = dnd_lib.multi_diceRoll(ATTACK_DAMAGE_DICE) + dnd_lib.multi_diceRoll(ATTACK_DAMAGE_DICE)

                    # Roll crunchy crits for critical damage
                    elif to_hit == 20:
                        damage = await dnd_lib.multi_diceRoll_crunchyCrits(ATTACK_DAMAGE_DICE) + await dnd_lib.multi_diceRoll(ATTACK_DAMAGE_DICE)

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


async def dnd_SummonCreature(spell, spell_level, creature_name, creature_amount, creature_action, adv):

    # Function to normalize user inputs
    def clean_input(s):
        return ' '.join(w[:1].upper() + w[1:] for w in s.split('_'))
    
    if creature_name is None:

        # Get a table of creatures that can be summoned with Conjure Animals
        creatures_msgs = await dnd_CreatureStatBlocks(spell)

        return creatures_msgs

    elif creature_action is None:

        # Clean creature name input
        creature_name = clean_input(creature_name)
        
        # Get a table of actions that this creature can perform
        creatures_msgs = await dnd_CreatureActionStatBlocks(spell, creature_name)

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
        creatures_msgs = await dnd_CreatureActionCalculator(spell, spell_level, creature_name, creature_amount, creature_action, adv)

        return creatures_msgs
