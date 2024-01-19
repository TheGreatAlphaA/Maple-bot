
import sys
import math

try:
    import asyncio
except ModuleNotFoundError:
    print("Please install asyncio. (pip install asyncio)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")


# ------------------------- Read from txt files -----------------


def read_from_txt(path):

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


# ------------------------- Write to txt files -----------------


def write_to_txt(path, txt):

    # Opens the txt file, and appends data to it
    try:
        f = open(path, "a")
        f.write("\n")
        f.write(txt.lower())
        f.close()

    except FileNotFoundError:
        print("Error! No txt file found!")
        return None


def write_to_txt_overwrite(path, txt):

    # Opens the txt file, and writes data to it
    try:
        f = open(path, "w")
        f.write(txt)
        f.close()

    except FileNotFoundError:
        print("Error! No txt file found!")
        return None


# ------------------------- Remove data from txt files -----------------


def remove_from_txt(path, txt):

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


# ------------------------- Convert char arrays to int arrays -----------------


def convert_to_int(array):
    try:
        new_array = [int(element) for element in array]
        return new_array
    except ValueError:
        print("Error! Expected ints, but got chars in convert_to_int")


# ------------------------- Make long numbers readable -----------------


def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])
