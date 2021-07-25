import discord
from discord.ext import commands
import youtube_dl
import re

class YouTube(commands.Cog):
    """Youtube sound"""
    def __init__(self, bot):
        self.bot = bot
    
        if self.bot.data["debug"]["youtube"]:
            print(f"[youtube]Loaded")


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

                    await self.PlaySound(vc) #play yt mp3

                    await ctx.reply("Odtwarzam film z YouTube", delete_after=5)

                    if self.bot.data["debug"]["youtube"]:
                        print(f'[youtube][_playyt]Playing {youtubeLink}\n')

                    return True

                else:
                    await ctx.reply("Film jest za długi.", delete_after=5)

                    if self.bot.data["debug"]["youtube"]:
                        print(f'[youtube][_playyt]{youtubeLink} is too long\n')

                    return False


    async def Join(self, ctx):
        user_vc=ctx.message.author.voice.channel #get user's vc

        same_channel = False

        if user_vc != None: #user has to be in the vc
            if(self.bot.voice_clients != []): #if bot is on any server's vc
                for vc in self.bot.voice_clients: #cycle through all servers
                    if(vc.channel == user_vc): #bot is already on the same vc
                        same_channel = True

                        if self.bot.data["debug"]["youtube"]:
                            print(f'[youtube][Join]Bot is in the same vc')

                        return vc

                if same_channel == False: #User is on the same server's vc, but not the same channel
                    #await ctx.reply("Dołączam na kanał `" + str(voice_channel.name) + "`", delete_after=5)

                    if self.bot.data["debug"]["youtube"]:
                        print(f'[youtube][Join]Bot joined vc (bot was on the other channel)')

                    await vc.disconnect() #disconnect from old channel

                    return await user_vc.connect() #join user channel

            else:
                #await ctx.reply("Dołączam na kanał `" + str(voice_channel.name) + "`", delete_after=5)

                if self.bot.data["debug"]["youtube"]:
                    print(f'[youtube][Join]Bot joined vc (bot wasnt connected)')

                return await user_vc.connect() #connect to the requested channel, bot isn't connected to any of the server's vc


    def PlaySound(self, vc : discord.VoiceChannel):
        if vc.is_playing() == True:
            vc.stop() #stop playing

            vc.play(discord.FFmpegPCMAudio(self.bot.data['ttsAudioPath'] + 'yt.mp3', options = "-loglevel error"), after=lambda e: print('Player error: %s' % e) if e else (print(f'[youtube][PlaySound]Played yt sound on {vc.channel.name}') if self.bot.data["debug"]["youtube"] else None)) #play sound on vc


def setup(bot):
    bot.add_cog(YouTube(bot))