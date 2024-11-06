import sys
import json

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
    from discord.ext import commands, tasks
except ModuleNotFoundError:
    print("Please install discordpy. (pip install discord.py)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")


class yt_notifications_cog(commands.Cog):
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

        self.api_key = self.config['NOTIFICATIONS']['youtube_api_key']

        self.bot_channel = int(self.config['DISCORD_CHANNELS']['bot_commands'])
        self.security_channel = int(self.config['DISCORD_CHANNELS']['security_news'])
        self.gaming_channel = int(self.config['DISCORD_CHANNELS']['gaming_news'])
        self.pc_hardware_channel = int(self.config['DISCORD_CHANNELS']['pc_hardware_news'])
        self.educational_channel = int(self.config['DISCORD_CHANNELS']['educational_news'])
        self.celebrity_channel = int(self.config['DISCORD_CHANNELS']['celebrity_news'])

        self.general_news_role = int(self.config['DISCORD_ROLES']['deal_notifications'])
        self.security_news_role = int(self.config['DISCORD_ROLES']['security_news'])
        self.gaming_news_role = int(self.config['DISCORD_ROLES']['gaming_news'])
        self.pc_hardware_news_role = int(self.config['DISCORD_ROLES']['pc_hardware_news'])
        self.educational_news_role = int(self.config['DISCORD_ROLES']['educational_news'])
        self.celebrity_news_role = int(self.config['DISCORD_ROLES']['celebrity_news'])

        self.yt_channels = {
            #   <channel_name>
            #       <channel_name>
            #       <playlist_id>
            #       <tag>

        }
        self.yt_videos = {
            #   <video_id>
            #       <channel_name>
            #       <video_id>
            #       <video_name>
            #       <tag>
        }

        self.YouTubeTrackerLoop.start()

    # ==================================================================================== #
    #                                YOUTUBE NOTIFICATIONS                                 #
    # ==================================================================================== #

    def GetDiscordChannel(self, tag):

        # Get the channel object from discord
        if tag == "security":
            channel = self.security_channel
        elif tag == "gaming":
            channel = self.gaming_channel
        elif tag == "pc_hardware":
            channel = self.pc_hardware_channel
        elif tag == "educational":
            channel = self.educational_channel
        elif tag == "celebrity":
            channel = self.celebrity_channel
        else:
            channel = self.bot_channel

        return self.bot.get_channel(channel)

    def GetDiscordRole(self, tag):

        # Get the channel object from discord
        if tag == "security":
            role = self.security_news_role
        elif tag == "gaming":
            role = self.gaming_news_role
        elif tag == "pc_hardware":
            role = self.pc_hardware_news_role
        elif tag == "educational":
            role = self.educational_news_role
        elif tag == "celebrity":
            role = self.celebrity_news_role
        else:
            role = self.general_news_role

        return f"<@&{role}>"

    def YouTubeGetPlaylistID(self, username):
        # Make an API call to YouTube to get the five most recent videos from a given channel's 'upload playlist'
        url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forHandle={username}&key={self.api_key}"
        resp = urllib.request.urlopen(url)
        api_data = json.load(resp)

        channel_id = api_data["items"][0]["id"]

        playlist_id = channel_id.replace("UC", "UU", 1)

        return playlist_id

    def YouTubeUpdateVideoIDs(self, channel_name, playlist_id, tag):

        try:
            # ------------------------------ Define the lists ------------------------------- #
            new_video_ids = []
            old_video_ids = []

            # ------------------------------ Get new video ids ------------------------------ #
            # Make an API call to YouTube to get the five most recent videos from a given channel's 'upload playlist'
            maxResults = 5
            url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults={maxResults}&playlistId={playlist_id}&key={self.api_key}"
            resp = urllib.request.urlopen(url)
            api_data = json.load(resp)

            for i in range(maxResults):
                new_video_ids.append(api_data["items"][i]["snippet"]["resourceId"]["videoId"])

            # ------------------------------ Get old video ids ------------------------------ #
            # Connect to the database
            mydb = mysql.connector.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_database
            )

            cursor = mydb.cursor(buffered=True)

            # Get a list of video ids from the database
            query = """SELECT VIDEO_ID FROM yt_videos WHERE CHANNEL_NAME = %(channel_name)s"""
            cursor.execute(query, {'channel_name': channel_name})

            db_data = cursor.fetchall()
            
            for i in range(len(db_data)):
                old_video_ids.append(db_data[i][0])

            # -------------------- Check the difference between old and new -------------------- #
            # If there is no difference, return none
            if set(old_video_ids) == set(new_video_ids):
                return None

            # If there are new videos, ammend the database and return the new video ids
            else:

                # -------------------- Remove unmonitored videos -------------------- #
                remove_these_videos = set(old_video_ids).difference(new_video_ids)

                for video_id in remove_these_videos:
                    query = """DELETE FROM yt_videos WHERE VIDEO_ID = %(video_id)s"""
                    cursor.execute(query, {'video_id': video_id})

                # -------------------- Add newly posted videos -------------------- #
                add_these_videos = set(new_video_ids).difference(old_video_ids)

                for video_id in add_these_videos:
                    for i in range(maxResults):
                        if video_id == api_data["items"][i]["snippet"]["resourceId"]["videoId"]:
                            video_name = api_data["items"][i]["snippet"]["title"]

                            query = """INSERT INTO yt_videos (CHANNEL_NAME, VIDEO_NAME, VIDEO_ID, TAG) VALUES (%(channel_name)s, %(video_name)s, %(video_id)s, %(tag)s)"""
                            cursor.execute(query, {'channel_name': channel_name, 'video_name': video_name, 'video_id': video_id, 'tag': tag})

                # Commit changes to database
                mydb.commit()

                return add_these_videos

        except Exception as e:
            print("Exception occured during YouTubeUpdateVideoIDs function: ", str(e))
            return

    def YoutubeInitUpdate(self):

        try:
            # Connect to the database
            mydb = mysql.connector.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_database
            )

            cursor = mydb.cursor(buffered=True)

            query = """SELECT NAME, PLAYLIST_ID, TAG FROM yt_channels"""
            cursor.execute(query)

            # Checks if query is empty
            if cursor.rowcount == 0:
                print("Error! The `yt_channels` database appears to be empty!")
                return

            # Organizes the data
            channel_data = cursor.fetchall()

            for i in range(len(channel_data)):
                # Assign friendly names to the data
                channel_name = channel_data[i][0]
                playlist_id = channel_data[i][1]
                tag = channel_data[i][2]

                # Defines the list of youtube channels
                channel_dict = {
                    "channel_name": channel_name,
                    "playlist_id": playlist_id,
                    "tag": tag
                }

                self.yt_channels[channel_name] = channel_dict

                query = """SELECT VIDEO_ID, VIDEO_NAME, TAG FROM yt_videos WHERE CHANNEL_NAME = %(channel_name)s"""
                cursor.execute(query, {'channel_name': channel_name})

                # Checks if query is empty
                if cursor.rowcount == 0:
                    # Initialize the database
                    self.YouTubeUpdateVideoIDs(channel_name, playlist_id, tag)

                # Organizes the data
                video_data = cursor.fetchall()

                for j in range(len(video_data)):
                    # Assign friendly names to the data
                    channel_name = channel_name
                    video_id = video_data[j][0]
                    video_name = video_data[j][1]
                    tag = video_data[j][2]

                    video_dict = {
                        "channel_name": channel_name,
                        "video_id": video_id,
                        "video_name": video_name,
                        "tag": tag
                    }

                    self.yt_videos[video_id] = video_dict

        except Exception as e:
            print("Exception occured during YoutubeInitUpdate function: ", str(e))
            return

    def YoutubeUpdate(self, channel_name):
        # playlist_id = self.yt_channels[channel_name]["playlist_id"]
        tag = self.yt_channels[channel_name]["tag"]

        try:
            # Connect to the database
            mydb = mysql.connector.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_database
            )

            cursor = mydb.cursor(buffered=True)

            query = """SELECT VIDEO_ID, VIDEO_NAME, TAG FROM yt_videos WHERE CHANNEL_NAME = %(channel_name)s"""
            cursor.execute(query, {'channel_name': channel_name})

            # Checks if query is empty
            if cursor.rowcount == 0:
                print(f"Error! The `yt_videos` database for {channel_name} appears to be empty!")
                return

            # Organizes the data
            video_data = cursor.fetchall()

            for j in range(len(video_data)):
                # Assign friendly names to the data
                channel_name = channel_name
                video_id = video_data[j][0]
                video_name = video_data[j][1]
                tag = video_data[j][2]

                video_dict = {
                    "channel_name": channel_name,
                    "video_id": video_id,
                    "video_name": video_name,
                    "tag": tag
                }

                self.yt_videos[video_id] = video_dict

        except Exception as e:
            print("Exception occured during YoutubeUpdate function: ", str(e))
            return

    @commands.hybrid_command(name="yt_playlist_id")
    @commands.is_owner()
    async def yt_playlist_id(self, ctx, youtube_username):

        try:

            playlist_id = self.YouTubeGetPlaylistID(youtube_username)

            if playlist_id is not None:
                await ctx.send(f"The playlist id for {youtube_username} is {playlist_id}")
            else:
                await ctx.send("Could not find a valid YouTube channel for that handle. Sorry.")

        except Exception as e:
            print("Exception occured during yt_playlist_id function: ", str(e))
            return

    @tasks.loop(seconds=900)
    async def YouTubeTrackerLoop(self):

        try:

            for channel in self.yt_channels.keys():
                channel_name = self.yt_channels[channel]["channel_name"]
                playlist_id = self.yt_channels[channel]["playlist_id"]
                tag = self.yt_channels[channel]["tag"]

                add_these_videos = self.YouTubeUpdateVideoIDs(channel_name, playlist_id, tag)

                if add_these_videos is None:
                    continue
                else:

                    # Update the dictionary
                    self.YoutubeUpdate(channel_name)

                    for video_id in add_these_videos:
                        video_name = self.yt_videos[video_id]["video_name"]
                        tag = self.yt_videos[video_id]["tag"]

                        url = f"https://youtu.be/{video_id}"

                        channel = self.GetDiscordChannel(tag)
                        role = self.GetDiscordRole(tag)

                        await channel.send(f"**{channel_name}** uploaded a video: **{video_name}**\n{role}\n{url}")

        except Exception as e:
            print("Exception occured during YouTubeTrackerLoop function: ", str(e))
            return

    @YouTubeTrackerLoop.before_loop
    async def before_YouTubeTrackerLoop(self):
        await self.bot.wait_until_ready()

        try:
            self.YoutubeInitUpdate()

        except Exception as e:
            print("Exception occured during before_YouTubeTrackerLoop function: ", str(e))
            return
