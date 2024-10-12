import discord
from discord.ext import commands
import yt_dlp
import asyncio

# YTDL options for better search flexibility
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': 'True',
    'quiet': True,
    'default_search': 'auto'  # This allows searching by lyrics or title
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, search, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
       
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch5:{search}", download=not stream))
        if 'entries' in data:
            data = data['entries'][0]  
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename), data=data)

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="with  Balls"))

@client.command(name='play', help='Plays a song based on the search query (lyrics or title).')
async def play(ctx, *, search: str):
    if ctx.author.voice is None:
        await ctx.send("You need to be in a voice channel to use this command.")
        return

    channel = ctx.author.voice.channel
    voice_client = ctx.voice_client

    if voice_client is None:
        voice_client = await channel.connect()
    elif voice_client.channel != channel:
        await voice_client.move_to(channel)

    try:
   
        player = await YTDLSource.from_url(search, loop=client.loop, stream=True)
        voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=player.title))

        await ctx.send(f'Now playing: {player.title}')
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@client.command(name='stop', help='Stops the current song.')
async def stop(ctx):
    if ctx.voice_client is None:
        await ctx.send("I'm not connected to a voice channel.")
        return

   
    await ctx.voice_client.disconnect()

   
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="with  Balls"))

client.run('YOUR_BOT_TOKEN')
