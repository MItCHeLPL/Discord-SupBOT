import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import datetime
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle

class Info(commands.Cog):
    """Inforamcje i statystyki"""
    def __init__(self, bot):
        self.bot = bot

        if self.bot.data["debug"]["info"]:
            print(f"[info]Loaded")

    @commands.Cog.listener()
    async def on_member_remove(self, member):

        if (str(member.guild.id) in self.bot.data["setting"]["info"] and self.bot.data["setting"]["info"][str(member.guild.id)]["show_info_on_leave"]) or (str(member.guild.id) not in self.bot.data["setting"]["info"] and self.bot.data["setting"]["info"]["default"]["show_info_on_leave"]):
            ctx = member.guild.system_channel

            embed = discord.Embed()
            embed.set_author(name='👋Użytkownik opuścił serwer') #embed header

            if member.bot == True:
                embed.description = '`🤖BOT`\n ' #add bot tag

            await self._userinfo(ctx, member, embed)

            if self.bot.data["debug"]["info"]:
                print(f'[info][on_member_remove]{member.name} left {member.guild.name}. Requested user info')


    @commands.Cog.listener()
    async def on_member_join(self, member):

        if (str(member.guild.id) in self.bot.data["setting"]["info"] and self.bot.data["setting"]["info"][str(member.guild.id)]["show_info_on_join"]) or (str(member.guild.id) not in self.bot.data["setting"]["info"] and self.bot.data["setting"]["info"]["default"]["show_info_on_join"]):
            ctx = member.guild.system_channel

            embed = discord.Embed()
            embed.set_author(name='👋Użytkownik dołączył na serwer') #embed header

            if member.bot == True:
                embed.description = '`🤖BOT`\n ' #add bot tag

            await self._userinfo(ctx, member, embed)

            if self.bot.data["debug"]["info"]:
                print(f'[info][on_member_join]{member.name} joined {member.guild.name}. Requested user info')


    #combined info
    @commands.command(name = 'info', aliases = ['stats'])
    async def _info(self, ctx):
        """Wszystkie informacje"""
        await self._userinfo(ctx, ctx.author)
        await self._serverinfo(ctx)
        await self._botinfo(ctx)

        if self.bot.data["debug"]["info"]:
            print(f'[info][_info]Requested full info')


    #user info
    @commands.command(name = 'userinfo', aliases = ['user', 'infouser', 'baninfo', 'kickinfo', 'userstats'])
    async def _userinfo(self, ctx, member:discord.Member=None, embed:discord.Embed=None, action_row=None):
        """Informacje o użytkowniku (yo userinfo [@użytkownik])"""
        if member == "":
            member = ctx.author

        #Calculate total kick amount
        kick_count = 0
        async for x in ctx.guild.audit_logs(limit=None, before=None, after=None, oldest_first=None, action=discord.AuditLogAction.kick):
            if(x.target == member):
                kick_count += 1

        #Calculate total ban amount
        ban_count = 0
        async for x in ctx.guild.audit_logs(limit=None, before=None, after=None, oldest_first=None, action=discord.AuditLogAction.ban):
            if(x.target == member):
                ban_count += 1
        

        #embed
        if embed==None:
            embed=discord.Embed()
            embed.set_author(name='🛈 Informacje o użytkowniku:')

            if member.bot == True:
                embed.description = '`🤖BOT`\n ' #add bot tag

        embed.title = str(member.name)
        embed.colour = member.color

        embed.set_thumbnail(url=member.avatar_url) #avatar

        #info
        #created/joined at
        embed.add_field(name="🚪Dołączono do serwera", value=('`'+str(member.joined_at)[0:-7]+'`'), inline=True)
        embed.add_field(name="🌟Utworzono konto", value=('`'+str(member.created_at)[0:-7]+'`'), inline=True)

        embed.add_field(name="‌‌ ", value="‌‌ ", inline=False) #separator

        #ban/kick
        embed.add_field(name="🥾Kicki", value=('`'+str(kick_count)+'`'), inline=True)
        embed.add_field(name="🔒Bany", value=('`'+str(ban_count)+'`'), inline=True)

        #add bot fields
        if member.bot == True:

            embed.add_field(name="‌‌ ", value="‌‌ ", inline=False) #separator

            #server count/ping
            embed.add_field(name="📊Ilość serwerów", value=('`'+str(len(ctx.bot.guilds))+'`'), inline=True)
            embed.add_field(name="📶Ping", value=('`'+str(round(ctx.bot.latency * 100, 2)) + "ms"+'`'), inline=True)

            embed.add_field(name="‌‌ ", value="‌‌ ", inline=False) #separator

            #generate guild list
            guilds = ''
            for guild in ctx.bot.guilds:
                guilds += '`➤' + str(guild.name) + '`\n'

            #guild list
            embed.add_field(name="📊Serwery", value=guilds, inline=False)

        embed.add_field(name="‌‌ ", value="‌‌ ", inline=False) #separator

        #roles
        embed.add_field(name="📜Najwyższa rola", value=('`'+str(member.top_role)+'`'), inline=False)

        #timestamp
        embed.timestamp = datetime.datetime.utcnow()

        if action_row is None:
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed, components=[action_row])

        if self.bot.data["debug"]["info"]:
            print(f'[info][_userinfo]Sent info about {member.name}\n')



    #server info
    @commands.command(name = 'serverinfo', aliases = ['server', 'infoserver', 'serwer', 'infoserwer', 'serwerinfo', 'serverstats'])
    @has_permissions(view_audit_log=True)
    async def _serverinfo(self, ctx):
        """Informacje o serwerze"""
        #Calculate online/offline members
        online_count = 0
        bot_count = 0
        invc_count = 0

        for user in ctx.guild.members:
            if user.status != discord.Status.offline and user.bot == False:
                online_count += 1
            if user.bot:
                bot_count += 1

        offline_count = ctx.guild.member_count - online_count

        #Calculate in vc members
        for vc in ctx.guild.voice_channels:
            invc_count += len(vc.members)

        #Calculate total kick amount
        kick_count = 0
        async for x in ctx.guild.audit_logs(limit=None, before=None, after=None, oldest_first=None, action=discord.AuditLogAction.kick):
            kick_count += 1

        #Calculate total ban amount
        ban_count = 0
        async for x in ctx.guild.audit_logs(limit=None, before=None, after=None, oldest_first=None, action=discord.AuditLogAction.ban):
            ban_count += 1

        #Calculate current ban amount
        current_ban_count = await ctx.guild.bans()


        #embed
        embed=discord.Embed()
        embed.set_author(name='🛈 Informacje o serwerze:')

        embed.title = str(ctx.guild.name)
        embed.colour = ctx.author.color #random color

        embed.set_thumbnail(url=ctx.guild.icon_url) #server banner

        #info
        #created/owner/region
        embed.add_field(name="👑Właściciel", value=str(ctx.guild.owner.mention), inline=True)
        embed.add_field(name="🌟Utworzono", value=('`'+str(ctx.guild.created_at)[0:-7]+'`'), inline=True)
        embed.add_field(name="🌎Region", value=('`'+str(ctx.guild.region)+'`'), inline=True)

        embed.add_field(name="‌‌ ", value="‌‌ ", inline=False) #separator

        #online/offline/all/onchannel/bot
        embed.add_field(name="🟢Online", value=('`'+str(online_count) + '/' + str(offline_count)+'`'), inline=True)
        embed.add_field(name="🎤Na kanałach", value=('`'+str(invc_count)+'`'), inline=True)
        embed.add_field(name="🤖Botów", value=('`'+str(bot_count)+'`'), inline=True)
        embed.add_field(name="👤Razem", value=('`'+str(ctx.guild.member_count)+'`'), inline=True)

        embed.add_field(name="‌‌ ", value="‌‌ ", inline=False) #separator

        #ban/kick
        embed.add_field(name="🥾Kicki", value=('`'+str(kick_count)+'`'), inline=True)
        embed.add_field(name="🔒Bany razem", value=('`'+str(ban_count)+'`'), inline=True)
        embed.add_field(name="🔒Bany teraz", value=('`'+str(len(current_ban_count))+'`'), inline=True)

        embed.add_field(name="‌‌ ", value="‌‌ ", inline=False) #separator

        #voice/tex/all channels
        embed.add_field(name="🎤Kanały głosowe", value=('`'+str(len(ctx.guild.voice_channels))+'`'), inline=True)
        embed.add_field(name="💬Kanały tekstowe", value=('`'+str(len(ctx.guild.text_channels))+'`'), inline=True)
        embed.add_field(name="#️⃣Kanały razem", value=('`'+str(len(ctx.guild.channels))+'`'), inline=True)

        embed.add_field(name="‌‌ ", value="‌‌ ", inline=False) #separator

        #roles
        embed.add_field(name="📜Ilość ról", value=('`'+str(len(ctx.guild.roles))+'`'), inline=True)

        #timestamp
        embed.timestamp = datetime.datetime.utcnow()

        await ctx.send(embed=embed)

        if self.bot.data["debug"]["info"]:
            print(f'[info][_serverinfo]Sent info about {ctx.guild.name}\n')


    #bot info
    @commands.command(name = 'botinfo', aliases = ['infobot', 'infosupbot', 'supbotinfo', 'about', 'aboutbot', 'github', 'project'])
    async def _botinfo(self, ctx):
        """Informacje o tym bocie"""
        embed=discord.Embed() 
        embed.set_author(name='🛈 Informacje o bocie:') #embed header

        if self.bot.data["setting"]["info"]["show_bot_author_info"]:   
            embed.description = '**Twórca: [M!tCHeL](https://github.com/MItCHeLPL)**\n**Projekt: [GitHub](https://github.com/MItCHeLPL/Discord-SupBOT)**\n\n`🤖BOT`\n '
        else:
            embed.description = '`🤖BOT`\n '

        await self._userinfo(ctx, ctx.me, embed) #show user info about bot

        if self.bot.data["debug"]["info"]:
            print(f'[info][_botinfo]Requested info about SupBOT')
        

def setup(bot):
    bot.add_cog(Info(bot))