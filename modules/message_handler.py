import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from discord_slash import cog_ext, SlashContext
import datetime

class MessageHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if self.bot.settings["debug"]["message_handler"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][message_handler]Loaded")


    #any message
    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.settings["setting"]["message_handler"]["reply_yo"]:   
            #reply 'yo', if someone says yo
            if (message.content.strip().lower() == 'yo' and message.author.bot == False):
                await message.reply('yo')

                if self.bot.settings["debug"]["message_handler"]:
                    print(f'[{str(datetime.datetime.utcnow())[0:-7]}][message_handler][on_message]Sent yo\n')

        #if message has prefix and command name/alias matches the one in message add processing emoji
        if (message.content.startswith('yo ') or message.content.startswith('Yo ')) and message.author.bot == False:
            for x in self.bot.commands: #cycle through normal commands
                if message.content[3:(None if message.content.find(" ", 4) == -1 else message.content.find(" ", 4)+1)] == x.name or message.content[3:(None if message.content.find(" ", 4) == -1 else message.content.find(" ", 4)+1)] in x.aliases: #if found command in message
                    await message.add_reaction('⌛') #add processing command emoji
                    break

    #yo slash command
    @cog_ext.cog_slash(name="yo", 
        description="yo"
    )
    async def _yo_slash(self, ctx:SlashContext):
        await ctx.send("yo")

        if self.bot.settings["debug"]["message_handler"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][message_handler][_yo_slash]Sent yo\n')

                    
    #normal command error
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            await ctx.message.add_reaction('❌') #add error emoji
            if self.bot.settings["setting"]["message_handler"]["reply_error_message"]:   
                await ctx.reply('Yo, nie rozumiem,\nWpisz `yo help` i przestań mi bota prześladować', delete_after=10) #error message

        if self.bot.settings["debug"]["message_handler"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][message_handler][on_command_error]Command error: {error}\n')

    #slash command error
    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx: SlashContext, error):
        if self.bot.settings["setting"]["message_handler"]["reply_error_message"]:   
            await ctx.send('Yo, wystąpił błąd komendy,\nWpisz `yo help` lub `/help` i przestań mi bota prześladować', hidden=True) #error message

        if self.bot.settings["debug"]["message_handler"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][message_handler][on_slash_command_error]Command error: {error}\n')


    #normal command success
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.message != None:
            await ctx.message.remove_reaction('⌛', self.bot.user) #remove processing emoji
            await ctx.message.add_reaction('✅') #add success emoji
            

def setup(bot):
    bot.add_cog(MessageHandler(bot))