import discord
from discord.ext import commands
import datetime

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        ctx = member.guild.system_channel

        embed = discord.Embed()
        embed.set_author(name='👋Użytkownik opuścił serwer')

        await self._userinfo(ctx, member, embed)


    @commands.Cog.listener()
    async def on_member_join(self, member):
        ctx = member.guild.system_channel

        embed = discord.Embed()
        embed.set_author(name='👋Użytkownik dołączył na serwer')

        await self._userinfo(ctx, member, embed)


    #TODO MODIFY
    #combined info
    @commands.command(name = 'info', aliases = ['stats'])
    async def _info(self, ctx):
        return #TEMP


    #user info
    @commands.command(name = 'userinfo', aliases = ['user', 'infouser', 'counter', 'baninfo', 'kickinfo', 'userstats'])
    async def _userinfo(self, ctx, member:discord.Member, embed:discord.Embed=None):
        
        #ban counter
        ban_entries = []

        async for x in ctx.guild.audit_logs(before=None, after=None, oldest_first=None, action=discord.AuditLogAction.ban):
            if(x.target == member):
                ban_entries.append(x)

        ban_count = len(ban_entries)

        #kick counter
        kick_entries = []

        async for x in ctx.guild.audit_logs(before=None, after=None, oldest_first=None, action=discord.AuditLogAction.kick):
            if(x.target == user):
                kick_entries.append(x)

        kick_count = len(kick_entries)
        
        #embed
        if embed==None:
            embed=discord.Embed()
            embed.set_author(name='🛈 Informacje o użytkowniku:')

        embed.title = member.name
        embed.colour = member.color

        embed.set_thumbnail(url=member.avatar_url) #avatar

        #info
        if member.bot = True:
            embed.description='🤖BOT'

        #created/joined at
        embed.add_field(name="🚪Dołączono do serwera", value=member.joined_at, inline=True)
        embed.add_field(name="🌟Utworzono konto", value=member.created_at, inline=True)

        embed.add_field(name=" ", value=" ", inline=False) #separator

        #ban/kick
        embed.add_field(name="🥾Kicki", value=str(kick_count), inline=True)
        embed.add_field(name="🔒Bany", value=str(ban_count), inline=True)

        embed.add_field(name=" ", value=" ", inline=False) #separator

        #roles
        embed.add_field(name="📜Rola", value=member.top_role, inline=False)

        #timestamp
        embed.timestamp = datetime.datetime.utcnow()

        await ctx.send(embed=embed)


        #TODO MODIFY
        #server info
        @commands.command(name = 'serverinfo', aliases = ['server', 'infoserver', 'serwer', 'infoserwer', 'serwerinfo', 'serverstats'])
        async def _serverinfo(self, ctx):
            
            #embed
            embed=discord.Embed()
            embed.set_author(name='🛈 Informacje o serwerze:')

            embed.title = ctx.guild.name
            embed.colour = member.color

            embed.set_thumbnail(url=member.avatar_url) #avatar

            #info
            if member.bot = True:
                embed.description='🤖BOT'

            #created/joined at
            embed.add_field(name="🚪Dołączono do serwera", value=member.joined_at, inline=True)
            embed.add_field(name="🌟Utworzono konto", value=member.created_at, inline=True)

            embed.add_field(name=" ", value=" ", inline=False) #separator

            #ban/kick
            embed.add_field(name="🥾Kicki", value=str(kick_count), inline=True)
            embed.add_field(name="🔒Bany", value=str(ban_count), inline=True)

            embed.add_field(name=" ", value=" ", inline=False) #separator

            #roles
            embed.add_field(name="📜Rola", value=member.top_role, inline=False)

            #timestamp
            embed.timestamp = datetime.datetime.utcnow()

            await ctx.send(embed=embed)


        #TODO MODIFY
        #bot info
        @commands.command(name = 'botinfo', aliases = ['infobot', 'bot', 'infosupbot', 'supbotinfo', 'about', 'aboutbot'])
        async def _botinfo(self, ctx):
            
            #embed
            embed=discord.Embed()
            embed.set_author(name='🛈 Informacje o SupBOT:')

            embed.title = ctx.guild.name
            embed.colour = member.color

            embed.set_thumbnail(url=member.avatar_url) #avatar

            #info
            if member.bot = True:
                embed.description='🤖BOT'

            #created/joined at
            embed.add_field(name="🚪Dołączono do serwera", value=member.joined_at, inline=True)
            embed.add_field(name="🌟Utworzono konto", value=member.created_at, inline=True)

            embed.add_field(name=" ", value=" ", inline=False) #separator

            #ban/kick
            embed.add_field(name="🥾Kicki", value=str(kick_count), inline=True)
            embed.add_field(name="🔒Bany", value=str(ban_count), inline=True)

            embed.add_field(name=" ", value=" ", inline=False) #separator

            #roles
            embed.add_field(name="📜Rola", value=member.top_role, inline=False)

            #timestamp
            embed.timestamp = datetime.datetime.utcnow()

            await ctx.send(embed=embed)
        

def setup(bot):
    bot.add_cog(Info(bot))