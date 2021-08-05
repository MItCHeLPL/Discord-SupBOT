import discord
from discord.ext import commands
import json
import datetime

class GlobalCounter(commands.Cog):
    """Globalny licznik"""
    def __init__(self, bot):
        self.bot = bot

        if self.bot.settings["debug"]["global_counter"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][global_counter]Loaded")


    @commands.command(name = 'add', aliases = ['dodaj', '+', 'licznik', 'counter'])
    async def _add(self, ctx):
        """Dodaj do globalnego licznika"""

        #add to counter
        self.bot.data["counter"] += 1

        #update json
        with open('data.json', 'w') as outfile:
            json.dump(self.bot.data, outfile)

        await ctx.reply(f'Licznik wynosi: `{self.bot.data["counter"]}`') #send outcome

        if self.bot.settings["debug"]["global_counter"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][global_counter][_add]Added {self.bot.settings["setting"]["global_counter"]["add_value"]} to global counter value, now it equals: {self.bot.data["counter"]} \n')


def setup(bot):
    bot.add_cog(GlobalCounter(bot))