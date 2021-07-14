import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

class Ai(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.aiBot = self.bot.get_user(os.getenv('DISCORD_ID_AISUPBOT')) #get AI discord bot
        self.lastMessageChannel = None

    #if got response from ai bot in dm's post it to last message channel
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild == None and message.author == self.aiBot:
            await self.lastMessageChannel.send(message)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            await self._send_dm_to_ai(ctx, ctx.message) #send ai response

    #send dm to ai bot
    @commands.command(name = 'ai' aliases=['si'])
    async def _send_dm_to_ai(self, ctx, text : str, *args):
        #get text after space
        spaceText = ""
        for txt in args:
            spaceText += (" " + str(txt))

        if(self.aiBot != None):
            await self.aiBot.send('yoai ' + text + spaceText)
            self.lastMessageChannel = ctx.channel

    
def setup(bot):
    bot.add_cog(AI(bot))