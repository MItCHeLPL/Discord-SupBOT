import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
import datetime
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

load_dotenv()

class Other(commands.Cog):
    """Inne"""
    def __init__(self, bot):
        self.bot = bot

        if self.bot.settings["debug"]["other"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][other]Loaded")

    @commands.Cog.listener()
    async def on_ready(self):
        self.user_szary_id = int(os.getenv('DISCORD_ID_SZARY')) #save Szary's id


    #meme/inside joke functionality
    async def _sup(self, ctx):
        if isinstance(ctx, SlashContext): #slash command
            await ctx.send("nm u?")
        else: #normal command
            await ctx.reply("nm u?")

        if self.bot.settings["debug"]["other"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_sup]sup\n')

    #normal command
    @commands.command(name = 'sup', 
        help="Pytasz bota co tam u niego.", 
        brief="Pytasz bota co tam u niego.")
    async def _sup_command(self, ctx):
        if self.bot.settings["debug"]["other"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_sup_command]{ctx.author.name} requested normal command')

        await self._sup(ctx)

    #slash command
    #@cog_ext.cog_slash(name="sup", 
    #    description="Pytasz bota co tam u niego.")
    #async def _sup_slash(self, ctx:SlashContext):
    #    if self.bot.settings["debug"]["other"]:
    #        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_sup_slash]{ctx.author.name} requested slash command')
    #
    #    await self._sup(ctx)


    #meme/inside joke functionality
    async def _nm(self, ctx):
        if isinstance(ctx, SlashContext): #slash command
            await ctx.send("cool.")
        else: #normal command
            await ctx.reply("cool.")

        if self.bot.settings["debug"]["other"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_nm]nm\n')
            
    #normal command
    @commands.command(name = 'nm', 
        help="Reakcja bota na to że nic ciekawego się u ciebie nie dzieje.", 
        brief="Reakcja bota na to że nic ciekawego się u ciebie nie dzieje.")
    async def _nm_command(self, ctx):
        if self.bot.settings["debug"]["other"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_nm_command]{ctx.author.name} requested normal command')

        await self._nm(ctx)

    #slash command
    #@cog_ext.cog_slash(name="nm", 
    #    description="Reakcja bota na to że nic ciekawego się u ciebie nie dzieje.")
    #async def _nm_slash(self, ctx:SlashContext):
        #if self.bot.settings["debug"]["other"]:
            #print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_nm_slash]{ctx.author.name} requested slash command')
    #
    #    await self._nm(ctx)


    #meme/inside joke functionality
    async def _wiek(self, ctx, wiek:int):
        wynik = (wiek/2) + 7

        if isinstance(ctx, SlashContext): #slash command
            await ctx.send("Yo, `" + str(wynik) + "` i rzucasz kartę.")
        else: #normal command
            await ctx.reply("Yo, `" + str(wynik) + "` i rzucasz kartę.")

        if self.bot.settings["debug"]["other"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_wiek]wiek: {str(wynik)}\n')
    
    #normal command
    @commands.command(name = 'wiek', 
        help="Czy możesz robić ruchy dla takiego wieku? (yo wiek [liczba])", 
        brief="Czy możesz robić ruchy dla takiego wieku? (yo wiek [liczba])")
    async def _wiek_command(self, ctx, wiek:int):
        if self.bot.settings["debug"]["other"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_wiek_command]{ctx.author.name} requested normal command')

        await self._wiek(ctx, wiek)

    #slash command
    @cog_ext.cog_slash(name="wiek", 
        description="Czy możesz robić ruchy dla takiego wieku?", 
        options=[
            create_option(
                name="wiek", 
                description="Podaj wiek", 
                option_type=4, 
                required=True)], 
        guild_ids=[int(os.getenv('DISCORD_ID_BOBERSCHLESIEN')), int(os.getenv('DISCORD_ID_SCAMELOT'))])
    async def _wiek_slash(self, ctx:SlashContext, wiek:int):
        if self.bot.settings["debug"]["other"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_wiek_slash]{ctx.author.name} requested slash command')

        await self._wiek(ctx, wiek)


    #shows lighting map for poland
    async def _weathermap(self, ctx):
        embed=discord.Embed() #create new embed
        embed.colour = random.randint(0, 0xffffff) #random color
        embed.set_image(url=f"http://images.blitzortung.org/Images/image_b_pl.png") #set image
        embed.title = "Aktualna mapa burzowa w Polsce" #set title
        embed.url= "https://www.blitzortung.org/pl/live_lightning_maps.php?map=17"

        embed.timestamp = datetime.datetime.utcnow() #set timestamp

        if isinstance(ctx, SlashContext): #slash command
            await ctx.send(embed=embed)
        else: #normal command
            await ctx.reply(embed=embed)

        if self.bot.settings["debug"]["other"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_weathermap]Posted weather map\n')

    #normal command
    @commands.command(name = 'burza', 
        aliases=['pogoda', 'weather', 'piorun', 'mapa', 'map', 'blitz', 'lightning', 'lighting', 'lightingmap', 'lightningmap', 'thunder'],
        help="Wyświetla mapę burz dla polski", 
        brief="Wyświetla mapę burz dla polski")
    async def _weathermap_command(self, ctx):
        if self.bot.settings["debug"]["other"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_weathermap_command]{ctx.author.name} requested normal command')

        await self._weathermap(ctx)

    #slash command
    @cog_ext.cog_slash(name="burza", 
        description="Wyświetla mapę burz dla polski")
    async def _weathermap_slash(self, ctx:SlashContext):
        if self.bot.settings["debug"]["other"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_weathermap_slash]{ctx.author.name} requested slash command')

        await self._weathermap(ctx)


    #send dm to Szary (meme/inside joke functionality)
    async def _dmszary(self, ctx, text : str):
        if self.bot.settings["setting"]["other"]["enable_dmszary"]:  
            user_szary = discord.utils.get(ctx.guild.members, id=self.user_szary_id) #get szary's user

            if(user_szary != None):
                await user_szary.send('\nYo,\n' + text) #send text

                if isinstance(ctx, SlashContext): #slash command
                    await ctx.send("Wysłano dm do szarego", hidden=True)
                else: #normal command
                    await ctx.reply("Wysłano dm do szarego", delete_after=10)

                if self.bot.settings["debug"]["other"]:
                    print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_dmszary]Sent DM to szary, text: {text}\n')

    #normal command
    @commands.command(name = 'dmszary', 
        aliases=['szary', 'pmszary', 'privszary'],
        help="Wysyła dm do Szarego (yo dmszary [tekst])", 
        brief="Wysyła dm do Szarego (yo dmszary [tekst])")
    async def _dmszary_command(self, ctx, text : str, *args):
        #combine text into one string
        spaceText = ""
        for txt in args:
            spaceText += (" " + str(txt))
        text += spaceText

        if self.bot.settings["debug"]["other"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_dmszary_command]{ctx.author.name} requested normal command')

        await self._dmszary(ctx, text)

    #slash command
    @cog_ext.cog_slash(name="dmszary", 
        description="Wysyła dm do Szarego", 
        options=[
            create_option(
                name="text", 
                description="Podaj tekst wiadomości", 
                option_type=3, 
                required=True)], 
        guild_ids=[int(os.getenv('DISCORD_ID_BOBERSCHLESIEN')), int(os.getenv('DISCORD_ID_SCAMELOT'))])
    async def _dmszary_slash(self, ctx:SlashContext, text : str):
        if self.bot.settings["debug"]["other"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_dmszary_slash]{ctx.author.name} requested slash command')

        await self._dmszary(ctx, text)


    #picks random person from voicechannel you are in, and calls it and "impostor"
    async def _impostor(self, ctx):
        channel = discord.utils.get(ctx.guild.voice_channels, name=ctx.author.voice.channel.name) #get voice channel that you are is in

        if(channel != None):
            member_ids = list(channel.voice_states.keys()) #list of user ids

            pickedUserId = random.randint(0, len(member_ids)-1) #random user from list

            user = await self.bot.fetch_user(member_ids[pickedUserId]) #id to user
            
            if isinstance(ctx, SlashContext): #slash command
                await ctx.send("Yo, " + str(user.mention) + " jest impostorem.")
            else: #normal command
                await ctx.reply("Yo, " + str(user.mention) + " jest impostorem.")

            if self.bot.settings["debug"]["other"]:
                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_impostor]Requested impostor, outcome: {user.name}\n')

        else:
            if isinstance(ctx, SlashContext): #slash command
                await ctx.send("Nie znaleziono kanału, na którym jesteś", hidden=True)
            else: #normal command
                await ctx.reply("Nie znaleziono kanału, na którym jesteś", delete_after=5)
            
            if self.bot.settings["debug"]["other"]:
                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_impostor]Requested impostor, bot didnt find users channel\n')
    
    #normal command
    @commands.command(name = 'impostor', 
        aliases=['imposter', 'amogus', 'amongus', 'sus'],
        help="Kto z kanału głosowego jest impostorem", 
        brief="Kto z kanału głosowego jest impostorem")
    async def _impostor_command(self, ctx):
        if self.bot.settings["debug"]["other"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_impostor_command]{ctx.author.name} requested normal command')

        await self._impostor(ctx)

    #slash command
    @cog_ext.cog_slash(name="impostor", 
        description="Kto z kanału głosowego jest impostorem")
    async def _impostor_slash(self, ctx:SlashContext):
        if self.bot.settings["debug"]["other"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][other][_impostor_slash]{ctx.author.name} requested slash command')

        await self._impostor(ctx)
    

def setup(bot):
    bot.add_cog(Other(bot))