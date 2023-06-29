import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
from constants import Constants

Constants = Constants()
class Queue:
    def __int__(self):
        self.queue = []

    def enqueue(self, item):
        self.queue.insert(0, item)

    def dequeue(self):
        self.queue.pop()

    def peek(self):
        return self.queue[0]

    def is_empty(self):
        return len(self.queue) == 0

    def clear(self):
        for _ in self.queue:
            self.dequeue()

    def print_queue(self):
        print_list = ""
        for i in range(0, len(self.queue)):
            if i > Constants.MAX_QUEUE_DISPLAY: break
            print_list += self.queue[i][0]["title"] + '\n'
        return print_list


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.is_paused = False

        self.music_queue = Queue()
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = None

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" %item, download=False)['entries'][0]
            except Exception:
                return False
            return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if not self.music_queue.is_empty():
            self.is_playing = True
            m_url = self.music_queue.peek()[0]['source']
            self.music_queue.dequeue()
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    async def play_music(self, ctx):
        if not self.music_queue.is_empty():
            self.is_playing = True
            m_url = self.music_queue.peek()[0]['source']

            if self.vc or not self.vc.is_connected():
                self.vc = await self.music_queue.peek()[1].connect()

                if self.vc:
                    await ctx.send('Could not connect to the voice channel')
                    return
            else:
                await self.vc.move_to(self.music_queue.peek()[1])
                self.music_queue.dequeue()
                self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after = lambda e: self.play_next())
        else:
            self.is_playing = False

    @commands.command(name= "play", aliases=["p","playing"], help ="Play the selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("Connect to a voice channel!")
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not download song. Try a different format")
            else:
                await ctx.send("Song added to the queue")
                self.music_queue.enqueue([song, voice_channel])
                if not self.is_playing:
                    await self.play_music(ctx)

    @commands.command(name="pause", aliases=["p"], help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()

    @commands.command(name="resume", aliases=["r"], help="Resumes playing the current song being played")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Skips current song")
    async def skip(self,ctx,*args):
        if self.vc is not None and self.vc:
            self.vc.stop()
            await self.play_music(ctx)

    @commands.command(name="queue", aliases=["q"], help="Prints out all music in queue")
    async def queue(self,ctx):
        print_list = self.music_queue.print_queue()
        if print_list != "":
            message = "Here are the next " + Constants.MAX_QUEUE_DISPLAY + " songs:\n" + print_list
            await ctx.send(message)
        else:
            await ctx.send("No music in the queue")

    @commands.command(name='clear', aliases=["c, bin"], help="Clears all music in queue")
    async def clear(self, ctx, *args):
        if self.vc is not None and self.is_playing:
            self.vc.stop()
        self.music_queue.clear()
        await ctx.send("Music queue cleared")

    @commands.command(name ="leave", aliases=["l", "disconnect", "d"], help="Disconnects bot from voice channel")
    async def leave(self,ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()
