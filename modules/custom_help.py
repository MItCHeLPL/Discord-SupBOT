import discord
from discord.ext import commands
from pretty_help import DefaultMenu, PrettyHelp

class CustomHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        #self.bot.remove_command('help') #remove default help command

        #Preety help menu configuration
        menu = DefaultMenu(page_left="⬅️", page_right="➡️", remove="✖️", active_time=45)

        #Preety help command configuration
        self.bot.help_command = PrettyHelp(menu=menu, index_title="Kategorie", no_category="Bez kategorii", show_index=True)


def setup(bot):
    bot.add_cog(CustomHelp(bot))