import discord
from discord.ext import commands

class Admin(commands.Cog):
    """Admin-only"""
    def __init__(self, bot):
        self.bot = bot
    

    #check if sender is admin
    def is_admin(self):
        def predicate(ctx):
            return (ctx.message.author.id == self.bot.owner_id or str(ctx.message.author.id) in self.bot.data["setting"]["admin"]["admin_ids"])
        return commands.check(predicate)


    @commands.command(name = 'adminsay', aliases = [])
    @is_admin()
    async def _say(self, ctx, channel_id, userText : str, *args):
        """Wypisz tekst na dowolnym kanale (yo adminsay [id_kanału] [tekst])"""
        channel = self.bot.get_channel(channel_id)

        #get text after space
        spaceText = ""
        for txt in args:
            spaceText += (" " + str(txt))

        text = (userText + spaceText) #combine text

        await channel.send(text)
        if self.bot.data["debug"]["admin"]:
            print(f'[admin][_say]Admin ({str(ctx.message.author.mention)}) sent {text} on channel {channel.name}\n')


    @_say.error
    async def _error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply('Nie masz uprawnień do tej komendy', delete_after=5)


def setup(bot):
    bot.add_cog(Admin(bot))