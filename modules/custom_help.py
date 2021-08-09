import discord
from discord.ext import commands
from pretty_help import DefaultMenu, PrettyHelp
from discord_slash import cog_ext, SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component
from discord_slash.model import ButtonStyle
import difflib
import datetime
import random

class CustomHelp(commands.Cog):
    """Pomoc"""

    def __init__(self, bot):
        self.bot = bot

        self.commands_names_and_aliases = [] #list of names and aliases of all normal commands

        self.bot.remove_command('help') #remove default help command

        #Preety help menu configuration
        menu = DefaultMenu(page_left="⬅️", page_right="➡️", remove="✖️", active_time=None) #message settings

        ending_note = f"Wpisz `yo help [komenda]` aby zobaczyć szczegóły dotyczące danej komendy"

        #Preety help command configuration
        self.bot.help_command = PrettyHelp(menu=menu, ending_note=ending_note, index_title="Kategorie", no_category="Bez kategorii", show_index=True, dm_help=self.bot.settings["setting"]["custom_help"]["send_help_in_dm"]) #help command settings

        if self.bot.settings["debug"]["custom_help"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][custom_help]Loaded")

    @commands.Cog.listener()
    async def on_ready(self):
        #Generate list of all normal commands names and aliases combined
        for command in self.bot.commands:
            self.commands_names_and_aliases.append(str(command.name)) #append name

            for alias in command.aliases:
                self.commands_names_and_aliases.append(str(alias)) #append alias


    #info about specific command
    async def _help(self, ctx:SlashContext, command:str):
        try:
            found_command = self.bot.get_command(command) #command

            #embed
            embed=discord.Embed()

            embed.title = "🛈 Informacje o komendzie:" #set title
            embed.description = f"`{found_command.name}`" #command name
            embed.colour = random.randint(0, 0xffffff) #random color

            #embed fields
            embed.add_field(name="Aliasy", value=str(found_command.aliases)[1:-1].replace("'", "`"), inline=False)
            embed.add_field(name="Kategoria", value=f"`{found_command.cog_name}`", inline=False)
            embed.add_field(name="Opis", value=f"`{found_command.brief}`", inline=False)
            embed.add_field(name="Opis szczegółowy", value=f"`{found_command.help}`", inline=False)
            embed.add_field(name="Użycie", value=f"`{found_command.usage}`", inline=False)

            embed.timestamp = datetime.datetime.utcnow() #timestamp

            embed.set_footer(text=f"/help {found_command.name}") #footer

            await ctx.send(embed=embed, hidden=True) #send embed

            if self.bot.settings["debug"]["custom_help"]:
                print(f"[{str(datetime.datetime.utcnow())[0:-7]}][custom_help][_help_slash]Found command {found_command.name} and posted help\n")

        except:
            #find close matches in command names and aliases
            close_matches = difflib.get_close_matches(command, self.commands_names_and_aliases, 5, 0.5)

            if len(close_matches) > 0: #if found matches
                #create button for each match
                buttons = []

                for match in close_matches:
                    buttons.append(create_button(style=ButtonStyle.primary, label=str(f"Informacje o '{match}'"), custom_id=match),)

                action_row = create_actionrow(*buttons)

                await ctx.send(f"Nie znaleziono komendy `{command}`\n➤Czy chodziło ci o: `{str(close_matches)[1:-1]}`", components=[action_row], hidden=True) #send message with button to call slash command

                #wait for button press
                while True:
                    button_ctx: ComponentContext = await wait_for_component(self.bot, components=action_row)
                    if button_ctx.component_type == 2 and button_ctx.custom_id in close_matches: #check if button and button correspond to match
                        await self._help(ctx, button_ctx.custom_id) #call help for this match

            else: #if didn't find matches
                await ctx.send(f"Nie znaleziono komendy `{command}`", hidden=True)

            if self.bot.settings["debug"]["custom_help"]:
                print(f"[{str(datetime.datetime.utcnow())[0:-7]}][custom_help][_help_slash]Didn't find command {command}, closest commands: {close_matches}\n")
    
    #slash command
    @cog_ext.cog_slash(name="help", 
        description="Wyświetla pomoc", 
        options=[
            create_option(
                name="command", 
                description="Podaj nazwę komendy", 
                option_type=3, 
                required=True
            )
        ]
    )
    async def _help_slash(self, ctx:SlashContext, command:str):
        if self.bot.settings["debug"]["custom_help"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][custom_help][_help_slash]{ctx.author.name} requested slash command')

        await self._help(ctx, command)


def setup(bot):
    bot.add_cog(CustomHelp(bot))