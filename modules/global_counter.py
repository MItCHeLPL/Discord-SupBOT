import discord
from discord.ext import commands
import json

class GlobalCounter(commands.Cog):
    """Globalny licznik"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'add', aliases = ['dodaj', '+', 'licznik', 'counter'])
    async def _add(self, ctx):
        """Dodaj do globalnego licznika"""
        with open('global_counter.json') as file: #read json file
            counter = int(json.loads(file)['counter']) #get current value

        counter += 1 #add one to current value

        #prepare json scheme with current counter value
        data = {
            "counter": counter,
        }

        #save json
        with open('global_counter.json', 'w') as outfile:
            json.dump(data, outfile)

        await ctx.reply(f'Licznik wynosi: `{counter}`')


def setup(bot):
    bot.add_cog(GlobalCounter(bot))