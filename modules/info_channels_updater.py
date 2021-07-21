import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv

load_dotenv() #load .env

class InfoChannelsUpdater(commands.Cog):
    """Aktualizator kanałów statystycznych"""
    def __init__(self, bot):
        self.bot = bot

        #assign info channels
        for guild in bot.guilds:
            if(guild.id == os.getenv('DISCORD_ID_BOBERSCHLESIEN')): #boberschlesien
                self.bbsch = guild #get guild

                #get info channels
                self.bbsch_online = discord.utils.get(guild.voice_channels, id=os.getenv('DISCORD_ID_BBSCH_ONLINE'))
                self.bbsch_bot = discord.utils.get(guild.voice_channels, id=os.getenv('DISCORD_ID_BBSCH_BOT'))
                self.bbsch_in_vc = discord.utils.get(guild.voice_channels, id=os.getenv('DISCORD_ID_BBSCH_INVC'))

            elif(guild.id == os.getenv('DISCORD_ID_SCAMELOT')): #scamelot
                self.scamelot = guild #get guild
                
                #get info channels
                self.scamelot_online = discord.utils.get(guild.voice_channels, id=os.getenv('DISCORD_ID_SCAMELOT_ONLINE'))
                self.scamelot_offline = discord.utils.get(guild.voice_channels, id=os.getenv('DISCORD_ID_SCAMELOT_OFFLINE'))
                self.scamelot_total = discord.utils.get(guild.voice_channels, id=os.getenv('DISCORD_ID_SCAMELOT_TOTAL'))
                self.scamelot_bot = discord.utils.get(guild.voice_channels, id=os.getenv('DISCORD_ID_SCAMELOT_BOT'))

        self._updater.start()

    def cog_unload(self):
        self._updater.cancel()


    #updater
    @tasks.loop(seconds=60.0)
    async def _updater(self):
        #boberschlesien
        if(self.bbsch_online != None):
            bbsch_online_count = 0
            bbsch_bot_count = 0
            bbsch_invc_count = 0

            #count online/all members 
            for user in self.bbsch.members:
                if user.status != discord.Status.offline and user.bot == False:
                    bbsch_online_count += 1
                if user.bot:
                    bbsch_bot_count += 1

            bbsch_total_count = self.bbsch.member_count - bbsch_bot_count

            voice_channel_list = self.bbsch.voice_channels
            for vc in voice_channel_list:
                bbsch_invc_count += len(vc.members)
        
            #edit channels
            await self.bbsch_online.edit(name='🟢Online: ' + str(bbsch_online_count) + '/' + str(bbsch_total_count)) 
            if(self.bbsch_in_vc != None):
                await self.bbsch_in_vc.edit(name='🎤Na kanałach: ' + str(bbsch_invc_count))   
            if(self.bbsch_bot != None):
                await self.bbsch_bot.edit(name='🤖Bot: ' + str(bbsch_bot_count))  
            

        #scamelot
        if(self.scamelot_online != None): 
            scamelot_online_count = 0
            scamelot_bot_count = 0

            #Calculate online/all members
            for user in self.scamelot.members:
                if user.status != discord.Status.offline and user.bot == False:
                    scamelot_online_count += 1
                if user.bot:
                    scamelot_bot_count += 1

            scamelot_total_count = self.scamelot.member_count - scamelot_bot_count

            scamelot_offline_count = scamelot_total_count - scamelot_online_count

            await self.scamelot_online.edit(name='Online: ' + str(scamelot_online_count))
            if(self.scamelot_offline != None):
                await self.scamelot_offline.edit(name='Offline: ' + str(scamelot_offline_count))
            if(self.scamelot_total != None):    
                await self.scamelot_total.edit(name='Total: ' + str(scamelot_total_count))
            if(self.scamelot_bot != None):
                await self.scamelot_bot.edit(name='BOTS: ' + str(scamelot_bot_count))


    #wait until bot is ready
    @_updater.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()
    
def setup(bot):
    bot.add_cog(InfoChannelsUpdater(bot))