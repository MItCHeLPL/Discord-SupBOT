 
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv() #load .env

class RoleAssigner(commands.Cog):
    """Przypisywanie ról"""
    def __init__(self, bot):
        self.bot = bot

        #assign guilds
        for guild in bot.guilds:
            if (str(guild.id) in self.bot.data["setting"]["role_assigner"] and self.bot.data["setting"]["role_assigner"][str(guild.id)]["assign_roles"]) or self.bot.data["setting"]["role_assigner"]["default"]["assign_roles"]:
                if(guild.id == os.getenv('DISCORD_ID_BOBERSCHLESIEN')): #boberschlesien
                    self.bbsch = guild #get guild
                    self.bbsch_rank_dj = discord.utils.get(guild.roles, id=os.getenv('DISCORD_ROLE_BBSCH_DJ')) #Bot get guild(server) dj role

                elif(guild.id == os.getenv('DISCORD_ID_SCAMELOT')): #scamelot
                    self.scamelot = guild #get guild
                    self.scamelot_rank_dj = discord.utils.get(guild.roles, id=os.getenv('DISCORD_ROLE_SCAMELOT_DJ')) #Bot get guild(server) dj role
                    self.scamelot_rank_scam = discord.utils.get(guild.roles, id=os.getenv('DISCORD_ROLE_SCAMELOT_SCAM')) #Bot get guild(server) scam role


    @commands.Cog.listener()
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

    
def setup(bot):
    bot.add_cog(RoleAssigner(bot))