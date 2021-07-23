 
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import os
from dotenv import load_dotenv

load_dotenv() #load .env

class RoleAssigner(commands.Cog):
    """Przypisywanie ról"""
    def __init__(self, bot):
        self.bot = bot

        self.bbsch = None
        self.bbsch_rank_dj = None
        self.scamelot = None
        self.scamelot_rank_dj = None
        self.scamelot_rank_scam = None
        
        if self.bot.data["debug"]["role_assigner"]:
            print(f"[role_assigner]Loaded")

    @commands.Cog.listener()
    async def on_ready(self):    
        #assign guilds
        for guild in self.bot.guilds:
            if (str(guild.id) in self.bot.data["setting"]["role_assigner"] and self.bot.data["setting"]["role_assigner"][str(guild.id)]["assign_roles"]) or self.bot.data["setting"]["role_assigner"]["default"]["assign_roles"]:
                if(guild.id == os.getenv('DISCORD_ID_BOBERSCHLESIEN')): #boberschlesien
                    self.bbsch = guild #get guild
                    self.bbsch_rank_dj = discord.utils.get(guild.roles, id=os.getenv('DISCORD_ROLE_BBSCH_DJ')) #Bot get guild(server) dj role

                elif(guild.id == os.getenv('DISCORD_ID_SCAMELOT')): #scamelot
                    self.scamelot = guild #get guild
                    self.scamelot_rank_dj = discord.utils.get(guild.roles, id=os.getenv('DISCORD_ROLE_SCAMELOT_DJ')) #Bot get guild(server) dj role
                    self.scamelot_rank_scam = discord.utils.get(guild.roles, id=os.getenv('DISCORD_ROLE_SCAMELOT_SCAM')) #Bot get guild(server) scam role


    @commands.Cog.listener()
    @has_permissions(manage_roles=True)
    async def on_member_join(self, member):
        if (str(member.guild.id) in self.bot.data["setting"]["role_assigner"] and self.bot.data["setting"]["role_assigner"][str(member.guild.id)]["assign_roles"]) or self.bot.data["setting"]["role_assigner"]["default"]["assign_roles"]:
            #boberschlesien
            if(member.guild.id == self.bbsch):
                if(self.bbsch_rank_dj != None):
                    await member.add_roles(self.bbsch_rank_dj) #add role

            #scamelot
            elif(member.guild.id == self.scamelot): 
                if(self.scamelot_rank_dj != None):
                    await member.add_roles(self.scamelot_rank_dj) #add role

                if(self.scamelot_rank_scam != None):
                    await member.add_roles(self.scamelot_rank_scam) #add role

            if self.bot.data["debug"]["role_assigner"]:
                print(f'[role_assigner][on_member_join]Assigned roles to {member.name}\n')

    
def setup(bot):
    bot.add_cog(RoleAssigner(bot))