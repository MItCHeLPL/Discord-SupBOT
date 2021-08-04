import discord
from discord.ext import commands
import datetime
import random
import math
import datetime

class Soundboard(commands.Cog):
    """Bindy"""
    def __init__(self, bot):
        self.bot = bot

        if self.bot.data["debug"]["soundboard"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][soundboard]Loaded")
    

    @commands.command(name = 'playbind', aliases = ['bind', 'soundboard', 'pb', 'ps', 'sound', 'playsound'])
    async def _bind(self, ctx, name : str):
        """Odtwarza binda (yo playbind [nazwa]) 
        Lista bindów dostępna używając: (yo bindlist)"""
        voiceline = name + '.mp3'

        if voiceline in self.bot.data["audio"]['binds']:
            vc = await self.Join(ctx) #join vc

            await self.PlaySound(vc, voiceline) #play tts

            await ctx.reply('Odtwarzam binda `' + name + '`', delete_after=5)

            if self.bot.data["debug"]["soundboard"]:
                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][_bind]Playing bind: {name}\n')

            return True

        else:
            await ctx.reply('Nie znaleziono binda `' + name + '`', delete_after=5)

            if self.bot.data["debug"]["soundboard"]:
                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][_bind]Sound not found\n')

            return False


    @commands.command(name = 'bindlist', aliases = ['bindy', 'listabindów', 'listbind', 'bindslist', 'listbinds'])
    async def _bindList(self, ctx):
        """Wyświetla listę dostępnych bindów"""
        list = self.bot.data["audio"]['binds'] #take all the available binds
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
                if self.bot.data["setting"]["soundboard"]["send_bindlist_in_dm"]:  
                    await ctx.author.send(embed=embed) #dm
                else:
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

        if self.bot.data["setting"]["soundboard"]["send_bindlist_in_dm"]:   
            await ctx.author.send(embed=embed) #send last message in dm
            await ctx.reply("Wysłałem DM z listą bindów do " + str(ctx.author.mention), delete_after=5)

            if self.bot.data["debug"]["soundboard"]:
                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][_bindList]Sent bindlist in DM to {ctx.author.name}\n')

        else:
            await ctx.reply(embed=embed)

            if self.bot.data["debug"]["soundboard"]:
                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][_bindList]Sent bindlist to text channel\n')

    
    async def Join(self, ctx):
        user_vc=ctx.message.author.voice.channel #get user's vc

        same_channel = False

        if user_vc != None: #user has to be in the vc
            if(self.bot.voice_clients != []): #if bot is on any server's vc
                for vc in self.bot.voice_clients: #cycle through all servers
                    if(vc.channel == user_vc): #bot is already on the same vc
                        same_channel = True

                        if self.bot.data["debug"]["soundboard"]:
                            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][Join]Bot is in the same vc')

                        return vc #return current channel

                if same_channel == False: #User is on the same server's vc, but not the same channel
                    #await ctx.reply("Dołączam na kanał `" + str(voice_channel.name) + "`", delete_after=5)

                    if self.bot.data["debug"]["soundboard"]:
                        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][Join]Bot joined vc (bot was on the other channel)')

                    await vc.disconnect() #disconnect from old channel

                    return await user_vc.connect() #join user channel
                    
            else:
                #await ctx.reply("Dołączam na kanał `" + str(voice_channel.name) + "`", delete_after=5)

                if self.bot.data["debug"]["soundboard"]:
                    print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][Join]Bot joined vc (bot wasnt connected)')

                return await user_vc.connect() #connect to the requested channel, bot isn't connected to any of the server's vc
                

    async def PlaySound(self, vc : discord.VoiceChannel, voiceline):
        if vc.is_playing() == True:
            vc.stop() #stop playing

        vc.play(discord.FFmpegPCMAudio(self.bot.data['audioPath'] + voiceline), after=lambda e: print('Player error: %s' % e) if e else (print(f'[{str(datetime.datetime.utcnow())[0:-7]}][soundboard][PlaySound]Played bind on {vc.channel.name}') if self.bot.data["debug"]["soundboard"] else None)) #play sound on vc


def setup(bot):
    bot.add_cog(Soundboard(bot))