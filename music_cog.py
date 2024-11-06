
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

    # searching the item on youtube
    def search_yt(self, item):
        if item.startswith("https://"):
            title = self.ytdl.extract_info(item, download=False)["title"]
            return {'source': item, 'title': title}
        search = VideosSearch(item, limit=1)
        return {'source': search.result()["result"][0]["link"], 'title': search.result()["result"][0]["title"]}

    async def play_next(self):

        if len(self.music_queue) > 0:
            self.is_playing = True

            # get the first url
            m_url = self.music_queue[0][0]['source']

            # remove the first element as you are currently playing it
            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, executable="ffmpeg", **self.FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))
        else:
            self.is_playing = False

    # infinite loop checking 
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
            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, **self.FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))

        else:
            self.is_playing = False

    @commands.hybrid_group(name="music", aliases=["m"], invoke_without_command=True)
    @commands.has_role("End User")
    async def music(self, ctx):
        await ctx.send("```Sure thing boss. Please specify a subcommand to use this feature.\nHere is the subcommand list for the 'music' command:\n    'q': displays the current music queue.\n    'p': finds the song on youtube and plays it in your current channel.\n    'skip': skips the current song being played.\n    'clear': stops the music and clears the queue.\n    'stop': disconnects the bot from the voice channel.\n    'pause': pauses the current song being played or resumes if already paused.\n    'resume': resumes playing the current song.\n    'remove': removes last song from the queue.```")

    @music.command(name="play", aliases=["p", "playing"], help="plays a selected song from youtube")
    @commands.has_role("End User")
    async def play(self, ctx, *, args):
        query = args
        try:
            voice_channel = ctx.author.voice.channel
        except Exception as e:
            print(e)
            await ctx.send("You need to connect to a voice channel before I can do that.")
            return
        if self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) is True:
                await ctx.send("Sorry, I couldn't play that song. You could try different keywords to get better results.")
            else:
                if self.is_playing:
                    await ctx.send(f"**#{len(self.music_queue)+2} -'{song['title']}'** added to the queue")  
                else:
                    await ctx.send(f"**'{song['title']}'** added to the queue")  
                self.music_queue.append([song, voice_channel])
                if self.is_playing is False:
                    await self.play_music(ctx)

    @music.command(name="pause", help="pauses the current song being played or resumes if already paused")
    @commands.has_role("End User")
    async def pause(self, ctx):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @music.command(name="resume", aliases=["r"], help="resumes playing the current song")
    @commands.has_role("End User")
    async def resume(self, ctx):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @music.command(name="skip", aliases=["s"], help="skips the current song being played")
    @commands.has_role("End User")
    async def skip(self, ctx):
        if self.vc is not None and self.vc:
            self.vc.stop()
            # try to play next in the queue if it exists
            await self.play_music(ctx)

    @music.command(name="queue", aliases=["q"], help="displays the current music queue")
    @commands.has_role("End User")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += f"#{i+1} -{self.music_queue[i][0]['title']}\n"

        if retval != "":
            await ctx.send(f"```queue:\n{retval}```")
        else:
            await ctx.send("There isn't anything in the queue right now.")

    @music.command(name="clear", aliases=["c", "bin"], help="stops the music and clears the queue")
    @commands.has_role("End User")
    async def clear(self, ctx):
        if self.vc is not None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Cleared the music queue!")

    @music.command(name="stop", aliases=["disconnect", "l", "d"], help="disconnects the bot from the voice channel")
    @commands.has_role("End User")
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()
    
    @music.command(name="remove", help="removes last song from the queue")
    @commands.has_role("End User")
    async def re(self, ctx):
        self.music_queue.pop()
        await ctx.send("Got it. Removed the last song added to the playlist.")
