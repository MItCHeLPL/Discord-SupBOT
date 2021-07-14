import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random

load_dotenv()

class Other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'sup')
    async def _sup(self, ctx):
        await ctx.reply("nm u?")

    @commands.command(name = 'nm')
    async def _nm(self, ctx):
        await ctx.reply("cool.")

    @commands.command(name = 'wiek')
    async def _wiek(self, ctx, wiek:int):
        wynik = (wiek/2) + 7
        await ctx.reply("Yo, " + str(wynik) + " i rzucasz kartę byniu.")

    #send dm to user
    @commands.command(name = 'dmuser', aliases=['dm', 'pm', 'priv'])
    async def _dmuser(self, ctx, user : discord.Member, text : str, *args):
        #get text after space
        spaceText = ""
        for txt in args:
            spaceText += (" " + str(txt))

        await user.send('\nYo,\n' + text + spaceText)
        await ctx.reply("Yo, wysłano dm do " + str(user.mention) + ".", delete_after=10)

    @commands.command(name = 'dmszary', aliases=['szary', 'pmszary', 'privszary'])
    async def _dmszary(self, ctx, text : str, *args):
        user = self.bot.get_user(os.getenv('DISCORD_ID_SZARY')) #Szary ID
        if(user != None):
            await self._dmuser(ctx, user, text)

    #picks random person from voicechannel you are in
    @commands.command(name = 'impostor', aliases=['imposter', 'amogus', 'amongus'])
    async def _impostor(self, ctx):
        channel = discord.utils.get(ctx.guild.voice_channels,  name=ctx.message.author.voice.channel.name) #get voice channel that caller is in

        member_ids = list(channel.voice_states.keys()) #list of user ids

        pickedUserId = random.randint(0, len(member_ids)-1) #random user from list

        user = await self.bot.fetch_user(member_ids[pickedUserId]) #id to user
        
        await ctx.reply("Yo, " + str(user.mention) + " jest impostorem.")
    
def setup(bot):
    bot.add_cog(Other(bot))