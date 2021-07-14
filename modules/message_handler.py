import discord
from discord.ext import commands

class MessageHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #any message
    @commands.Cog.listener()
    async def on_message(self, message):
        #reply 'yo', if someone says yo
        if ((message.content == 'yo' or message.content == 'Yo') and message.author.bot == False):
            await message.reply('yo') 

        await self.bot.process_commands(message) #else

    #command error
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            await ctx.message.add_reaction('❌') #add emoji
            await ctx.reply('Yo, nie rozumiem,\nWpisz "**yo help**" i przestań mi bota prześladować') #error message

    #command success
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        await ctx.add_reaction('✅') #add emoji

def setup(bot):
    bot.add_cog(MessageHandler(bot))