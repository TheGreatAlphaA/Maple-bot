
import sys

try:
    from discord.ext import commands
except ModuleNotFoundError:
    print("Please install discordpy. (pip install discord.py)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    import configparser
except ModuleNotFoundError:
    print("Please install configparser. (pip install configparser)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    import mysql.connector
except ModuleNotFoundError:
    print("Please install mysql-connector. (pip install mysql-connector-python)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")


class database_cog(commands.Cog):
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

        self.Init_Database()
        
    # ==================================================================================== #
    #                                      FUNCTIONS                                       #
    # ==================================================================================== #

    def Create_Database_Table(self, table_name):

        try:
            # Connect to the database
            mydb = mysql.connector.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_database
            )

            cursor = mydb.cursor(buffered=True)

            if table_name == "network_mac":
                query = """CREATE TABLE network_mac (ID int, MAC varchar(18), HOSTNAME varchar(50), IP_ADDRESS varchar(15))"""

            elif table_name == "network_public_ip":
                query = """CREATE TABLE network_public_ip (ID int, IP_ADDRESS varchar(15))"""

            elif table_name == "sb_players":
                query = """CREATE TABLE sb_players (ID int, MINECRAFT_USERNAME varchar(16), MINECRAFT_UUID varchar(32), SKYBLOCK_UUID varchar(32), COLLECTION int, DAYS_SINCE int)"""

            elif table_name == "dnd_creatures":
                query = """CREATE TABLE dnd_creatures (ID int, NAME varchar(64), TYPE varchar(64), CR decimal(3,2), SIZE varchar(32), AC int, HP_DICE varchar(32), HP_AVG int, HP_BONUS int, SPEED_WALK int, SPEED_SWIM int, SPEED_FLY int, SPEED_BURROW int, STR_STAT int, DEX_STAT int, CON_STAT, int, INT_STAT, int, WIS_STAT int, CHA_STAT int, PROFICIENCY int, SOURCE varchar(64), DESCRIPTION varchar(500), SPECIAL_FEATS varchar(1000))"""

            elif table_name == "dnd_creatures_attacks":
                query = """CREATE TABLE dnd_creatures_attacks (ID int, CREATURE_NAME varchar(64), CREATURE_ACTION varchar(64), CREATURE_ACTION_BONUS varchar(128), ATTACK_HIT_BASE int, ATTACK_HIT_MODIFIER int, ATTACK_HIT_PROFICIENCY int, ATTACK_HIT_TOTAL int, ATTACK_DAMAGE_DICE varchar(32), ATTACK_DAMAGE_FLAT int, ATTACK_DAMAGE_TYPE varchar(32), ATTACK_DESCRIPTION varchar(1000))"""
            
            elif table_name == "keywords":
                query = """CREATE TABLE keywords (ID int, KEYWORD varchar(32), NEGATIVE tinyint(1))"""

            elif table_name == "reminders":
                query = """CREATE TABLE reminders (ID int, REMINDER varchar(32), AUTHOR varchar(32), MESSAGE varchar(1500))"""

            elif table_name == "yt_channels":
                query = """CREATE TABLE yt_channels (ID int, NAME varchar(32), URL varchar(64), PLAYLIST_ID varchar(24), TAG varchar(32))"""

            elif table_name == "yt_videos":
                query = """CREATE TABLE yt_videos (ID int, CHANNEL_NAME varchar(32), VIDEO_NAME varchar(256), VIDEO_ID varchar(12), TAG varchar(32))"""
            cursor.execute(query)

            # Commit changes to database
            mydb.commit()

        except Exception as e:
            print(f"Error connecting to MySQL database: {e}")
            return

    def Init_Database(self):
            
        print("=============== DATABASE ===============")

        try:
            data = None
            connection = False

            # Connect to the database
            mydb = mysql.connector.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_database
            )

            cursor = mydb.cursor(buffered=True)

            query = """SELECT VERSION()"""
            cursor.execute(query)

            data = cursor.fetchone()

            if data:
                connection = True
                print(f"Validated connection to {self.db_database}.")
            else:
                connection = False

        except Exception as e:
            print(f"Error connecting to MySQL database. Make sure your account credentials are correctly configured in the info.ini file. {e}")
            sys.exit()

        if connection is False:
            print("Error connecting to MySQL database. Make sure your account credentials are correctly configured in the info.ini file.")
            sys.exit()

        elif connection is True:
            try:
                table_names = [
                    # Network
                    "network_mac",
                    "network_public_ip",
                    # Skyblock
                    "sb_players",
                    # DnD
                    "dnd_creatures",
                    "dnd_creatures_attacks",
                    # Keywords
                    "keywords",
                    # Reminders
                    "reminders",
                    # Youtube Notifications
                    "yt_channels",
                    "yt_videos"
                ]

                number_of_tables = len(table_names)
                number_of_validated_tables = 0

                for table_name in table_names:
                    # Clear old data
                    data = None

                    # Validate that all tables exist
                    query = """SELECT * FROM information_schema.tables WHERE table_name = %(table_name)s"""
                    cursor.execute(query, {'table_name': table_name})

                    data = cursor.fetchone()

                    if data:
                        number_of_validated_tables += 1
                    else:
                        print(f"Unable to find table named {table_name}.")
                        try:
                            self.Create_Database_Table(table_name)
                            print(f"Created a new table named {table_name}.")
                            number_of_validated_tables += 1
                        except Exception as e:
                            print(f"Error creating new table {table_name}: {e}")
                            return

                if number_of_validated_tables == number_of_tables:
                    print(f"Validated all tables in {self.db_database}.")
                else:
                    print("Warning! Errors detected in configuration. Some functions may not work as intended.")

            except Exception as e:
                print(f"Error connecting to MySQL database. Make sure your account credentials are correctly configured in the info.ini file. {e}")
                sys.exit()

        print("========================================")
