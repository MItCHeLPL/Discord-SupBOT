import discord
from discord.ext import tasks, commands
import random
import os
import re
from dotenv import load_dotenv
import asyncio

load_dotenv() #load .env

class VCHandler(commands.Cog):
    """Chat głosowy"""
    def __init__(self, bot):
        self.bot = bot

        self.AutoJoinDefaultVC.start() #start joining loop

        if self.bot.data["debug"]["vc_handler"]:
            print(f"[vc_handler]Loaded")


    @commands.command(name = 'join', aliases = ['j', 'joi', 'dolacz', 'dołącz', 'connect', 'enter'])
    async def _join(self, ctx):
        """Dołączna na twój kanał głosowy"""
        user_vc=ctx.message.author.voice.channel #get user's vc

        same_channel = False

        if user_vc != None: #user has to be in the vc
            if(self.bot.voice_clients != []): #if bot is on any server's vc
                for vc in self.bot.voice_clients: #cycle through all servers
                    if(vc.channel == user_vc): #bot is already on the same vc
                        same_channel = True

                        await ctx.reply("Jestem już na tym kanale", delete_after=5)

                        if self.bot.data["debug"]["vc_handler"]:
                            print(f'[vc_handler][_join]Bot is in the same vc\n')

                        break

                if same_channel == False: #User is on the same server's vc, but not the same channel
                    await vc.disconnect() #disconnect from old channel

                    vc = await user_vc.connect() #join user channel

                    await ctx.reply("Dołączam na kanał `" + str(user_vc.name) + "`", delete_after=5)

                    await self.PlaySound(vc, self.bot.data["audio"]["greetings"])

                    if self.bot.data["debug"]["vc_handler"]:
                        print(f'[vc_handler][_join]Bot joined vc (bot was on the other channel)\n')

            else:
                vc = await user_vc.connect() #connect to the requested channel, bot isn't connected to any of the server's vc

                await ctx.reply("Dołączam na kanał `" + str(user_vc.name) + "`", delete_after=5)

                await self.PlaySound(vc, self.bot.data["audio"]["greetings"])

                if self.bot.data["debug"]["vc_handler"]:
                    print(f'[vc_handler][_join]Bot joined vc (bot wasnt connected)\n')


    @commands.command(name = 'leave', aliases = ['l', 'leav', 'wyjdz', 'wyjdź', 'disconnect'])
    async def _leave(self, ctx):
        """Wychodzi z twojego kanału głosowego"""
        user_vc=ctx.message.author.voice.channel #get user's vc

        same_channel = False

        if user_vc != None: #user has to be in the vc
            if(self.bot.voice_clients != []): #if bot is on any server's vc
                for vc in self.bot.voice_clients: #cycle through all servers
                    if(vc.channel == user_vc): #bot is already on the same vc
                        same_channel = True
                        
                        if vc.is_playing() == True:
                            vc.stop() #stop playing

                        await self.PlaySound(vc, self.bot.data["audio"]["farewells"]) #play farewell voice line

                        #cooldown before saying member name
                        while vc.is_playing(): #Checks if voice is playing
                            await asyncio.sleep(0.1) #While it's playing it sleeps for .1 of a second

                        await vc.disconnect() #leave

                        await ctx.reply("Wychodzę z kanału`" + str(user_vc.name) + "`", delete_after=5)

                        if self.bot.data["debug"]["vc_handler"]:
                            print(f'[vc_handler][_leave]Bot left vc\n')

                        break

                if same_channel == False: #User is on the same server's vc, but not the same channel
                    await ctx.reply('Nie jesteśmy na tym samym kanale głosowym', delete_after=5)

                    if self.bot.data["debug"]["vc_handler"]:
                        print(f'[vc_handler][_leave]Bot and user arent in the same vc\n')

            else:
                await ctx.reply('Nie jestem na żadnym kanale głosowym', delete_after=5) #bot isn't connected to any of the server's vc

                if self.bot.data["debug"]["vc_handler"]:
                    print(f'[vc_handler][_leave]Bot isnt on any vc\n')


    #universal play command with source detection (yt -> spotify -> bind -> tts)
    @commands.command(name = 'play', aliases = ['p', 'pla', 'odtwórz', 'odtworz', 'graj', 'start'])
    async def _play(self, ctx, text : str, *args):
        """Odtwarza link/bind/tts na twoim kanale (yo play [url/nazwa_binda/tekst])"""
        soundboard_result = False
        yt_result = False

        youtube_regex = r'(https?://)?(www\.)?youtube\.(com|nl)/watch\?v=([-\w]+)'

        #get text after space
        spaceText = ""
        for txt in args:
            spaceText += (" " + str(txt))
        text = (text + spaceText) #combine text


        if re.match(youtube_regex, text) and self.bot.data["setting"]["vc_handler"]["enable_yt_play"]:
            yt = self.bot.get_cog('YouTube')
            if yt is not None:
                yt_result = await yt._playyt(ctx, text)

                if self.bot.data["debug"]["vc_handler"] and yt_result:
                    print(f'[vc_handler][_play]Chose yt')


        if yt_result == False and self.bot.data["setting"]["vc_handler"]["enable_soundboard_play"]:
            soundboard = self.bot.get_cog('Soundboard')
            if soundboard is not None:
                soundboard_result = await soundboard._bind(ctx, text)

                if self.bot.data["debug"]["vc_handler"] and soundboard_result:
                    print(f'[vc_handler][_play]Chose soundboard')


        if yt_result == False and soundboard_result == False and self.bot.data["setting"]["vc_handler"]["enable_tts_play"]:
            tts = self.bot.get_cog('TTS')
            if tts is not None:
                await tts._tts(ctx, text)

                if self.bot.data["debug"]["vc_handler"]:
                    print(f'[vc_handler][_play]Chose tts')
  

    @commands.command(name = 'stop', aliases = ['s', 'sto', 'zatrzymaj', 'wstrzymaj', 'cancel', 'pause'])
    async def _stop(self, ctx):
        """Zatrzymuje odtwarzanie"""
        user_vc=ctx.message.author.voice.channel #get user's vc

        same_channel = False

        if user_vc != None: #user has to be in the vc
            if(self.bot.voice_clients != []): #if bot is on any server's vc
                for vc in self.bot.voice_clients: #cycle through all servers
                    if(vc.channel == user_vc): #bot is already on the same vc
                        same_channel = True
                        
                        if vc.is_playing() == True:
                            vc.stop() #stop playing

                            await ctx.reply("Zatrzymałem odtwarzanie.", delete_after=5)

                            if self.bot.data["debug"]["vc_handler"]:
                                print(f'[vc_handler][_stop]Stopped playing\n')

                        else:
                            await ctx.reply("Nic nie jest odtwarzane.", delete_after=5)

                            if self.bot.data["debug"]["vc_handler"]:
                                print(f'[vc_handler][_stop]Nothing is played right now\n')

                        break

                if same_channel == False: #User is on the same server's vc, but not the same channel
                    await ctx.reply('Nie jesteśmy na tym samym kanale głosowym', delete_after=5)

                    if self.bot.data["debug"]["vc_handler"]:
                        print(f'[vc_handler][_stop]Bot and user arent in the same vc\n')

            else:
                await ctx.reply('Nie jestem na żadnym kanale głosowym', delete_after=5) #bot isn't connected to any of the server's vc

                if self.bot.data["debug"]["vc_handler"]:
                    print(f'[vc_handler][_stop]Bot isnt on any vc\n')


    async def PlaySound(self, channel : discord.VoiceChannel, array):
        for vc in self.bot.voice_clients: #cycle through all servers
            if(vc == channel): #find current voice channel
                voiceLineId = random.randint(0, (len(array)-1)) #pick random voice line

                #play voice line 
                if vc.is_playing() == False: #if not saying something
                    vc.play(discord.FFmpegPCMAudio(self.bot.data['audioPath'] + array[voiceLineId]), after=lambda e: print('Player error: %s' % e) if e else (print(f'[vc_handler][PlaySound]Played sound') if self.bot.data["debug"]["vc_handler"] else None)) #play voice line on channel

                break 


    #auto join vc, and reconnect after discornnected for some time and bot isn't in other vs on same server
    @tasks.loop(seconds=3600.0)       
    async def AutoJoinDefaultVC(self):
        for guild in self.bot.guilds:

            if (str(guild.id) in self.bot.data["setting"]["vc_handler"] and self.bot.data["setting"]["vc_handler"][str(guild.id)]["enable_auto_join"]):
                vc = discord.utils.get(self.bot.voice_clients, guild=guild) #vc that bot isconnected to

                if vc is None: #if bot isn't on any vc on this server
                    channel = discord.utils.get(guild.voice_channels, id=int(os.getenv(str(self.bot.data["setting"]["vc_handler"][str(guild.id)]["auto_join_vc"])))) #get default voice channel
                    
                    if(channel != None):
                        channel = await channel.connect() #connect to channel
                        await self.PlaySound(channel, self.bot.data["audio"]["greetings"]) #play greeting voice line

                        if self.bot.data["debug"]["vc_handler"]:
                            print(f'[vc_handler][AutoJoinDefaultVC]Auto-joined on {guild.name}')


    #wait before joining until bot is ready
    @AutoJoinDefaultVC.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(VCHandler(bot))