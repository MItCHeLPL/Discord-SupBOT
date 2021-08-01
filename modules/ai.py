import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound, has_permissions
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

class Ai(commands.Cog):
    """Komunikacja ze sztuczną inteligencją"""
    def __init__(self, bot):
        self.bot = bot

        self.aiBot = None
        self.ai_category = None
        self.bbsch_everyone_role = None

        if self.bot.data["debug"]["ai"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][ai]Loaded")

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            if guild.id == int(os.getenv('DISCORD_ID_BOBERSCHLESIEN')): #boberschlesien
                self.aiBot = discord.utils.get(guild.members, id=int(os.getenv('DISCORD_ID_AISUPBOT'))) #get AI discord bot

                if self.bot.data["setting"]["ai"]["change_cat_visibility_for_aibot"]:
                    self.ai_category = discord.utils.get(guild.categories, id=int(os.getenv('DISCORD_ID_AI_CATEGORY')))
                    self.bbsch_everyone_role = discord.utils.get(guild.roles, id=int(os.getenv('DISCORD_ROLE_BBSCH_EVERYONE')))


    @commands.Cog.listener()
    @has_permissions(manage_roles=True, manage_channels=True)
    async def on_voice_state_update(self, member, before, after):      
        if self.bot.data["setting"]["ai"]["change_cat_visibility_for_aibot"]:   
            if self.ai_category is not None and self.bbsch_everyone_role is not None:
                #show/hide AI category
                if member == self.aiBot and member.status == discord.Status.online:
                    await self.ai_category.set_permissions(self.bbsch_everyone_role, view_channel = True, read_messages = True, send_messages = False)

                    if self.bot.data["debug"]["ai"]:
                        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][ai][on_voice_state_update]Enabled AIBOT category visibility\n')
                        
                if member == self.aiBot and member.status == discord.Status.offline:
                    await self.ai_category.set_permissions(self.bbsch_everyone_role, view_channel = False, read_messages = False, send_messages = False)
                    
                    if self.bot.data["debug"]["ai"]:
                        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][ai][on_voice_state_update]Disabled AIBOT category visibility\n')

    
def setup(bot):
    bot.add_cog(Ai(bot))