
import sys
import json

import common_lib
import database_lib

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


# ---- importing .ini file

config = configparser.ConfigParser()
config.read("info.ini")

# This is the api key that identifies the bot
sb_api_key = config['SKYBLOCK']['hypixel_api_key']

# This is the list of player profiles
sb_players = database_lib.sb_profiles()


async def SkyblockGhastTearCollection(player, profile):
    url = "https://api.hypixel.net/skyblock/profile?key=" + sb_api_key + "&profile=" + profile
    resp = urllib.request.urlopen(url)
    data = json.load(resp)
    ghast_collection = data["profile"]["members"][player]["collection"]["GHAST_TEAR"]
    return ghast_collection


async def SkyblockMayorChecker():
    url = "https://api.hypixel.net/resources/skyblock/election?key=" + sb_api_key
    resp = urllib.request.urlopen(url)
    data = json.load(resp)

    mayor = []

    # Append the currently elected mayor
    mayor.append(data["mayor"]["name"])

    # Append the mayors up for election
    try:
        for i in range(5):
            mayor.append(data["current"]["candidates"][i]["name"])
    except KeyError:
        # Mayor election are not open yet!
        pass

    return mayor


async def SkyblockGeneralProfitabilityChecker(mayor, bazaar_data):
    ghast_instant_sell = bazaar_data["products"]["ENCHANTED_GHAST_TEAR"]["quick_status"]["sellPrice"]

    # Calculated using T12 Ghast Minions + Plasma Bucket + 1 Flycatcher + Mithril Infusion
    # 475.2 Enchanted Ghast Tears per minion
    # 0.99 is for bazaar 1% tax for sellers
    if mayor == "Derpy":
        # Doubled output when Derpy is mayor
        daily_gross = 475.2 * 30 * ghast_instant_sell * 2 * 0.99
    else:
        daily_gross = 475.2 * 30 * ghast_instant_sell * 0.99
    daily_expense = 0
    daily_net = daily_gross - daily_expense
    
    return int(daily_net)


async def SkyblockHyperCatalystProfitabilityChecker(mayor, bazaar_data):
    ghast_instant_sell = bazaar_data["products"]["ENCHANTED_GHAST_TEAR"]["quick_status"]["sellPrice"]
    hypercatalyst_buy_order = bazaar_data["products"]["HYPER_CATALYST"]["quick_status"]["sellPrice"]
    starfall_buy_order = bazaar_data["products"]["STARFALL"]["quick_status"]["sellPrice"]

    # Calculated using T12 Ghast Minions + 1 Flycatcher + Mithril Infusion + T5 Beacon Boost
    # 1612.8 Enchanted Ghast Tears per minion
    # 4 Hyper Catalysts per minion
    # 0.99 is for bazaar 1% tax for sellers
    if mayor == "Derpy":
        # Doubled output when Derpy is mayor
        daily_gross = 1612.8 * 30 * ghast_instant_sell * 2 * 0.99
    else:
        daily_gross = 1612.8 * 30 * ghast_instant_sell * 0.99

    daily_expense = (4 * 30 * hypercatalyst_buy_order) + (128 * starfall_buy_order)
    # Net profit for hypercatalysts needs to exceed baseline profit, otherwise, we would still make more money without them
    baseline = await SkyblockGeneralProfitabilityChecker(mayor, bazaar_data)
    daily_net = daily_gross - daily_expense - baseline
    
    return int(daily_net)


async def SkyblockTracker():
    # Estimated burden of this function is 5 API calls
    url = "https://api.hypixel.net/skyblock/bazaar?key=" + sb_api_key
    resp = urllib.request.urlopen(url)
    bazaar_data = json.load(resp)

    # Checks which mayors are elected or up for election
    mayors = await SkyblockMayorChecker()
    # Assigns the currently elected mayor
    mayor = mayors[0]
    # Calculates the estimates profit for today.
    profit_hyper = await SkyblockHyperCatalystProfitabilityChecker(mayor, bazaar_data)
    profit_gen = await SkyblockGeneralProfitabilityChecker(mayor, bazaar_data)

    ranking = [[] for i in range(len(sb_players))]

    # Compiles the ghast tear collection data for all 3 players being tracked
    for i in range(len(sb_players)):
        ranking[i].append(await SkyblockGhastTearCollection(sb_players[i][1], sb_players[i][2]))
        ranking[i].append(sb_players[i][0])
    ranking.sort(reverse=True)
    # This string contains the message that will be sent at the end.
    sb_tracker_msg = ""

    # Lists the ranked ghast collection leaderboard.
    for i in range(len(sb_players)):
        # Checks if any of the top 3 include myself
        if ranking[i][1] == "Alpha_A":
            if i == 0:
                sb_tracker_msg += ranking[i][1] + " has a ghast collection of " + str(ranking[i][0])
                sb_delta = ranking[i][0] - ranking[1][0]
                sb_tracker_msg += " (+" + str(sb_delta) + " from 2nd place)"
            else:
                sb_tracker_msg += ranking[i][1] + " has a ghast collection of " + str(ranking[i][0])
                sb_delta = ranking[0][0] - ranking[i][0]
                sb_tracker_msg += " (-" + str(sb_delta) + " from 1st place)"

            # Reads yesterday's delta
            # Delta is a vaule that determines the difference between myself and first place
            sb_delta_old = common_lib.convert_to_int(common_lib.read_from_txt("skyblock/delta.txt"))

            # Computes delta over time. This is helpful for spotting drastic changes
            sb_delta_ot = sb_delta - sb_delta_old[0]
            if sb_delta_ot > 0:
                sb_tracker_msg += " (+" + str(sb_delta_ot) + " \u0394)\n"
            else:
                sb_tracker_msg += " (" + str(sb_delta_ot) + " \u0394)\n"

            # Writes down today's delta to compare tomorrow
            common_lib.write_to_txt_overwrite("skyblock/delta.txt", str(sb_delta))

        else:
            # Lists the ghast collections for everyone else
            sb_tracker_msg += str(ranking[i][1]) + " has a ghast collection of " + str(ranking[i][0]) + "\n"

    # Check if a special mayor has been elected
    if mayor not in {"Aatrox", "Cole", "Diana", "Diaz", "Finnegan", "Foxy", "Marina", "Paul"}:
        sb_tracker_msg += "\n:person_in_tuxedo: Special Mayor " + mayor + " is in office today.\n"

    # Check if a special mayor is up for election
    try:
        # Assigns all the mayoral candidates
        candidates = []
        for i in [1, 2, 3, 4, 5]:
            candidates.append(mayors[i])
        for candidate in candidates:
            if candidate not in {"Aatrox", "Cole", "Diana", "Diaz", "Finnegan", "Foxy", "Marina", "Paul"}:
                sb_tracker_msg += "\n:person_in_tuxedo: Special Mayor " + candidate + " is up for election.\n"
    except IndexError:
        # No candidates avaliable
        pass

    # Total profit before adding hypercatalysts
    sb_tracker_msg += "\n:bar_chart: We made " + str(common_lib.human_format(profit_gen)) + " coins.\n"

    # Check if the estimated profit for using hypercatalysts today was positive
    if profit_hyper > 0:
        sb_tracker_msg += "\n:chart_with_upwards_trend: Today is PROFITABLE for Hyper Catalysts (+" + str(common_lib.human_format(profit_hyper)) + " coins)"
    else:
        sb_tracker_msg += "\n:chart_with_downwards_trend: Today is not profitable for Hyper Catalysts... (" + str(common_lib.human_format(profit_hyper)) + " coins)"

    return sb_tracker_msg
