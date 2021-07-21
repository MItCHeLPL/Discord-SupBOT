import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
import datetime

load_dotenv()

class Other(commands.Cog):
    """Inne"""
    def __init__(self, bot):
        self.bot = bot
        
        self.user_id_szary = os.getenv('DISCORD_ID_SZARY')

    @commands.command(name = 'sup')
    async def _sup(self, ctx):
        """Pytasz bota co tam u niego."""
        await ctx.reply("nm u?")

    @commands.command(name = 'nm')
    async def _nm(self, ctx):
        """Reakcja bota na to że nic ciekawego się u ciebie nie dzieje."""
        await ctx.reply("cool.")

    @commands.command(name = 'wiek')
    async def _wiek(self, ctx, wiek:int):
        """Czy możesz rzucać kartę dla takiego wieku? (yo wiek [liczba])"""
        wynik = (wiek/2) + 7
        await ctx.reply("Yo, `" + str(wynik) + "` i rzucasz kartę byniu.")

    @commands.command(name = 'pogoda', aliases=['burza', 'weather', 'piorun', 'mapa', 'map', 'blitz', 'lightning', 'lighting', 'lightingmap', 'lightningmap', 'thunder'])
    async def _weathermap(self, ctx):
        """Wyświetla mapę burz"""
        embed=discord.Embed() #create new embed
        embed.colour = random.randint(0, 0xffffff) #random color
        embed.set_image(url=f"http://images.blitzortung.org/Images/image_b_pl.png?mapId={int(datetime.now().timestamp() * 1000)}") #set image
        embed.title = "Aktualna mapa burzowa w Polsce" #set title
        embed.url= "https://www.blitzortung.org/pl/live_lightning_maps.php?map=17"

        embed.timestamp = datetime.datetime.utcnow() #set time

        await ctx.reply(embed=embed)

    #send dm to user
    @commands.command(name = 'dmuser', aliases=['dm', 'pm', 'priv'])
    async def _dmuser(self, ctx, user : discord.Member, text : str, *args):
        """Wysyła dm do użytkownika (yo dmuser [@użytkownik] [tekst])"""
        #get text after space
        spaceText = ""
        for txt in args:
            spaceText += (" " + str(txt))

        await user.send('\nYo,\n' + text + spaceText)
        await ctx.reply("Yo, wysłano dm do " + str(user.mention) + ".", delete_after=10)

    @commands.command(name = 'dmszary', aliases=['szary', 'pmszary', 'privszary'])
    async def _dmszary(self, ctx, text : str, *args):
        """Wysyła dm do Szarego (yo dmszary [tekst])"""
        user = self.bot.get_user(self.user_id_szary) #Szary ID
        if(user != None):
            await self._dmuser(ctx, user, text)

    #picks random person from voicechannel you are in
    @commands.command(name = 'impostor', aliases=['imposter', 'amogus', 'amongus', 'sus'])
    async def _impostor(self, ctx):
        """Kto z kanału głosowego jest impostorem"""
        channel = discord.utils.get(ctx.guild.voice_channels,  name=ctx.message.author.voice.channel.name) #get voice channel that caller is in

        member_ids = list(channel.voice_states.keys()) #list of user ids

        pickedUserId = random.randint(0, len(member_ids)-1) #random user from list

        user = await self.bot.fetch_user(member_ids[pickedUserId]) #id to user
        
        await ctx.reply("Yo, " + str(user.mention) + " jest impostorem.")
    
def setup(bot):
    bot.add_cog(Other(bot))