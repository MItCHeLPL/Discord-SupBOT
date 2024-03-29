import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
import os
from dotenv import load_dotenv
import datetime

load_dotenv() #load .env

class InfoChannelsUpdater(commands.Cog):
    """Aktualizator kanałów statystycznych"""
    def __init__(self, bot):
        self.bot = bot

        self._updater.start() #start task

        if self.bot.settings["debug"]["info_channels_updater"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][info_channels_updater]Loaded")

        
    def cog_unload(self):
        self._updater.cancel() #stop task after unloading module


    #updater
    @tasks.loop(seconds=60.0) #loop every 60sec
    @has_permissions(manage_channels=True)
    async def _updater(self):
        for guild in self.bot.guilds:
            if (str(guild.id) in self.bot.settings["setting"]["info_channels_updater"] and self.bot.settings["setting"]["info_channels_updater"][str(guild.id)]["update_channels"]):

                #get channels for each guild
                channel_online = discord.utils.get(guild.voice_channels, id=int(os.getenv(str(self.bot.settings["setting"]["info_channels_updater"][str(guild.id)]["channels"]["channel_online"]))))
                channel_invc = discord.utils.get(guild.voice_channels, id=int(os.getenv(str(self.bot.settings["setting"]["info_channels_updater"][str(guild.id)]["channels"]["channel_in_vc"]))))
                channel_bot = discord.utils.get(guild.voice_channels, id=int(os.getenv(str(self.bot.settings["setting"]["info_channels_updater"][str(guild.id)]["channels"]["channel_bot"]))))

                if(channel_online != None and channel_invc != None and channel_bot != None):
                    online_count = 0
                    total_count = 0
                    invc_count = 0
                    bot_count = 0

                    #count online/bot members
                    for user in guild.members:
                        if user.status != discord.Status.offline and user.bot == False:
                            online_count += 1
                        if user.bot:
                            bot_count += 1

                    #count total members 
                    total_count = guild.member_count - bot_count

                    #count members in voice chat
                    for vc in guild.voice_channels:
                        invc_count += len(vc.members)
                
                    #edit channels
                    await channel_online.edit(name='🟢Online: ' + str(online_count) + '/' + str(total_count)) 
                    await channel_invc.edit(name='🎤Na kanałach: ' + str(invc_count))   
                    await channel_bot.edit(name='🤖Bot: ' + str(bot_count))  

                    if self.bot.settings["debug"]["info_channels_updater"]:
                        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][info_channels_updater][_updater]Updated {guild.name} info channels\n')


    #wait until bot is ready
    @_updater.before_loop
    async def before_updater(self):
        await self.bot.wait_until_ready()
    

def setup(bot):
    bot.add_cog(InfoChannelsUpdater(bot))