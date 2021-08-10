import discord
from discord.ext import tasks, commands
import random
import os
import re
from dotenv import load_dotenv
import asyncio
import datetime
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

load_dotenv() #load .env

class VCHandler(commands.Cog):
    """Chat głosowy"""
    def __init__(self, bot):
        self.bot = bot

        self.AutoJoinDefaultVC.start() #start joining loop

        if self.bot.settings["debug"]["vc_handler"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler]Loaded")


    #join user's voice channel
    async def _join(self, ctx):
        user_vc:discord.Member=ctx.author.voice.channel #get user's vc

        same_channel = False

        if user_vc != None: #user has to be in the vc
            if(self.bot.voice_clients != []): #if bot is on any server's vc
                for vc in self.bot.voice_clients: #cycle through all servers
                    if(vc.channel == user_vc): #bot is already on the same vc
                        same_channel = True

                        if isinstance(ctx, SlashContext): #slash command
                            await ctx.send("Jestem już na twoim kanale", hidden=True)
                        else: #normal command
                            await ctx.reply("Jestem już na twoim kanale", delete_after=5)

                        if self.bot.settings["debug"]["vc_handler"]:
                            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_join]Bot is in the same vc\n')

                        return

                #User isn't on the same vc
                if same_channel == False: 
                    for vc in self.bot.voice_clients: #cycle through all servers
                        if vc.guild == user_vc.guild: #bot is on the same guild, but on other channel
                            await vc.disconnect() #disconnect from old vc

                            vc = await user_vc.connect() #join user vc

                            if isinstance(ctx, SlashContext): #slash command
                                await ctx.send("Dołączam na kanał `" + str(user_vc.name) + "`", hidden=True)
                            else: #normal command
                                await ctx.reply("Dołączam na kanał `" + str(user_vc.name) + "`", delete_after=5)

                            await self.PlaySound(vc, self.bot.settings["audio"]["greetings"])

                            if self.bot.settings["debug"]["vc_handler"]:
                                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_join]Bot joined vc (bot was on the other channel)')

                            return
                    
                    #bot isn't connected to any of the server's vc
                    vc = await user_vc.connect() #connect to the requested channel        

                    if isinstance(ctx, SlashContext): #slash command
                        await ctx.send("Dołączam na kanał `" + str(user_vc.name) + "`", hidden=True)
                    else: #normal command
                        await ctx.reply("Dołączam na kanał `" + str(user_vc.name) + "`", delete_after=5)

                    await self.PlaySound(vc, self.bot.settings["audio"]["greetings"])

                    if self.bot.settings["debug"]["vc_handler"]:
                        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_join]Bot joined vc (bot wasnt connected)')

    @commands.command(name = 'join',
        aliases = ['j', 'joi', 'dolacz', 'dołącz', 'connect', 'enter'], 
        brief = "Dołącza na twój kanał głosowy", 
        help = "Bot dołącza na kanał głosowy, na którym jest użytkownik", 
        usage = "yo join"
    )
    async def _join_command(self, ctx):
        if self.bot.settings["debug"]["vc_handler"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_join_command]{ctx.author.name} requested normal command')

        await self._join(ctx)

    #slash command
    @cog_ext.cog_slash(name="join", 
        description="Dołącza na twój kanał głosowy"
    )
    async def _join_slash(self, ctx:SlashContext):
        if self.bot.settings["debug"]["vc_handler"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_join_slash]{ctx.author.name} requested slash command')

        await self._join(ctx)


    #leave from current voice channel
    async def _leave(self, ctx):
        user_vc:discord.Member=ctx.author.voice.channel #get user's vc

        same_channel = False

        if user_vc != None: #user has to be in the vc
            if(self.bot.voice_clients != []): #if bot is on any server's vc
                for vc in self.bot.voice_clients: #cycle through all servers
                    if(vc.channel == user_vc): #bot is already on the same vc
                        same_channel = True
                        
                        if vc.is_playing() == True:
                            vc.stop() #stop playing

                        await self.PlaySound(vc, self.bot.settings["audio"]["farewells"]) #play farewell voice line

                        #cooldown before saying member name
                        while vc.is_playing(): #Checks if voice is playing
                            await asyncio.sleep(0.1) #While it's playing it sleeps for .1 of a second

                        await vc.disconnect() #leave

                        if isinstance(ctx, SlashContext): #slash command
                            await ctx.send("Wychodzę z kanału `" + str(user_vc.name) + "`", hidden=True)
                        else: #normal command
                            await ctx.reply("Wychodzę z kanału `" + str(user_vc.name) + "`", delete_after=5)

                        if self.bot.settings["debug"]["vc_handler"]:
                            print(f'\033[F[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_leave]Bot left vc\n') #\033[F moves cursor to the beginning of the previous line

                        return

                #User isn't on the same vc
                if same_channel == False: 
                    for vc in self.bot.voice_clients: #cycle through all servers
                        if vc.guild == user_vc.guild: #bot is on the same guild, but on other channel
                            if isinstance(ctx, SlashContext): #slash command
                                await ctx.send('Nie jesteśmy na tym samym kanale głosowym', hidden=True)
                            else: #normal command
                                await ctx.reply('Nie jesteśmy na tym samym kanale głosowym', delete_after=5)

                            if self.bot.settings["debug"]["vc_handler"]:
                                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_leave]Bot and user arent in the same vc\n')

                            return

                    #bot isn't connected to any of the server's vc
                    if isinstance(ctx, SlashContext): #slash command
                        await ctx.send('Nie jestem na żadnym kanale głosowym', hidden=True)
                    else: #normal command
                        await ctx.reply('Nie jestem na żadnym kanale głosowym', delete_after=5)

                    if self.bot.settings["debug"]["vc_handler"]:
                        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_leave]Bot isnt on any vc\n')

    @commands.command(name = 'leave',
        aliases = ['l', 'leav', 'wyjdz', 'wyjdź', 'disconnect'], 
        brief = "Wychodzi z twojego kanału głosowego", 
        help = "Bot wychodzi z kanału głosowego, na którym jest użytkownik", 
        usage = "yo leave"
    )
    async def _leave_command(self, ctx):
        if self.bot.settings["debug"]["vc_handler"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_leave_command]{ctx.author.name} requested normal command')

        await self._leave(ctx)

    #slash command
    @cog_ext.cog_slash(name="leave", 
        description="Wychodzi z twojego kanału głosowego"
    )
    async def _leave_slash(self, ctx:SlashContext):
        if self.bot.settings["debug"]["vc_handler"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_leave_slash]{ctx.author.name} requested slash command')

        await self._leave(ctx)


    #universal play command with source detection (yt -> spotify -> bind -> tts)
    async def _play(self, ctx, text : str, source:str=None):
        soundboard_result = False
        yt_result = False

        youtube_regex = r'(https?://)?(www\.)?youtube\.(com|nl)/watch\?v=([-\w]+)'

        if (re.match(youtube_regex, text) or source == 'youtube') and self.bot.settings["setting"]["vc_handler"]["enable_yt_play"]:
            yt = self.bot.get_cog('YouTube')
            if yt is not None:
                yt_result = await yt._playyt(ctx, text)

                if self.bot.settings["debug"]["vc_handler"] and yt_result:
                    print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_play]Chose yt')


        if (yt_result == False or source == 'soundboard') and self.bot.settings["setting"]["vc_handler"]["enable_soundboard_play"]:
            soundboard = self.bot.get_cog('Soundboard')
            if soundboard is not None:
                soundboard_result = await soundboard._bind(ctx, text)

                if self.bot.settings["debug"]["vc_handler"] and soundboard_result:
                    print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_play]Chose soundboard')


        if ((yt_result == False and soundboard_result == False) or source == 'tts') and self.bot.settings["setting"]["vc_handler"]["enable_tts_play"]:
            tts = self.bot.get_cog('TTS')
            if tts is not None:
                await tts._tts(ctx, text)

                if self.bot.settings["debug"]["vc_handler"]:
                    print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_play]Chose tts')

    #normal command
    @commands.command(name = 'play',
        aliases = ['p', 'pla', 'odtwórz', 'odtworz', 'graj', 'start'], 
        brief = "Odtwarza link/bind/tts na twoim kanale (yo play [url/nazwa_binda/tekst])", 
        help = "Odtwarza url z youtube, bind lub tekst z tts na twoim kanale", 
        usage = "yo play [url/nazwa_binda/tekst]"
    )
    async def _play_command(self, ctx, text : str, *args):
        if self.bot.settings["debug"]["vc_handler"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_play_command]{ctx.author.name} requested normal command')

        #combine text to one string
        spaceText = ""
        for txt in args:
            spaceText += (" " + str(txt))
        text += spaceText

        await self._play(ctx, text)

    #slash command
    #@cog_ext.cog_slash(name="play", 
    #    description="Odtwarza link/bind/tts na twoim kanale", 
    #    options=[
    #        create_option(
    #            name="source",
    #            description="Rodzaj źródła do odtworzenia",
    #            option_type=3,
    #            required=True,
    #            choices=[
    #                #create_choice(
    #                #    name="Spotify",
    #                #    value="spotify"
    #                #),
    #                #create_choice(
    #                #    name="YouTube",
    #                #    value="youtube"
    #                #),
    #                create_choice(
    #                    name="Bind",
    #                    value="soundboard"
    #                ),
    #                create_choice(
    #                    name="TTS",
    #                    value="tts"
    #                )
    #            ]
    #        ),
    #        create_option(
    #            name="value", 
    #            description="Podaj co chcesz odtworzyć", 
    #            option_type=3, 
    #            required=True
    #        )
    #    ]
    #)
    #async def _play_slash(self, ctx:SlashContext, source:str, value : str):
    #    if self.bot.settings["debug"]["vc_handler"]:
    #        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_play_slash]{ctx.author.name} #requested slash command')
