import discord
from discord.ext import commands
import json
import datetime
from discord_slash import cog_ext, SlashContext, ComponentContext
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component
from discord_slash.model import ButtonStyle

class GlobalCounter(commands.Cog):
    """Globalny licznik"""
    def __init__(self, bot):
        self.bot = bot

        if self.bot.settings["debug"]["global_counter"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][global_counter]Loaded")


    async def IncreaseNumber(self):
        #add to counter
        self.bot.data["counter"] += int(self.bot.settings["setting"]["global_counter"]["add_value"])

        #update json
        with open('data.json', 'w') as outfile:
            json.dump(self.bot.data, outfile, indent=4)

        if self.bot.settings["debug"]["global_counter"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][global_counter][IncreaseNumber]Added {self.bot.settings["setting"]["global_counter"]["add_value"]} to global counter value, now it equals: {self.bot.data["counter"]}')


    #add digit to global counter
    async def _add(self, ctx):
        #increase number
        await self.IncreaseNumber() 

        #add button
        buttons = [
            create_button(
                style=ButtonStyle.success,
                label="Dodaj kolejny",
                custom_id="add_next",
            ),
        ]
        action_row = create_actionrow(*buttons)

        #send outcome
        if isinstance(ctx, SlashContext): #slash command
            await ctx.send(f'Licznik wynosi: `{self.bot.data["counter"]}`', components=[action_row])
        else: #normal command
            await ctx.reply(f'Licznik wynosi: `{self.bot.data["counter"]}`', components=[action_row])

        if self.bot.settings["debug"]["global_counter"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][global_counter][_add]Created add message\n')

    #normal command
    @commands.command(name = 'dodaj',
        aliases = ['add', '+', 'licznik', 'counter'], 
        brief = "Dodaj punkt do globalnego licznika", 
        help = "Dodaj punkt do globalnego licznika tego bota", 
        usage = "yo dodaj"
    )
    async def _add_command(self, ctx):
        if self.bot.settings["debug"]["global_counter"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][global_counter][_add_command]{ctx.author.name} requested normal command')

        await self._add(ctx)

    #slash command
    @cog_ext.cog_slash(name="dodaj", 
        description="Dodaj punkt do globalnego licznika"
    )
    async def _add_slash(self, ctx:SlashContext):
        if self.bot.settings["debug"]["global_counter"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][global_counter][_add_slash]{ctx.author.name} requested slash command')

        await self._add(ctx)


    #on button press
    @cog_ext.cog_component()
    async def add_next(self, ctx: ComponentContext):
        await self.IncreaseNumber() #increase number    

        await ctx.edit_origin(content=f'Licznik wynosi: `{self.bot.data["counter"]}`') #edit message

        if self.bot.settings["debug"]["global_counter"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][global_counter][_add]Pressed button on add message\n')


def setup(bot):
    bot.add_cog(GlobalCounter(bot))