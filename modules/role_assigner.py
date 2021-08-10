 
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import os
from dotenv import load_dotenv
import datetime

load_dotenv() #load .env

class RoleAssigner(commands.Cog):
    """Przypisywanie ról"""
    def __init__(self, bot):
        self.bot = bot
        
        if self.bot.settings["debug"]["role_assigner"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][role_assigner]Loaded")


    @commands.Cog.listener()
    @has_permissions(manage_roles=True)
    async def on_member_join(self, member):
        if (str(member.guild.id) in self.bot.settings["setting"]["role_assigner"] and self.bot.settings["setting"]["role_assigner"][str(member.guild.id)]["assign_roles"]): #if guild is set to assign roles
            
            #foreach role to assign in each guild
            for role_env_name in self.bot.settings["setting"]["role_assigner"][str(member.guild.id)]["roles"]:
            
                role = discord.utils.get(member.guild.roles, id=int(os.getenv(str(role_env_name)))) #get role

                if role != None:
                    await member.add_roles(role) #assign role

                    if self.bot.settings["debug"]["role_assigner"]:
                        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][role_assigner][on_member_join]Assigned {role.name} to {member.name}\n')

    
def setup(bot):
    bot.add_cog(RoleAssigner(bot))