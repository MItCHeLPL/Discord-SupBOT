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
        if message.author.bot is False and self.bot.settings["setting"]["archiver"]["archive_new_messeges"]:
            archive_channel = discord.utils.get(self.bot.get_all_channels(), id=int(self.bot.settings["setting"]["archiver"]["archive_channel_id"])) #get archive channel

            content = "\n◤━━━━━━━━━━━━━━\n"

            #source info
            content += ("**🟩New message** \n__🌐" + message.guild.name + "\n💬" + message.channel.name + "\n👤" + (str(message.author.name) + " #" + str(message.author.discriminator)) + "\n🆕" + str(datetime.datetime.utcnow())[0:-7] +  "__\n\n")

            #text content
            if message.content != "":
                content += message.content + "\n"

            #attachment content
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
            if payload.cached_message.author.bot is False and self.bot.settings["setting"]["archiver"]["archive_removed_messeges"]:
                archive_channel = discord.utils.get(self.bot.get_all_channels(), id=int(self.bot.settings["setting"]["archiver"]["archive_channel_id"])) #get archive channel

                content = "\n◤━━━━━━━━━━━━━━\n"

                #source info
                content += ("**🟥New removed message** \n__🌐" + payload.cached_message.guild.name + "\n💬" + payload.cached_message.channel.name + "\n👤" + (str(payload.cached_message.author.name) + " #" + str(payload.cached_message.author.discriminator)) + "\n🆕" + payload.cached_message.created_at.strftime("%Y-%m-%d %H:%M:%S") + "\n🗑️" + str(datetime.datetime.utcnow())[0:-7] +  "__\n\n")

                #text content
                if payload.cached_message.content != "":
                    content += payload.cached_message.content + "\n"

                #attachment content
                for attachment in payload.cached_message.attachments:
                    content += attachment.url + "\n"

                content += "\n"

                await archive_channel.send(content=content)

                if self.bot.settings["debug"]["archiver"]:
                    print(f'[{str(datetime.datetime.utcnow())[0:-7]}][archiver][on_raw_message_delete]Archived removed message\n')

def setup(bot):
    bot.add_cog(Archiver(bot))