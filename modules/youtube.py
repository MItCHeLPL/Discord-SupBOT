import discord
from discord.ext import commands
import youtube_dl
import re
import datetime
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

class YouTube(commands.Cog):
    """Youtube sound"""
    def __init__(self, bot):
        self.bot = bot
    
        if self.bot.settings["debug"]["youtube"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][youtube]Loaded")


    async def _playyt(self, ctx, youtubeLink):
        #download vid
        ytdlopts = {
            'format': 'bestaudio/best',
            'outtmpl': self.bot.settings['ttsAudioPath'] + 'yt.%(ext)s',
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
                if meta['duration'] < self.bot.settings["setting"]["youtube"]["max_duration"]: #if shorter than max duration
                    ytdl.download([youtubeLink]) #download .mp3

                    vc = await self.Join(ctx) #join vc

                    if vc != None:

                        await self.PlaySound(vc) #play yt mp3

                        if isinstance(ctx, SlashContext): #slash command
                            await ctx.send("Odtwarzam film z YouTube", hidden=True)
                        else: #normal command
                            await ctx.reply("Odtwarzam film z YouTube", delete_after=5)

                        if self.bot.settings["debug"]["youtube"]:
                            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][youtube][_playyt]Playing {youtubeLink}')

                        return True

                else:
                    if isinstance(ctx, SlashContext): #slash command
                        await ctx.send("Film jest za długi", hidden=True)
                    else: #normal command
                        await ctx.reply("Film jest za długi", delete_after=5)

                    if self.bot.settings["debug"]["youtube"]:
                        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][youtube][_playyt]{youtubeLink} is too long\n')

                    return False

    #normal command
    @commands.command(name = 'playyt',
        aliases = ['playt', 'yt', 'youtube'], 
        brief = "Odtwarza dźwięk z filmu na YouTube (yo playyt [link])", 
        help = "Odtwarza dźwięk z podanego przez użytkownika linku do filmu na YouTube", 
        usage = "yo playyt [link]"
    )
    async def _playyt_command(self, ctx, link : str):
        if self.bot.settings["debug"]["youtube"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][youtube][_playyt_command]{ctx.author.name} requested normal command')

        await self._playyt(ctx, link)

    #slash command
    @cog_ext.cog_slash(name="youtube", 
        description="Odtwarza dźwięk z filmu na YouTube", 
        options=[
            create_option(
                name="link", 
                description="Podaj link do filmu na YouTube", 
                option_type=3, 
                required=True
            )
        ]
    )
    async def _playyt_slash(self, ctx:SlashContext, link : str):
        if self.bot.settings["debug"]["youtube"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][youtube][_playyt_slash]{ctx.author.name} requested slash command')

        await self._playyt(ctx, link)


    async def Join(self, ctx):
        user_vc:discord.Member=ctx.author.voice.channel #get user's vc

        same_channel = False

        if user_vc != None: #user has to be in the vc
            if(self.bot.voice_clients != []): #if bot is on any server's vc
                for vc in self.bot.voice_clients: #cycle through all servers
                    if(vc.channel == user_vc): #bot is already on the same vc
                        same_channel = True

                        if self.bot.settings["debug"]["youtube"]:
                            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][youtube][Join]Bot is in the same vc')

                        return vc

                if same_channel == False: #User isn't on the same vc
                    for vc in self.bot.voice_clients: #cycle through all servers
                        if vc.guild == user_vc.guild: #bot is on the same guild, but on other channel

                            if self.bot.settings["debug"]["youtube"]:
                                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][youtube][Join]Bot joined vc (bot was on the other channel)')

                            await vc.disconnect() #disconnect from old channel

                            return await user_vc.connect() #join user channel

                    #bot isn't connected to any of the server's vc
                    if self.bot.settings["debug"]["youtube"]:
                        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][youtube][Join]Bot joined vc (bot wasnt connected)')

                    return await user_vc.connect() #connect to the requested channel


    def PlaySound(self, vc : discord.VoiceChannel):
        if vc.is_playing() == True:
            vc.stop() #stop playing

            vc.play(discord.FFmpegPCMAudio(self.bot.settings['ttsAudioPath'] + 'yt.mp3', options = "-loglevel error"), after=lambda e: print('Player error: %s' % e) if e else (print(f'[{str(datetime.datetime.utcnow())[0:-7]}][youtube][PlaySound]Played yt sound on {vc.channel.name}\n') if self.bot.settings["debug"]["youtube"] else None)) #play sound on vc


def setup(bot):
    bot.add_cog(YouTube(bot))