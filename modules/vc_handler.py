import discord
from discord.ext import commands
import random
import os
from dotenv import load_dotenv

load_dotenv() #load .env

class VCHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


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
                        break

                if same_channel == False: #User is on the same server's vc, but not the same channel
                    vc = await voice_channel.connect()
                    await self.PlaySound(vc, self.bot.data["audio"]["greetings"])

            else:
                vc = await voice_channel.connect() #connect to the requested channel, bot isn't connected to any of the server's vc
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

                        break

                if same_channel == False: #User is on the same server's vc, but not the same channel
                    await ctx.reply('Nie jesteśmy na tym samym kanale głosowym')

            else:
                await ctx.reply('Nie jestem na żadnym kanale głosowym') #bot isn't connected to any of the server's vc


    #TODO CREATE Add source detection (bind -> spotify -> yt -> tts)
    @commands.command(name = 'play', aliases = ['p', 'pla', 'odtwórz', 'odtworz', 'graj', 'start'])
    async def _play(self, ctx):
        return #TEMP


    @commands.command(name = 'stop', aliases = ['s', 'sto', 'zatrzymaj', 'wstrzymaj', 'cancel', 'pause'])
    async def _stop(self, ctx):
        server = ctx.message.guild.voice_client #get server

        if(server != None):
            vc = server #get voice channel

            #if playing stop
            if vc.is_playing() == True:
                vc.stop()


    def PlaySound(self, channel : discord.VoiceChannel, array):
        for server in self.bot.voice_clients: #cycle through all servers
            if(server.channel == channel): #find current voice channel
                vc = server #get voice channel

                voiceLineId = random.randint(0, (len(array)-1)) #pick random voice line

                #play voice line 
                if vc.is_playing() == False: #if not saying something
                    vc.play(discord.FFmpegPCMAudio(self.bot.data['audioPath'] + array[voiceLineId]), after=lambda e: print('Player error: %s' % e) if e else None) #play voice line on channel

                break 


    #TODO PUT this in task loop to auto join, and reconnect after discornnected for some time           
    async def AutoJoinDefaultVC(self):
        for guild in self.bot.guilds:

            #Boberschlesien
            if(guild.id == os.getenv('DISCORD_ID_BOBERSCHLESIEN')):
                channel = discord.utils.get(guild.voice_channels, id=os.getenv('DISCORD_ID_BBSCH_DEFAULT_VC')) #get default voice channel
                
                if(channel != None):
                    await channel.connect() #connect to channel
                    await self.PlaySound(channel, self.bot.data["audio"]["greetings"]) #play greeting voice line

            #Scamelot
            elif(guild.id == os.getenv('DISCORD_ID_SCAMELOT')):     
                channel = discord.utils.get(guild.voice_channels, id=os.getenv('DISCORD_ID_SCAMELOT_DEFAULT_VC')) #get default voice channel

                if(channel != None):
                    await channel.connect() #connect to channel
                    await self.PlaySound(channel, self.bot.data["audio"]["greetings"])#play greeting voice line

            #Wojtini Industries
            elif(guild.id == os.getenv('DISCORD_ID_WOJTINI')): 
                channel = discord.utils.get(guild.voice_channels, id=os.getenv('DISCORD_ID_WOJTINI_DEFAULT_VC')) #get default voice channel

                if(channel != None):
                    await channel.connect() #connect to channel
                    await self.PlaySound(channel, self.bot.data["audio"]["greetings"])#play greeting voice line


def setup(bot):
    bot.add_cog(VCHandler(bot))