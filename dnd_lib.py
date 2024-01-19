
import random


async def diceRoll(dice):
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


async def diceRoll_crunchyCrits(dice):
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


async def multi_diceRoll(dice):
    diceInput = []
    diceOutput = []
    result = 0

    diceInput = dice.split("+")
    for x in diceInput:
        diceOutput.append(await diceRoll(x))

    for y in diceOutput:
        for value in y:
            result = result + value

    return result


async def multi_diceRoll_crunchyCrits(dice):
    diceInput = []
    diceOutput = []
    result = 0

    diceInput = dice.split("+")
    for x in diceInput:
        diceOutput.append(await diceRoll_crunchyCrits(x))

    for y in diceOutput:
        for value in y:
            result = result + value

    return result
