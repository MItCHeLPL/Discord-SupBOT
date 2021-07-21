import discord
from discord.ext import commands
import youtube_dl
import re

class YouTube(commands.Cog):
    """Youtube sound"""
    def __init__(self, bot):
        self.bot = bot
    

    @commands.command(name = 'playyt', aliases=['playt', 'yt', 'youtube'])
    async def _playyt(self, ctx, youtubeLink):
        """Odtwarza dźwięk z filmiku na YouTube (yo playyt [link])"""

        #download vid
        ytdlopts = {
            'format': 'bestaudio/best',
            'outtmpl': self.bot.data['ttsAudioPath'] + 'yt.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec':'mp3', 'preferredquality': '192'}],
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
        }

        #Check if link is valid
        youtube_regex = r'(https?://)?(www\.)?youtube\.(com|nl)/watch\?v=([-\w]+)'
        if re.match(youtube_regex, youtubeLink):

            with youtube_dl.YoutubeDL(ytdlopts) as ytdl:
                meta = ytdl.extract_info(youtubeLink, download=False)
                if meta['duration'] < self.bot.data["setting"]["youtube"]["max_duration"]: #if shorter than max duration
                    ytdl.download([youtubeLink])

                    vc = await self.Join(ctx) #join vc

                    await self.PlaySound(ctx, vc) #play yt mp3

                    await ctx.reply("Odtwarzam film z YouTube", delete_after=5)

                else:
                    await ctx.reply("Film jest za długi.", delete_after=5)


    async def Join(self, ctx):
        user=ctx.message.author #get user
        voice_channel=user.voice.channel #get user's vc

        same_channel = False

        if voice_channel != None: #user has to be in the vc
            if(self.bot.voice_clients != []): #if bot is on any server's vc
                for server in self.bot.voice_clients: #cycle through all servers
                    if(server.channel == voice_channel): #bot is already on the same vc
                        same_channel = True
                        break

                if same_channel == False: #User is on the same server's vc, but not the same channel
                    await ctx.reply("Dołączam na kanał `" + str(voice_channel.name) + "`", delete_after=5)
                    return await voice_channel.connect()

            else:
                await ctx.reply("Dołączam na kanał `" + str(voice_channel.name) + "`", delete_after=5)
                return await voice_channel.connect() #connect to the requested channel, bot isn't connected to any of the server's vc


    def PlaySound(self, channel : discord.VoiceChannel):
        for server in self.bot.voice_clients: #cycle through all servers
            if(server.channel == channel): #find current voice channel
                vc = server #get voice channel

                if vc.is_playing() == False: #if not saying something
                        vc.play(discord.FFmpegPCMAudio(self.bot.data['ttsAudioPath'] + 'yt.mp3'), after=lambda e: print('Player error: %s' % e) if e else None) #play sound on vc

                break 

def setup(bot):
    bot.add_cog(YouTube(bot))