import discord
from discord.ext import commands

class Admin(commands.Cog):
    """Admin-only"""

    def __init__(self, bot):
        self.bot = bot

        global globbot
        globbot = self.bot

        if self.bot.data["debug"]["admin"]:
            print(f"[admin]Loaded")


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
                        print(f'[admin][_say]Admin ({str(ctx.message.author.mention)}) sent {text} on channel {channel.name}\n')


    @_say.error
    async def _error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply('Nie masz uprawnień do tej komendy', delete_after=5)

            if self.bot.data["debug"]["admin"]:
                print(f'[admin][_say]{ctx.author.name} doesnt have permission to use admin command\n')


def setup(bot):
    bot.add_cog(Admin(bot))