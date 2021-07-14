 
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv() #load .env

class RoleAssigner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        #assign guilds
        for guild in bot.guilds:
            if(guild.id == os.getenv('DISCORD_ID_BOBERSCHLESIEN')): #boberschlesien
                self.bbsch = guild #get guild

            elif(guild.id == os.getenv('DISCORD_ID_SCAMELOT')): #scamelot
                self.scamelot = guild #get guild


    @commands.Cog.listener()
    async def on_member_join(self, member):

        #boberschlesien
        if(member.guild.id == self.bbsch):
            bbsch_rank_dj = discord.utils.get(member.guild.roles, id=os.getenv('DISCORD_ROLE_BBSCH_DJ')) #Bot get guild(server) dj role
            if(bbsch_rank_dj != None):
                await member.add_roles(bbsch_rank_dj) #add role

        #scamelot
        elif(member.guild.id == self.scamelot): 
            scamelot_rank_dj = discord.utils.get(member.guild.roles, id=os.getenv('DISCORD_ROLE_SCAMELOT_DJ')) #Bot get guild(server) dj role
            if(scamelot_rank_dj != None):
                await member.add_roles(scamelot_rank_dj) #add role

            scamelot_rank_scam = discord.utils.get(member.guild.roles, id=os.getenv('DISCORD_ROLE_SCAMELOT_SCAM')) #Bot get guild(server) scam role
            if(scamelot_rank_scam != None):
                await member.add_roles(scamelot_rank_scam) #add role

    
def setup(bot):
    bot.add_cog(RoleAssigner(bot))