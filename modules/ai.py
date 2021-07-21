import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound, has_permissions
import os
from dotenv import load_dotenv

load_dotenv()

class Ai(commands.Cog):
    """Komunikacja ze sztuczną inteligencją"""
    def __init__(self, bot):
        self.bot = bot

        for guild in bot.guilds:
            if(guild.id == os.getenv('DISCORD_ID_BOBERSCHLESIEN')): #boberschlesien
                self.aiBot = discord.utils.get(guild.members, id=(os.getenv('DISCORD_ID_AISUPBOT'))) #get AI discord bot

                if self.bot.data["setting"]["ai"]["change_cat_visibility_for_aibot"]:
                    self.ai_category = discord.utils.get(guild.categories, id=(os.getenv('DISCORD_ID_AI_CATEGORY')))
                    self.bbsch_everyone_role = discord.utils.get(guild.roles, id=(os.getenv('DISCORD_ROLE_BBSCH_EVERYONE')))

        self.lastMessageChannel = None


    #if got response from ai bot in dm's post it to last message channel
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild == None and message.author == self.aiBot:
            await self.lastMessageChannel.send(message)

            if self.bot.data["debug"]["ai"]:
                print(f'[ai][on_message]Got response from AIBOT: {message}. And sent it back to text channel\n')


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            if self.bot.data["setting"]["ai"]["send_msg_to_ai_on_command_error"]:
                await self._send_dm_to_ai(ctx, ctx.message) #send ai response

                if self.bot.data["debug"]["ai"]:
                    print(f'[ai][on_command_error]Sent {ctx.message} on command error in dm to AIBOT')


    @commands.Cog.listener()
    @has_permissions(manage_roles=True, manage_channels=True)
    async def on_voice_state_update(self, member, before, after):      
        if self.bot.data["setting"]["ai"]["change_cat_visibility_for_aibot"]:   
            if self.ai_category is not None and self.bbsch_everyone_role is not None:
                #show/hide AI category
                if member == self.aiBot and member.status == discord.Status.online:
                    await self.ai_category.set_permissions(self.bbsch_everyone_role, view_channel = True, read_messages = True, send_messages = False)
                if member == self.aiBot and member.status == discord.Status.offline:
                    await self.ai_category.set_permissions(self.bbsch_everyone_role, view_channel = False, read_messages = False, send_messages = False)

                if self.bot.data["debug"]["ai"]:
                    print(f'[ai][on_voice_state_update]Updated AIBOT category visibility\n')


    #send dm to ai bot
    @commands.command(name = 'ai', aliases=['si'])
    async def _send_dm_to_ai(self, ctx, text : str, *args):
        """Zapytaj o coś sztuczną inteligencję (yo ai [tekst])"""
        #get text after space
        spaceText = ""
        for txt in args:
            spaceText += (" " + str(txt))

        if(self.aiBot != None):
            await self.aiBot.send('yoai ' + text + spaceText)
            self.lastMessageChannel = ctx.channel

            if self.bot.data["debug"]["ai"]:
                print(f'[ai][_send_dm_to_ai]Sent {text + spaceText} in dm to AIBOT\n')

    
def setup(bot):
    bot.add_cog(Ai(bot))