import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound

class MessageHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #any message
    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.data["setting"]["message_handler"]["reply_yo"]:   
            #reply 'yo', if someone says yo
            if ((message.content == 'yo' or message.content == 'Yo') and message.author.bot == False):
                await message.reply('yo') 

                if self.bot.data["debug"]["message_handler"]:
                    print(f'[message_handler][on_message]Sent yo\n')

        await self.bot.process_commands(message) #else

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
        await ctx.add_reaction('✅') #add emoji

def setup(bot):
    bot.add_cog(MessageHandler(bot))