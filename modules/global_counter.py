import discord
from discord.ext import commands
import json

class GlobalCounter(commands.Cog):
    """Globalny licznik"""
    def __init__(self, bot):
        self.bot = bot

        if self.bot.data["debug"]["global_counter"]:
            print(f"[global_counter]Loaded")

    @commands.command(name = 'add', aliases = ['dodaj', '+', 'licznik', 'counter'])
    async def _add(self, ctx):
        """Dodaj do globalnego licznika"""

        with open('global_counter.json', 'r+') as file: #read json file
            counter_data = json.load(file) #get current value 

        counter = int(counter_data["counter"])

        counter += int(self.bot.data["setting"]["global_counter"]["add_value"]) #add to current value

        #prepare json scheme with current counter value
        data = {
            "counter": counter,
        }

        #save json
        with open('global_counter.json', 'w') as outfile:
            json.dump(data, outfile)

        await ctx.reply(f'Licznik wynosi: `{counter}`')

        if self.bot.data["debug"]["global_counter"]:
            print(f'[global_counter][_add]Added {self.bot.data["setting"]["global_counter"]["add_value"]} to global counter value, now it equals: {counter} \n')


def setup(bot):
    bot.add_cog(GlobalCounter(bot))