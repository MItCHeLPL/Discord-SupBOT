import discord
from discord.ext import commands
import datetime
import random
import math

class Admin(commands.Cog):
    """Admin-only"""

    def __init__(self, bot):
        self.bot = bot

        global globbot
        globbot = self.bot

        if self.bot.data["debug"]["admin"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][admin]Loaded")


    #check if sender is admin
    def is_admin(ctx):
        return (str(ctx.message.author.id) in globbot.data["setting"]["admin"]["admin_ids"])


    @commands.command(name = 'adminsay', aliases = ['sayadmin', 'ownersay', 'sayowner', 'admin_say', 'say_admin', 'owner_say', 'say_owner'])
    @commands.check(is_admin)
    async def _say(self, ctx, channel_id, userText : str, *args):
        """Wypisz tekst na dowolnym kanale (yo adminsay [id_kanału] [tekst])"""
        for guild in ctx.bot.guilds:
            for channel in guild.channels:
                if str(channel.id) == channel_id:
                    #get text after space
                    spaceText = ""
                    for txt in args:
                        spaceText += (" " + str(txt))

                    text = (userText + spaceText) #combine text

                    await channel.send(text)
                    if self.bot.data["debug"]["admin"]:
                        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][admin][_say]Admin ({str(ctx.message.author.name)}) sent {text} on channel {channel.name}\n')


    @commands.command(name = 'showlog', aliases = ['showoutput', 'log', 'botlog', 'printlog', 'logprint', 'adminlog', 'adminoutput', 'dziennik', 'zdarzenia'])
    @commands.check(is_admin)
    async def _log(self, ctx):
        """Wysyła dziennik zdarzeń bota w dm"""

        with open("output.log") as file:
            data = file.read()

        txt = data[data.rfind("[main][__main__]--------SETUP STARTED--------"):] #find newest log

        #4096 - limit of characters in embed description
        for x in range(0, math.ceil(len(txt)/4096)):
            embed=discord.Embed() 
            embed.colour = random.randint(0, 0xffffff)
            embed.title = f'Dziennik zdarzeń ({x+1}/{str(math.ceil(len(txt)/4096))})' #set title
            embed.timestamp = datetime.datetime.utcnow()

            embed.description = txt[x*4096:(x+1)*4096] #split log to embeds

            await ctx.author.send(embed=embed) 

        if self.bot.data["debug"]["admin"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][admin][_log]Sent debug log to {str(ctx.author.name)}\n')


    @_say.error
    async def _error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply('Nie masz uprawnień do tej komendy', delete_after=5)

            if self.bot.data["debug"]["admin"]:
                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][admin][_error]{ctx.author.name} doesnt have permission to use admin command\n')


def setup(bot):
    bot.add_cog(Admin(bot))