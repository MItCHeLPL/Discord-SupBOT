import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import random
import datetime
import re

class Archiver(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        if self.bot.settings["debug"]["archiver"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][archiver]Loaded")


    #any message
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id is not self.bot.user.id and self.bot.settings["setting"]["archiver"]["archive_new_messeges"]:
            for id in self.bot.settings["setting"]["archiver"]["archive_channel_ids"]:
                archive_channel = discord.utils.get(self.bot.get_all_channels(), id=int(id)) #get archive channel

                content = "\n◤━━━━━━━━━━━━━━\n"
                content += "**🟩New message**"

                #source info
                if message.guild:
                    content += "\n__🌐" + message.guild.name
                    content += "\n💬" + message.channel.name
                else:
                    content += "\n__💬Direct Message"

                content += "\n👤" + (str(message.author.name) + " #" + str(message.author.discriminator)) 
                content += "\n🆕" + str(datetime.datetime.utcnow())[0:-7] +  "__\n\n"

                #text content
                if message.clean_content != "":
                    content += message.clean_content + "\n"

                content += "\n"

                #add attachments as files
                try:
                    files = [await f.to_file() for f in message.attachments]
                except:
                    #there's no files attached found
                    files = None

                    #attachment content as text
                    for attachment in message.attachments:
                        content += attachment.url + "\n"

                    content += "\n"

                try:
                    await archive_channel.send(content=content, files=files)
                except:
                    #file is too large to send
                    #attachment content as text
                    for attachment in message.attachments:
                        content += attachment.url + "\n"

                    content += "\n"

                    await archive_channel.send(content=content)

                if self.bot.settings["debug"]["archiver"]:
                    print(f'[{str(datetime.datetime.utcnow())[0:-7]}][archiver][on_message]Archived message\n')
            

    #removed message
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        if payload.cached_message is not None:
            if payload.cached_message.author.id is not self.bot.user.id and self.bot.settings["setting"]["archiver"]["archive_removed_messeges"]:
                for id in self.bot.settings["setting"]["archiver"]["archive_channel_ids"]:
                    archive_channel = discord.utils.get(self.bot.get_all_channels(), id=int(id)) #get archive channel

                    content = "\n◤━━━━━━━━━━━━━━\n"
                    content += "**🟥New removed message**"

                    #source info
                    if payload.cached_message.guild:
                        content += "\n__🌐" + payload.cached_message.guild.name
                        content += "\n💬" + payload.cached_message.channel.name
                    else:
                        content += "\n__💬Direct Message"

                    content += "\n👤" + (str(payload.cached_message.author.name) + " #" + str(payload.cached_message.author.discriminator)) 
                    content += "\n🆕" + payload.cached_message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    content += "\n🗑️" + str(datetime.datetime.utcnow())[0:-7] +  "__\n\n"

                    #text content
                    if payload.cached_message.clean_content != "":
                        content += payload.cached_message.clean_content + "\n"

                    content += "\n"

                    #add attachments as files
                    try:
                        files = [await f.to_file() for f in payload.cached_message.attachments]
                    except:
                        #there's no files attached found
                        files = None

                        #attachment content as text
                        for attachment in payload.cached_message.attachments:
                            content += attachment.url + "\n"

                        content += "\n"

                    try:
                        await archive_channel.send(content=content, files=files)
                    except:
                        #file is too large to send
                        #attachment content as text
                        for attachment in payload.cached_message.attachments:
                            content += attachment.url + "\n"

                        content += "\n"

                        await archive_channel.send(content=content)

                    if self.bot.settings["debug"]["archiver"]:
                            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][archiver][on_raw_message_delete]Archived removed message\n')

def setup(bot):
    bot.add_cog(Archiver(bot))