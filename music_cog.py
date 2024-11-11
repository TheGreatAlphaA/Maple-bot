
import sys
    
# ffmpeg is a required dependancy of this project.
# Please install ffmpeg before running (sudo apt install ffmpeg)

try:
    from yt_dlp import YoutubeDL
except ModuleNotFoundError:
    print("Please install yt-dlp. (pip install yt-dlp)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    from youtubesearchpython import VideosSearch
except ModuleNotFoundError:
    print("Please install youtubesearchpython. (pip install youtube-search-python)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    import asyncio
except ModuleNotFoundError:
    print("Please install asyncio. (pip install asyncio)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")

try:
    import discord
    from discord.ext import commands
except ModuleNotFoundError:
    print("Please install discordpy. (pip install discord.py)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")


class music_cog(commands.Cog):
    # ==================================================================================== #
    #                                     DEFINITIONS                                      #
    # ==================================================================================== #
    def __init__(self, bot):
        self.bot = bot
    
        # all the music related stuff
        self.is_playing = False
        self.is_paused = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio/best'}
        self.FFMPEG_OPTIONS = {'options': '-vn'}

        self.vc = None
        self.ytdl = YoutubeDL(self.YDL_OPTIONS)
        
    # ==================================================================================== #
    #                                      FUNCTIONS                                       #
    # ==================================================================================== #

    # searching the item on youtube
    def search_yt(self, item):
        if item.startswith("https://"):
            title = self.ytdl.extract_info(item, download=False)["title"]
            return {'source': item, 'title': title}
        search = VideosSearch(item, limit=1)
        return {'source': search.result()["result"][0]["link"], 'title': search.result()["result"][0]["title"]}

    async def play_next(self):

        if len(self.music_queue) > 0:
            # remove the first element as it has already been played
            self.music_queue.pop(0)

        if len(self.music_queue) > 0:
            self.is_playing = True

            # get the first url
            m_url = self.music_queue[0][0]['source']

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, **self.FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))
        else:
            self.is_playing = False

    # ==================================================================================== #
    #                                    MAIN FUNCTION                                     #
    # ==================================================================================== #

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']
            # try to connect to voice channel if you are not already connected
            if self.vc is None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                # in case we fail to connect
                if self.vc is None:
                    await ctx.send("Sorry. I can't join that voice channel right now.")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])
            # remove the first element as you are currently playing it
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, **self.FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))

        else:
            self.is_playing = False

    # ==================================================================================== #
    #                                      COMMANDS                                        #
    # ==================================================================================== #

    @commands.hybrid_group(name="music", aliases=["m"], invoke_without_command=True)
    @commands.has_role("End User")
    async def music(self, ctx):
        try:
            msg = f"""
```Sure thing boss. Please specify a subcommand to use this feature.
Here is the subcommand list for the 'music' command:
{self.bot.command_prefix}music queue - displays the current music queue.
{self.bot.command_prefix}music play - finds the song on youtube and plays it in your current channel.
{self.bot.command_prefix}music skip - skips the current song being played.
{self.bot.command_prefix}music clear - stops the music and clears the queue.
{self.bot.command_prefix}music stop - disconnects the bot from the voice channel.
{self.bot.command_prefix}music pause - pauses the current song being played or resumes if already paused.
{self.bot.command_prefix}music resume - resumes playing the current song.
{self.bot.command_prefix}music remove - removes last song from the queue.
```
"""
            await ctx.send(msg)

        except Exception as e:
            print(f"Exception occured during command: /music: {e}")
            await ctx.send(f"Oops! I couldn't run the /music command: {e}")
            return

    @music.command(name="play", aliases=["p", "playing"], help="plays a selected song from youtube")
    @commands.has_role("End User")
    async def play(self, ctx, *, args):
        message = await ctx.send("Processing...")
        try:
            queue_length = len(self.music_queue)
            query = args
            try:
                voice_channel = ctx.author.voice.channel
            except AttributeError:
                await message.edit(content="You need to connect to a voice channel before I can do that.")
                return

            song = self.search_yt(query)
            if type(song) is True:
                await message.edit(content="Sorry, I couldn't play that song. You could try different keywords to get better results.")
            else:
                if self.is_playing:
                    await message.edit(content=f"**#{len(self.music_queue)+1} - '{song['title']}'** added to the queue")
                else:
                    await message.edit(content=f"**'{song['title']}'** added to the queue")  
                self.music_queue.append([song, voice_channel])
                if self.is_playing is False and queue_length == 0:
                    await self.play_music(ctx)

        except Exception as e:
            print(f"Exception occured during command: /music play: {e}")
            await message.edit(content=f"Oops! I couldn't run the /music play command: {e}")
            return

    @music.command(name="pause", help="pauses the current song being played or resumes if already paused")
    @commands.has_role("End User")
    async def pause(self, ctx):
        message = await ctx.send("Processing...")
        try:
            queue_length = len(self.music_queue)

            # Check if you are connected to a voice channel
            if self.vc is None or not self.vc.is_connected():
                await message.edit(content="I need to be connected to a voice channel before you can do that.")

            # Check if the queue is empty
            elif queue_length == 0:
                await message.edit(content="There isn't anything in the queue right now.")

            elif self.is_playing:
                self.is_playing = False
                self.is_paused = True
                self.vc.pause()
                await message.edit(content=":pause_button: Playback has been paused.")

            elif self.is_paused:
                self.is_paused = False
                self.is_playing = True
                self.vc.resume()
                await message.edit(content=":play_pause: Playback has resumed.")

            await asyncio.sleep(20)
            await message.delete()

        except Exception as e:
            print(f"Exception occured during command: /music pause: {e}")
            await message.edit(content=f"Oops! I couldn't run the /music pause command: {e}")
            return

    @music.command(name="resume", aliases=["r"], help="resumes playing the current song")
    @commands.has_role("End User")
    async def resume(self, ctx):
        message = await ctx.send("Processing...")
        try:
            queue_length = len(self.music_queue)

            # Check if you are connected to a voice channel
            if self.vc is None or not self.vc.is_connected():
                await message.edit(content="I need to be connected to a voice channel before you can do that.")

            # Check if the queue is empty
            elif queue_length == 0:
                await message.edit(content="There isn't anything in the queue right now.")

            elif self.is_paused:
                self.is_paused = False
                self.is_playing = True
                self.vc.resume()
                await message.edit(content=":play_pause: Playback has resumed.")

            await asyncio.sleep(20)
            await message.delete()

        except Exception as e:
            print(f"Exception occured during command: /music resume: {e}")
            await message.edit(content=f"Oops! I couldn't run the /music resume command: {e}")
            return

    @music.command(name="skip", aliases=["s"], help="skips the current song being played")
    @commands.has_role("End User")
    async def skip(self, ctx):
        message = await ctx.send("Processing...")
        try:
            queue_length = len(self.music_queue)

            # Check if you are connected to a voice channel
            if self.vc is None or not self.vc.is_connected():
                await message.edit(content="I need to be connected to a voice channel before you can do that.")

            # Check if the queue is empty
            elif queue_length == 0:
                await message.edit(content="There isn't anything in the queue right now.")

            else:
                self.vc.stop()
                await message.edit(content=":track_next: Playback has been skipped.")

            await asyncio.sleep(20)
            await message.delete()

        except Exception as e:
            print(f"Exception occured during command: /music skip: {e}")
            await message.edit(content=f"Oops! I couldn't run the /music skip command: {e}")
            return

    @music.command(name="queue", aliases=["q"], help="displays the current music queue")
    @commands.has_role("End User")
    async def queue(self, ctx):
        message = await ctx.send("Processing...")
        try:
            now_playing = ""
            queue = ""
            queue_length = len(self.music_queue)

            # Check if you are connected to a voice channel
            if self.vc is None or not self.vc.is_connected():
                await message.edit(content="I need to be connected to a voice channel before you can do that.")

            # Check if the queue is empty
            elif queue_length == 0:
                await message.edit(content="There isn't anything in the queue right now.")

            else:

                for i in range(queue_length):
                    # For the first item in the list, add to Now Playing
                    if i == 0:
                        now_playing = f"#{i+1} - {self.music_queue[i][0]['title']}\n"
                    # For all other items, add to Queue
                    else:
                        queue += f"#{i+1} - {self.music_queue[i][0]['title']}\n"

                if queue_length > 1:
                    await message.edit(content=f"```Now Playing:\n{now_playing}\nQueue:\n{queue}```")
                elif queue_length == 1:
                    await message.edit(content=f"```Now Playing:\n{now_playing}```")

        except Exception as e:
            print(f"Exception occured during command: /music queue: {e}")
            await message.edit(content=f"Oops! I couldn't run the /music queue command: {e}")
            return

    @music.command(name="clear", aliases=["c", "bin"], help="stops the music and clears the queue")
    @commands.has_role("End User")
    async def clear(self, ctx):
        message = await ctx.send("Processing...")
        try:
            queue_length = len(self.music_queue)

            # Check if you are connected to a voice channel
            if self.vc is None or not self.vc.is_connected():
                await message.edit(content="I need to be connected to a voice channel before you can do that.")

            # Check if the queue is empty
            elif queue_length == 0:
                await message.edit(content="There isn't anything in the queue right now.")

            else:
                if self.vc is not None:
                    self.vc.stop()
                self.music_queue = []
                await message.edit(content=":broom: Cleared the music queue!")

            await asyncio.sleep(20)
            await message.delete()

        except Exception as e:
            print(f"Exception occured during command: /music clear: {e}")
            await message.edit(content=f"Oops! I couldn't run the /music clear command: {e}")
            return

    @music.command(name="stop", aliases=["disconnect", "l", "d"], help="disconnects the bot from the voice channel")
    @commands.has_role("End User")
    async def stop(self, ctx):
        message = await ctx.send("Processing...")
        try:

            # Check if you are connected to a voice channel
            if self.vc is None:
                await message.edit(content="I need to be connected to a voice channel before you can do that.")

            else:
                self.is_playing = False
                self.is_paused = False
                self.music_queue = []

                self.vc.stop()
                await self.vc.disconnect()
                await message.edit(content=":woman_walking_facing_right: I've left the voice channel. See you later!")

                self.vc = None

            await asyncio.sleep(20)
            await message.delete()

        except Exception as e:
            print(f"Exception occured during command: /music stop: {e}")
            await message.edit(content=f"Oops! I couldn't run the /music stop command: {e}")
            return
    
    @music.command(name="remove", help="removes last song from the queue")
    @commands.has_role("End User")
    async def remove(self, ctx):
        message = await ctx.send("Processing...")
        try:
            queue_length = len(self.music_queue)

            # Check if you are connected to a voice channel
            if self.vc is None or not self.vc.is_connected():
                await message.edit(content="You need to connect to a voice channel before I can do that.")

            # Check if the queue is empty
            elif queue_length == 0:
                await message.edit(content="There isn't anything in the queue right now.")

            # Check if the queue is empty
            elif queue_length == 1:
                self.vc.stop()
                await message.edit(content=":track_previous: Got it. Removed the last song added to the playlist.")

            else:
                self.music_queue.pop()
                await message.edit(content=":track_previous: Got it. Removed the last song added to the playlist.")

            await asyncio.sleep(20)
            await message.delete()

        except Exception as e:
            print(f"Exception occured during command: /music remove: {e}")
            await message.edit(content=f"Oops! I couldn't run the /music remove command: {e}")
            return
