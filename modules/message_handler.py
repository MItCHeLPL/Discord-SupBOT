import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound

class MessageHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if self.bot.data["debug"]["message_handler"]:
            print(f"[message_handler]Loaded")


    #any message
    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.data["setting"]["message_handler"]["reply_yo"]:   
            #reply 'yo', if someone says yo
            if ((message.content == 'yo' or message.content == 'Yo' or message.content == 'yo ' or message.content == 'Yo ') and message.author.bot == False):
                await message.reply('yo')

                if self.bot.data["debug"]["message_handler"]:
                    print(f'[message_handler][on_message]Sent yo\n')

        #if message has prefix and command name/alias matches the one in message add processing emoji
        if (message.content.startswith('yo ') or message.content.startswith('Yo ')) and message.author.bot == False:
            for x in self.bot.commands:
                if message.content[3:(None if message.content.find(" ", 4) == -1 else message.content.find(" ", 4)+1)] == x.name or message.content[3:(None if message.content.find(" ", 4) == -1 else message.content.find(" ", 4)+1)] in x.aliases:
                    await message.add_reaction('⌛') #processing command
                    break

                    
    #command error
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            await ctx.message.add_reaction('❌') #add emoji
            if self.bot.data["setting"]["message_handler"]["reply_error_message"]:   
                await ctx.reply('Yo, nie rozumiem,\nWpisz `yo help` i przestań mi bota prześladować', delete_after=10) #error message

            if self.bot.data["debug"]["message_handler"]:
                print(f'[message_handler][on_command_error]Command error\n')


    #command success
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        await ctx.message.add_reaction('✅') #add emoji
        await ctx.message.remove_reaction('⌛', self.bot.user) #processed

def setup(bot):
    bot.add_cog(MessageHandler(bot))