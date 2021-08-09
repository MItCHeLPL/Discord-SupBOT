import discord
from discord.ext import commands
import datetime
import random
import math
import datetime
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

class Soundboard(commands.Cog):
    """Bindy"""
    def __init__(self, bot):
        self.bot = bot

        if self.bot.settings["debug"]["soundboard"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][soundboard]Loaded")
    

    async def _bind(self, ctx, name : str):
        voiceline = name + '.mp3'

        if voiceline in self.bot.settings["audio"]['binds']:
            vc = await self.Join(ctx) #join vc

            if vc != None:
                await self.PlaySound(vc, voiceline) #play tts

                if isinstance(ctx, SlashContext): #slash command
                    await ctx.send('Odtwarzam binda `' + name + '`', hidden=True)
                else: #normal command
                    await ctx.reply('Odtwarzam binda `' + name + '`', delete_after=5)

                if self.bot.settings["debug"]["soundboard"]:
                    print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][_bind]Playing bind: {name}')

                return True

        else:
            if isinstance(ctx, SlashContext): #slash command
                await ctx.send('Nie znaleziono binda `' + name + '`', hidden=True)
            else: #normal command
                await ctx.reply('Nie znaleziono binda `' + name + '`', delete_after=5)

            if self.bot.settings["debug"]["soundboard"]:
                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][_bind]Sound not found\n')

            return False
    
    #normal command
    @commands.command(name = 'playbind',
        aliases = ['bind', 'soundboard', 'pb', 'ps', 'sound', 'playsound'], 
        brief = "Odtwarza binda (yo playbind [nazwa])", 
        help = "Odtwarza wskazanego przez użytkownika binda. Lista bindów dostępna używając: (yo bindlist)", 
        usage = "yo playbind [nazwa]"
    )
    async def _bind_command(self, ctx, name : str):
        if self.bot.settings["debug"]["soundboard"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][_bind_command]{ctx.author.name} requested normal command')

        await self._bind(ctx, name)

    #slash command
    @cog_ext.cog_slash(name="playbind", 
        description="Odtwarza binda", 
        options=[
            create_option(
                name="nazwa", 
                description="Podaj nazwę binda", 
                option_type=3, 
                required=True
            )
        ]
    )
    async def _bind_slash(self, ctx:SlashContext, nazwa : str):
        if self.bot.settings["debug"]["soundboard"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][_bind_slash]{ctx.author.name} requested slash command')

        await self._bind(ctx, nazwa)


    async def _bindList(self, ctx):
        list = self.bot.settings["audio"]['binds'] #take all the available binds
        list = sorted(list, key=str.lower) #sort list alphabetically

        i = 0 #field counter
        j = 1 #messages counter

        color = random.randint(0, 0xffffff) #random color

        #create new embed
        embed=discord.Embed() 
        embed.colour = color
        embed.title = "Dostępne bindy: (1/" + str(math.ceil(len(list)/25)) + ")" #set title
        embed.description="'yo playbind [nazwa_binda]'" #set dsc
        embed.timestamp = datetime.datetime.utcnow() #timestamp
        
        for val in list:

            #new message
            if(i == 25):
                #send embed
                if self.bot.settings["setting"]["soundboard"]["send_bindlist_in_dm"]:  
                    await ctx.author.send(embed=embed) #dm
                else:
                    if isinstance(ctx, SlashContext): #slash command
                        await ctx.send(embed=embed, hidden=True)
                    else: #normal command
                        await ctx.reply(embed=embed)
                    

                j += 1 #add to message counter

                #create new embed
                embed=discord.Embed() 
                embed.colour = color
                embed.title = "Dostępne bindy: (" + str(j) + "/" + str(math.ceil(len(list)/25)) + ")" #set title
                embed.timestamp = datetime.datetime.utcnow() #timestamp

                i = 0 #reset line counter


            embed.add_field(name=str(val)[0:-4], value="`yo playbind " + str(val)[0:-4] + "`", inline=True) #add field without .mp3
            i += 1 #add to line counter

        if self.bot.settings["setting"]["soundboard"]["send_bindlist_in_dm"]:   
            await ctx.author.send(embed=embed) #send last message in dm
            if isinstance(ctx, SlashContext): #slash command
                await ctx.send("Wysłałem DM z listą bindów do " + str(ctx.author.mention), hidden=True)
            else: #normal command
                await ctx.reply("Wysłałem DM z listą bindów do " + str(ctx.author.mention), delete_after=5)

            if self.bot.settings["debug"]["soundboard"]:
                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][_bindList]Sent bindlist in DM to {ctx.author.name}\n')

        else:
            if isinstance(ctx, SlashContext): #slash command
                await ctx.send(embed=embed, hidden=True)
            else: #normal command
                await ctx.reply(embed=embed)

            if self.bot.settings["debug"]["soundboard"]:
                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][_bindList]Sent bindlist to text channel\n')
    
    #normal command
    @commands.command(name = 'bindlist',
        aliases = ['bindy', 'listabindów', 'listbind', 'bindslist', 'listbinds'], 
        brief = "Wyświetla listę dostępnych bindów", 
        help = "Wysyła listę dostępnych bindów w wiadomości prywatnej", 
        usage = "yo bindlist"
    )
    async def _bindList_command(self, ctx):
        if self.bot.settings["debug"]["soundboard"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][_bindList_command]{ctx.author.name} requested normal command')

        await self._bindList(ctx)

    #slash command
    @cog_ext.cog_slash(name="bindlist", 
        description="Wyświetla listę dostępnych bindów"
    )
    async def _bindList_slash(self, ctx:SlashContext):
        if self.bot.settings["debug"]["soundboard"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][_bindList_slash]{ctx.author.name} requested slash command')

        await self._bindList(ctx)

    
    async def Join(self, ctx):
        user_vc:discord.Member=ctx.author.voice.channel #get user's vc

        same_channel = False

        if user_vc != None: #user has to be in the vc
            if(self.bot.voice_clients != []): #if bot is on any server's vc
                for vc in self.bot.voice_clients: #cycle through all servers
                    if(vc.channel == user_vc): #bot is already on the same vc
                        same_channel = True

                        if self.bot.settings["debug"]["soundboard"]:
                            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][Join]Bot is in the same vc')

                        return vc #return current channel

                if same_channel == False: #User isn't on the same vc
                    for vc in self.bot.voice_clients: #cycle through all servers
                        if vc.guild == user_vc.guild: #bot is on the same guild, but on other channel

                            if self.bot.settings["debug"]["soundboard"]:
                                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][Join]Bot joined vc (bot was on the other channel)')

                            await vc.disconnect() #disconnect from old channel

                            return await user_vc.connect() #join user channel
                    
                    #bot isn't connected to any of the server's vc
                    if self.bot.settings["debug"]["soundboard"]:
                        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][Join]Bot joined vc (bot wasnt connected)')

                    return await user_vc.connect() #connect to the requested channel
                

    async def PlaySound(self, vc : discord.VoiceChannel, voiceline):
        if vc.is_playing() == True:
            vc.stop() #stop playing

        vc.play(discord.FFmpegPCMAudio(self.bot.settings['audioPath'] + voiceline), after=lambda e: print('Player error: %s' % e) if e else (print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][PlaySound]Played bind on {vc.channel.name}\n') if self.bot.settings["debug"]["soundboard"] else None)) #play sound on vc


def setup(bot):
    bot.add_cog(Soundboard(bot))