import discord
from discord.ext import commands
import datetime
import random
import math

class Soundboard(commands.Cog):
    """Bindy"""
    def __init__(self, bot):
        self.bot = bot
    

    @commands.command(name = 'playbind', aliases = ['bind', 'soundboard', 'pb', 'ps', 'sound', 'playsound'])
    async def _bind(self, ctx, name : str):
        """Odtwarza binda (yo playbind [nazwa]) 
        Lista bindów dostępna używając: (yo bindlist)"""
        voiceline = name + '.mp3'

        if voiceline in self.bot.data['binds']:
            vc = await self.Join(ctx) #join vc

            await self.PlaySound(ctx, vc, voiceline) #play tts

            ctx.reply('Odtwarzam binda `' + name + '`', delete_after=5)
            return True

        else:
            ctx.reply('Nie znaleziono binda `' + name + '`', delete_after=5)
            return False


    @commands.command(name = 'bindlist', aliases = ['bindy', 'listabindów', 'listbind', 'bindslist', 'listbinds'])
    async def _bindList(self, ctx):
        """Wyświetla listę dostępnych bindów"""
        list = self.bot.data['binds'] #take all the available binds
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
        else:
            await ctx.reply(embed=embed)

    
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
                    return await voice_channel.connect()
                    await ctx.reply("Dołączam na kanał `" + str(voice_channel.name) + "`", delete_after=5)

            else:
                return await voice_channel.connect() #connect to the requested channel, bot isn't connected to any of the server's vc
                await ctx.reply("Dołączam na kanał `" + str(voice_channel.name) + "`", delete_after=5)


    def PlaySound(self, channel : discord.VoiceChannel, voiceline):
        for server in self.bot.voice_clients: #cycle through all servers
            if(server.channel == channel): #find current voice channel
                vc = server #get voice channel

                if vc.is_playing() == False: #if not saying something
                        vc.play(discord.FFmpegPCMAudio(self.bot.data['audioPath'] + voiceline), after=lambda e: print('Player error: %s' % e) if e else None) #play sound on vc

                break 

def setup(bot):
    bot.add_cog(Soundboard(bot))