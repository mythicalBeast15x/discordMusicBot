import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
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
            return {'source': info['formats'][0]['url'],'title': info['title']}

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
