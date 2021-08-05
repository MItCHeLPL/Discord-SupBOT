import discord
from discord.ext import commands
from pretty_help import DefaultMenu, PrettyHelp
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

class CustomHelp(commands.Cog):
    """Pomoc"""
    def __init__(self, bot):
        self.bot = bot

        self.bot.remove_command('help') #remove default help command

        #Preety help menu configuration
        menu = DefaultMenu(page_left="⬅️", page_right="➡️", remove="✖️", active_time=None) #message settings

        ending_note = f"Wpisz `yo help [komenda]` aby zobaczyć szczegóły dotyczące danej komendy"

        #Preety help command configuration
        self.bot.help_command = PrettyHelp(menu=menu, ending_note=ending_note, index_title="Kategorie", no_category="Bez kategorii", show_index=True, dm_help=self.bot.settings["setting"]["custom_help"]["send_help_in_dm"]) #help command settings


    #slash command
    #@cog_ext.cog_slash(name="help", 
    #    description="Wyświetla pomoc", 
    #    options=[
    #        create_option(
    #            name="command", 
    #            description="Podaj nazwę komendy", 
    #            option_type=3, 
    #            required=False)])
    #async def _help_slash(self, ctx:SlashContext, command):
    #    return #temp


def setup(bot):
    bot.add_cog(CustomHelp(bot))