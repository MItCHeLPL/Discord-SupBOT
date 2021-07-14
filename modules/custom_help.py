import discord
from discord.ext import commands

class CustomHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.bot.remove_command('help') #remove default help command

    # custom help command
    @commands.command(name='help', aliases = ['pomoc', '?'])
    async def _help(self, ctx, command = None):
        if command == None:
            helpEmbed = self.generateHelp(self.bot.commands) #if no command passed show all commands
        else:
            for botCommand in self.bot.commands:
                if str(botCommand) == command or command in botCommand.aliases:
                    if isinstance(botCommand, commands.Group):
                        helpEmbed = self.generateHelp(botCommand.commands) #if passed command exists, show help about this command
                        break
                    else:
                        pass
                else:
                    pass

        await ctx.reply(embed = helpEmbed) #reply with help message


    def generateHelp(self, commandsArray):
    helpText = '**Komendy:**\n\n'
    for command in commandsArray:
        helpText += f'''{command} {command.signature}{' ...' if isinstance(command, commands.Group) else ''}\n'''
    return discord.Embed(title = 'Info', description = helpText)

def setup(bot):
    bot.add_cog(CustomHelp(bot))