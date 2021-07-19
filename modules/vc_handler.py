import discord
from discord.ext import tasks, commands
import random
import os
import re
from dotenv import load_dotenv

load_dotenv() #load .env

class VCHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        #dotenv storing
        self.guild_id_bbsch = os.getenv('DISCORD_ID_BOBERSCHLESIEN')
        self.defvc_id_bbsch = os.getenv('DISCORD_ID_BBSCH_DEFAULT_VC')

        self.guild_id_scamelot = os.getenv('DISCORD_ID_SCAMELOT')
        self.defvc_id_scamelot = os.getenv('DISCORD_ID_SCAMELOT_DEFAULT_VC')

        self.guild_id_wojtini = os.getenv('DISCORD_ID_WOJTINI')
        self.defvc_id_wojtini = os.getenv('DISCORD_ID_WOJTINI_DEFAULT_VC')

        self.AutoJoinDefaultVC.start() #start joining loop


    @commands.command(name = 'join', aliases = ['j', 'joi', 'dolacz', 'dołącz', 'connect', 'enter'])
    async def _join(self, ctx):
        user=ctx.message.author #get user
        voice_channel=user.voice.channel #get user's vc

        same_channel = False

        if voice_channel != None: #user has to be in the vc
            if(self.bot.voice_clients != []): #if bot is on any server's vc
                for server in self.bot.voice_clients: #cycle through all servers
                    if(server.channel == voice_channel): #bot is already on the same vc
                        same_channel = True

                        ctx.reply("Jestem już na tym kanale", delete_after=5)

                        break

                if same_channel == False: #User is on the same server's vc, but not the same channel
                    vc = await voice_channel.connect()

                    await ctx.reply("Dołączam na kanał `" + str(voice_channel.name) + "`", delete_after=5)

                    await self.PlaySound(vc, self.bot.data["audio"]["greetings"])

            else:
                vc = await voice_channel.connect() #connect to the requested channel, bot isn't connected to any of the server's vc

                await ctx.reply("Dołączam na kanał `" + str(voice_channel.name) + "`", delete_after=5)

                await self.PlaySound(vc, self.bot.data["audio"]["greetings"])


    @commands.command(name = 'leave', aliases = ['l', 'leav', 'wyjdz', 'wyjdź', 'disconnect'])
    async def _leave(self, ctx):
        user=ctx.message.author #get user
        voice_channel=user.voice.channel #get user's vc

        same_channel = False

        if voice_channel != None: #user has to be in the vc
            if(self.bot.voice_clients != []): #if bot is on any server's vc
                for server in self.bot.voice_clients: #cycle through all servers
                    if(server.channel == voice_channel): #bot is already on the same vc
                        same_channel = True
                        vc = voice_channel
                        
                        if vc.is_playing() == False:
                            self.PlaySound(vc, self.bot.data["audio"]["farewells"]) #play farewell voice line

                        #leave
                        while vc.is_playing(): #Checks if voice is playing
                            await self._stop(ctx)
                            await server.disconnect() #leave

                            await ctx.reply("Wychodzę z kanału`" + str(voice_channel.name) + "`", delete_after=5)

                        break

                if same_channel == False: #User is on the same server's vc, but not the same channel
                    await ctx.reply('Nie jesteśmy na tym samym kanale głosowym', delete_after=5)

            else:
                await ctx.reply('Nie jestem na żadnym kanale głosowym', delete_after=5) #bot isn't connected to any of the server's vc


    #universal play command with source detection (yt -> spotify -> bind -> tts)
    @commands.command(name = 'play', aliases = ['p', 'pla', 'odtwórz', 'odtworz', 'graj', 'start'])
    async def _play(self, ctx, text : str, *args):
        soundboard_result = False
        spotify_result = False
        yt_result = False

        youtube_regex = r'(https?://)?(www\.)?youtube\.(com|nl)/watch\?v=([-\w]+)'
        spotify_regex = r'/^(?:spotify:|(?:https?:\/\/(?:open|play)\.spotify\.com\/))(?:embed)?\/?(album|track)(?::|\/)((?:[0-9a-zA-Z]){22})/'

        #get text after space
        spaceText = ""
        for txt in args:
            spaceText += (" " + str(txt))
        text = (text + spaceText) #combine text


        if re.match(youtube_regex, text):
            yt = self.bot.get_cog('youtube')
            if yt is not None:
                yt_result = await yt._play(ctx, text)
        
        if re.match(spotify_regex, text) and yt_result == False:
            spotify = self.bot.get_cog('spotify')
            if spotify is not None:
                spotify_result = await spotify._play(ctx, text)

        if yt_result == False and spotify_result == False:
            soundboard = self.bot.get_cog('soundboard')
            if soundboard is not None:
                bind = await soundboard._bind(ctx, text)

        if yt_result == False and spotify_result == False and soundboard_result == False:
            tts = self.bot.get_cog('tts')
            if tts is not None:
                await tts._tts(ctx, text)
  

    @commands.command(name = 'stop', aliases = ['s', 'sto', 'zatrzymaj', 'wstrzymaj', 'cancel', 'pause'])
    async def _stop(self, ctx):
        server = ctx.message.guild.voice_client #get server

        if(server != None):
            vc = server #get voice channel

            #if playing stop
            if vc.is_playing() == True:
                vc.stop()
                await ctx.reply("Zatrzymałem odtwarzanie.", delete_after=5)


    def PlaySound(self, channel : discord.VoiceChannel, array):
        for server in self.bot.voice_clients: #cycle through all servers
            if(server.channel == channel): #find current voice channel
                vc = server #get voice channel

                voiceLineId = random.randint(0, (len(array)-1)) #pick random voice line

                #play voice line 
                if vc.is_playing() == False: #if not saying something
                    vc.play(discord.FFmpegPCMAudio(self.bot.data['audioPath'] + array[voiceLineId]), after=lambda e: print('Player error: %s' % e) if e else None) #play voice line on channel

                break 


    #auto join vc, and reconnect after discornnected for some time and bot isn't in other vs on same server
    @tasks.loop(seconds=3600.0)        
    async def AutoJoinDefaultVC(self):
        for guild in self.bot.guilds:

            #Boberschlesien
            if(guild.id == self.guild_id_bbsch):

                vc = discord.utils.get(self.bot.voice_clients, guild=guild) #vc that bot is connected to

                if vc is None: #if bot isn't on any vc on this server
                    channel = discord.utils.get(guild.voice_channels, id=self.defvc_id_bbsch) #get default voice channel
                    
                    if(channel != None):
                        await channel.connect() #connect to channel
                        await self.PlaySound(channel, self.bot.data["audio"]["greetings"]) #play greeting voice line

            #Scamelot
            elif(guild.id == self.guild_id_scamelot):     

                vc = discord.utils.get(self.bot.voice_clients, guild=guild) #vc that bot is connected to

                if vc is None: #if bot isn't on any vc on this server
                    channel = discord.utils.get(guild.voice_channels, id=self.defvc_id_scamelot) #get default voice channel

                    if(channel != None):
                        await channel.connect() #connect to channel
                        await self.PlaySound(channel, self.bot.data["audio"]["greetings"])#play greeting voice line

            #Wojtini Industries
            elif(guild.id == self.guild_id_wojtini): 

                vc = discord.utils.get(self.bot.voice_clients, guild=guild) #vc that bot is connected to

                if vc is None: #if bot isn't on any vc on this server
                    channel = discord.utils.get(guild.voice_channels, id=self.defvc_id_wojtini) #get default voice channel

                    if(channel != None):
                        await channel.connect() #connect to channel
                        await self.PlaySound(channel, self.bot.data["audio"]["greetings"])#play greeting voice line


    #wait before joining until bot is ready
    @AutoJoinDefaultVC.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(VCHandler(bot))