#
    #    await self._play(ctx, value, source)

    #slash command
    @cog_ext.cog_slash(name="play", 
        description="Odtwarza link/bind/tts na twoim kanale", 
        options=[
            create_option(
                name="value", 
                description="Podaj link/bind/tts do odtworzenia", 
                option_type=3, 
                required=True
            )
        ]
    )
    async def _play_slash(self, ctx:SlashContext, value : str):
        if self.bot.settings["debug"]["vc_handler"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_play_slash]{ctx.author.name}     requested slash command')

        await self._play(ctx, value)
  

    #stop playing on user's voice channel
    async def _stop(self, ctx):
        user_vc:discord.Member=ctx.author.voice.channel #get user's vc

        same_channel = False

        if user_vc != None: #user has to be in the vc
            if(self.bot.voice_clients != []): #if bot is on any server's vc
                for vc in self.bot.voice_clients: #cycle through all servers
                    if(vc.channel == user_vc): #bot is already on the same vc
                        same_channel = True
                        
                        if vc.is_playing() == True:
                            vc.stop() #stop playing

                            if isinstance(ctx, SlashContext): #slash command
                                await ctx.send("Zatrzymałem odtwarzanie na `" + str(user_vc.name) + "`", hidden=True)
                            else: #normal command
                                await ctx.reply("Zatrzymałem odtwarzanie na `" + str(user_vc.name) + "`", delete_after=5)

                            if self.bot.settings["debug"]["vc_handler"]:
                                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_stop]Stopped playing\n')

                        else:
                            if isinstance(ctx, SlashContext): #slash command
                                await ctx.send("Nic nie jest odtwarzane na `" + str(user_vc.name) + "`", hidden=True)
                            else: #normal command
                                await ctx.reply("Nic nie jest odtwarzane na `" + str(user_vc.name) + "`", delete_after=5)

                            if self.bot.settings["debug"]["vc_handler"]:
                                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_stop]Nothing is played right now\n')

                        return

                #User isn't on the same vc
                if same_channel == False: 
                    for vc in self.bot.voice_clients: #cycle through all servers
                        if vc.guild == user_vc.guild: #bot is on the same guild, but on other channel
                            if isinstance(ctx, SlashContext): #slash command
                                await ctx.send('Nie jesteśmy na tym samym kanale głosowym', hidden=True)
                            else: #normal command
                                await ctx.reply('Nie jesteśmy na tym samym kanale głosowym', delete_after=5)

                            if self.bot.settings["debug"]["vc_handler"]:
                                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_stop]Bot and user arent in the same vc\n')

                            return

                    #bot isn't connected to any of the server's vc
                    if isinstance(ctx, SlashContext): #slash command
                        await ctx.send('Nie jestem na żadnym kanale głosowym', hidden=True)
                    else: #normal command
                        await ctx.reply('Nie jestem na żadnym kanale głosowym', delete_after=5)

                    if self.bot.settings["debug"]["vc_handler"]:
                        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_stop]Bot isnt on any vc\n')

    @commands.command(name = 'stop',
        aliases = ['s', 'sto', 'zatrzymaj', 'wstrzymaj', 'cancel', 'pause'], 
        brief = "Zatrzymuje odtwarzanie", 
        help = "Zatrzymuje odtwarzanie na kanale, na którym jest użytkownik", 
        usage = "yo stop"
    )
    async def _stop_command(self, ctx):
        if self.bot.settings["debug"]["vc_handler"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_stop_command]{ctx.author.name} requested normal command')

        await self._stop(ctx)

    #slash command
    @cog_ext.cog_slash(name="stop", 
        description="Zatrzymuje odtwarzanie"
    )
    async def _stop_slash(self, ctx:SlashContext):
        if self.bot.settings["debug"]["vc_handler"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][_stop_slash]{ctx.author.name} requested slash command')

        await self._stop(ctx)


    #helper playing sound function
    async def PlaySound(self, vc : discord.VoiceChannel, array):
        voiceLineId = random.randint(0, (len(array)-1)) #pick random voice line

        #play voice line 
        if vc.is_playing() == False: #if not saying something
            vc.play(discord.FFmpegPCMAudio(self.bot.settings['audioPath'] + array[voiceLineId], options = "-loglevel error"), after=lambda e: print('Player error: %s' % e) if e else (print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][PlaySound]Played sound on {vc.channel.name}\n') if self.bot.settings["debug"]["vc_handler"] else None)) #play voice line on channel


    #auto join vc, and reconnect after disconnected for some time and bot isn't in other vs on same server
    @tasks.loop(seconds=3600.0)       
    async def AutoJoinDefaultVC(self):
        for guild in self.bot.guilds:

            if (str(guild.id) in self.bot.settings["setting"]["vc_handler"] and self.bot.settings["setting"]["vc_handler"][str(guild.id)]["enable_auto_join"]):
                vc = discord.utils.get(self.bot.voice_clients, guild=guild) #vc that bot is connected to

                if vc is None: #if bot isn't on any vc on this server
                    channel = discord.utils.get(guild.voice_channels, id=int(os.getenv(str(self.bot.settings["setting"]["vc_handler"][str(guild.id)]["auto_join_vc"])))) #get default voice channel
                    
                    if(channel != None):
                        vc = await channel.connect() #connect to channel

                        if len(channel.members) > 1: #if there is someone else in vc
                            await self.PlaySound(vc, self.bot.settings["audio"]["greetings"]) #play greeting voice line

                        if self.bot.settings["debug"]["vc_handler"]:
                            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_handler][AutoJoinDefaultVC]Auto-joined on {guild.name}\n')


    #wait before joining until bot is ready
    @AutoJoinDefaultVC.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(VCHandler(bot))