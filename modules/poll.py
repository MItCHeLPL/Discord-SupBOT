import discord
from discord.ext import commands
import random

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ankieta', aliases=['poll', 'glosowanie', 'głosowanie'])
    async def _poll(self, ctx, option1 : str, *args):

        emojis = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']

        #create options tables
        options = []
        options.append(option1)

        #set text after space to options
        for option in args:
            options.append(str(option))

        embed=discord.Embed() #create new embed
        embed.colour = random.randint(0, 0xffffff) #random color
        embed.title = "Ankieta" #set title

        i = 0 #option id
        for option in options:
            if i<10:
                embed.add_field(name=str(i), value=str(option), inline=False) #add option field
                i += 1
            else:
                break

        msg = await ctx.send(embed=embed) #post poll

        #react with voting emojis
        for emoji in emojis:
            if i > 0: 
                await msg.add_reaction(emoji)
                i -= 1

def setup(bot):
    bot.add_cog(Poll(bot))