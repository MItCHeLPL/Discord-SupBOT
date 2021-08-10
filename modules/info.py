import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import datetime
from discord_slash import cog_ext, SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle

class Info(commands.Cog):
    """Informacje i statystyki"""
    def __init__(self, bot):
        self.bot = bot

        if self.bot.settings["debug"]["info"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][info]Loaded")


    #somebody left guild
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        #if show_info_on_leave is enabled on this guild or show_info_on_leave is enabled on default and isn't set on this guild
        if (str(member.guild.id) in self.bot.settings["setting"]["info"] and self.bot.settings["setting"]["info"][str(member.guild.id)]["show_info_on_leave"]) or (str(member.guild.id) not in self.bot.settings["setting"]["info"] and self.bot.settings["setting"]["info"]["default"]["show_info_on_leave"]):
            ctx = member.guild.system_channel #get this guild's system channel

            embed = discord.Embed()
            embed.set_author(name='👋Użytkownik opuścił serwer') #embed header

            #add member mention to embed description
            if member.bot == True:
                embed.description = f'`🤖BOT`\n{member.mention}' #add bot tag
            else:
                embed.description = f'{member.mention}'

            await self._userinfo(ctx, member, embed) #show user info with this embed

            if self.bot.settings["debug"]["info"]:
                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][info][on_member_remove]{member.name} left {member.guild.name}. Requested user info\n')


    @commands.Cog.listener()
    async def on_member_join(self, member):
        #if show_info_on_join is enabled on this guild or show_info_on_join is enabled on default and isn't set on this guild
        if (str(member.guild.id) in self.bot.settings["setting"]["info"] and self.bot.settings["setting"]["info"][str(member.guild.id)]["show_info_on_join"]) or (str(member.guild.id) not in self.bot.settings["setting"]["info"] and self.bot.settings["setting"]["info"]["default"]["show_info_on_join"]):
            ctx = member.guild.system_channel #get this guild's system channel

            embed = discord.Embed()
            embed.set_author(name='👋Użytkownik dołączył na serwer') #embed header

            #add member mention to embed description
            if member.bot == True:
                embed.description = f'`🤖BOT`\n{member.mention}' #add bot tag
            else:
                embed.description = f'{member.mention}'

            await self._userinfo(ctx, member, embed) #show user info with this embed

            if self.bot.settings["debug"]["info"]:
                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][info][on_member_join]{member.name} joined {member.guild.name}. Requested user info\n')


    #combined info
    async def _info(self, ctx):
        if self.bot.settings["debug"]["info"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][info][_info]Requested full info')

        await self._userinfo(ctx, ctx.author) #show user info about author
        await self._serverinfo(ctx) #show guild info
        await self._botinfo(ctx) #show bot info

    #normal command
    @commands.command(name = 'info',
        aliases = ['stats'], 
        brief = "Wyświetla informacje", 
        help = "Wyświetla informacje o użytkowniku, serwerze oraz bocie", 
        usage = "yo info"
    )
    async def _info_command(self, ctx):
        if self.bot.settings["debug"]["info"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][info][_info_command]{ctx.author.name} requested normal command')

        await self._info(ctx)

    #slash command
    @cog_ext.cog_slash(name="info",
        description="Wyświetla informacje",
        options=[
            create_option(
                name="choice",
                description="Jakie informacje chcesz wyświetlić",
                option_type=3,
                required=False,
                choices=[
                    create_choice(
                        name="Informacje o użytkowniku",
                        value="user"
                    ),
                    create_choice(
                        name="Informacje o serwerze",
                        value="server"
                    ),
                    create_choice(
                        name="Informacje o bocie",
                        value="bot"
                    )
                ]
            ),
            create_option(
                name="user",
                description="Użytkownik, o którym chcesz wyświetlić informacje",
                option_type=6,
                required=False
            )
        ]
    )
    async def _info_slash(self, ctx:SlashContext, choice:str=None, user:discord.Member=None):
        if self.bot.settings["debug"]["info"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][info][_info_slash]{ctx.author.name} requested slash command')

        if choice == "user": 
            if user is None:
                await self._userinfo(ctx, ctx.author) #if chosen user and didn't input @user show author info
            elif isinstance(user, discord.Member) and user.id == self.bot.user.id:
                await self._botinfo(ctx) #if chosen user and did input @SupBOT show bot info
            else:
                await self._userinfo(ctx, user) #if chosen user and did input @user show user info
        elif choice == "server":
            await self._serverinfo(ctx) #if chosen server
        elif choice == "bot":
            await self._botinfo(ctx) #if chosen bot
        else:
            await self._info(ctx) #if no choice or wrong choice show all info


    #user info
    @commands.command(name = 'userinfo',
        aliases = ['user', 'infouser', 'baninfo', 'kickinfo', 'userstats'], 
        brief = "Wyświetla informacje o użytkowniku (yo userinfo [(opt)@użytkownik])", 
        help = "Wyświetla wszystkie dostępne informacje o podanym użytkowniku, lub o wysyłającym jeśli nie podano użytkownika", 
        usage = "yo userinfo [(opt)@użytkownik]"
    )
    async def _userinfo(self, ctx, member:discord.Member=None, embed:discord.Embed=None, action_row:dict=None):
        #if member wasn't passed show info about author
        if str(member).strip() == "" or member is None:
            member = ctx.author

        #if called yo userinfo @SupBOT, call botinfo
        if member.id == self.bot.user.id and embed is None:
            await self._botinfo(ctx)
            return

        #Calculate total kick amount
        kick_count = 0
        async for x in ctx.guild.audit_logs(limit=None, action=discord.AuditLogAction.kick):
            if(x.target == member):
                kick_count += 1

        #Calculate total ban amount
        ban_count = 0
        async for x in ctx.guild.audit_logs(limit=None, action=discord.AuditLogAction.ban):
            if(x.target == member):
                ban_count += 1
        
        #embed if none passed
        if embed==None:
            embed=discord.Embed()
            embed.set_author(name='🛈 Informacje o użytkowniku:') #set header

            #add member mention to embed description
            if member.bot == True:
                embed.description = f'`🤖BOT`\n{member.mention}' #add bot tag
            else:
                embed.description = f'{member.mention}'
            
        embed.title = (str(member.name) + " #" + str(member.discriminator)) #show Name #1234 in embed title
        embed.colour = member.color

        embed.set_thumbnail(url=member.avatar_url) #avatar

        #embed fields
        #created/joined at
        embed.add_field(name="🚪Dołączono do serwera", value=('`'+str(member.joined_at)[0:-7]+'`'), inline=True)
        embed.add_field(name="🌟Utworzono konto", value=('`'+str(member.created_at)[0:-7]+'`'), inline=True)

        embed.add_field(name="‌‌ ", value="‌‌ ", inline=False) #separator

        #ban/kick
        embed.add_field(name="🥾Kicki", value=('`'+str(kick_count)+'`'), inline=True)
        embed.add_field(name="🔒Bany", value=('`'+str(ban_count)+'`'), inline=True)

        #add bot fields if user is bot
        if member.bot == True:
            embed.add_field(name="‌‌ ", value="‌‌ ", inline=False) #separator

            #server count/ping
            embed.add_field(name="📊Ilość serwerów", value=('`'+str(len(ctx.bot.guilds))+'`'), inline=True)
            embed.add_field(name="📶Ping", value=('`'+str(round(ctx.bot.latency * 100, 2)) + "ms"+'`'), inline=True)

            embed.add_field(name="‌‌ ", value="‌‌ ", inline=False) #separator

            #generate guild list
            guilds = ''
            for guild in self.bot.guilds:
                guilds += '`➤' + str(guild.name) + '`\n'

            #guild list
            embed.add_field(name="📊Serwery", value=guilds, inline=False)

        embed.add_field(name="‌‌ ", value="‌‌ ", inline=False) #separator

        #roles
        embed.add_field(name="📜Najwyższa rola", value=('`'+str(member.top_role)+'`'), inline=False)

        #timestamp
        embed.timestamp = datetime.datetime.utcnow()

        #add button if one is set, send embed
        if action_row is None:
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed, components=[action_row])

        if self.bot.settings["debug"]["info"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][info][_userinfo]Sent info about {member.name}\n')


    #server info
    @commands.command(name = 'serverinfo',
        aliases = ['server', 'infoserver', 'serwer', 'infoserwer', 'serwerinfo', 'serverstats'], 
        brief = "Wyświetla informacje o serwerze", 
        help = "Wyświetla wszystkie dostępne informacje o serwerze", 
        usage = "yo serverinfo"
    )
    @has_permissions(view_audit_log=True)
    async def _serverinfo(self, ctx):
        online_count = 0
        bot_count = 0
        invc_count = 0

        #calculate online/bot members
        for user in ctx.guild.members:
            if user.status != discord.Status.offline and user.bot == False:
                online_count += 1
            if user.bot:
                bot_count += 1

        offline_count = ctx.guild.member_count - online_count #calculate offline members

        #Calculate in voice chat members
        for vc in ctx.guild.voice_channels:
            invc_count += len(vc.members)

        #Calculate total kick amount
        kick_count = 0
        async for x in ctx.guild.audit_logs(limit=None, action=discord.AuditLogAction.kick):
            kick_count += 1

        #Calculate total ban amount
        ban_count = 0
        async for x in ctx.guild.audit_logs(limit=None, action=discord.AuditLogAction.ban):
            ban_count += 1

        #Calculate current ban amount
        current_ban_count = await ctx.guild.bans()

        #embed
        embed=discord.Embed()
        embed.set_author(name='🛈 Informacje o serwerze:') #set header

        embed.title = str(ctx.guild.name) #show guild name in title
        embed.colour = ctx.author.color #random color

        embed.set_thumbnail(url=ctx.guild.icon_url) #server banner

        #embed fields
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

        #voice/text/all channels
        embed.add_field(name="🎤Kanały głosowe", value=('`'+str(len(ctx.guild.voice_channels))+'`'), inline=True)
        embed.add_field(name="💬Kanały tekstowe", value=('`'+str(len(ctx.guild.text_channels))+'`'), inline=True)
        embed.add_field(name="#️⃣Kanały razem", value=('`'+str(len(ctx.guild.channels))+'`'), inline=True)

        embed.add_field(name="‌‌ ", value="‌‌ ", inline=False) #separator

        #roles
        embed.add_field(name="📜Ilość ról", value=('`'+str(len(ctx.guild.roles))+'`'), inline=True)

        #timestamp
        embed.timestamp = datetime.datetime.utcnow()

        #create invite to guild channel
        try:
            for invite in await ctx.guild.invites(): #try to find infinite invite
                if invite.max_age == 0:
                    invite_url = invite.url #found infinite invite
                    break
            raise Exception('InfiniteInvite', 'NotFound') #raise exception when didn't find infinite invite
        except:
            try:
                if ctx.guild.system_channel != None: #create infinite invite to system channel
                    invite_url = await ctx.guild.system_channel.create_invite(max_age = 0)
                else: #create infinite invite to message channel when system channel doesn't exist
                    invite_url = await ctx.message.channel.create_invite(max_age = 0)
            except:
                try:
                    if ctx.guild.system_channel != None: #create 5min invite to system channel
                        invite_url = await ctx.guild.system_channel.create_invite(max_age = 300)
                    else: #create 5min invite to message channel when system channel doesn't exist
                        invite_url = await ctx.message.channel.create_invite(max_age = 300)
                except:
                    pass #couldn't get an invite

        #create buttons if got guild invite            
        if invite_url is not None:
            buttons = [
                create_button(
                    style=ButtonStyle.URL,
                    label=str(f"Zaproszenie na {str(ctx.guild.name)}"),
                    url=str(invite_url)
                ),
            ]
            action_row = create_actionrow(*buttons)

        #add button if one is set, send embed
        if action_row is None:
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed, components=[action_row])

        if self.bot.settings["debug"]["info"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][info][_serverinfo]Sent info about {ctx.guild.name}\n')


    #bot info
    @commands.command(name = 'botinfo',
        aliases = ['infobot', 'infosupbot', 'supbotinfo', 'about', 'aboutbot', 'github', 'project'], 
        brief = "Wyświetla informacje o SupBOT", 
        help = "Wyświetla wszystkie dostępne informacje o tym bocie", 
        usage = "yo botinfo"
    )
    async def _botinfo(self, ctx):
        embed=discord.Embed() 
        embed.set_author(name='🛈 Informacje o bocie:') #embed header

        #show details about SupBOT in description or do standard bot user description
        if self.bot.settings["setting"]["info"]["show_bot_author_info"]:   
            embed.description = f'**Twórca: [M!tCHeL](https://github.com/MItCHeLPL)**\n**Projekt: [GitHub](https://github.com/MItCHeLPL/Discord-SupBOT)**\n`🤖BOT`\n{self.bot.user.mention}\n'
        else:
            embed.description = f'`🤖BOT`\n{self.bot.user.mention}'

        #create buttons
        buttons = [
            create_button(
                style=ButtonStyle.URL,
                label="Twórca",
                url="https://github.com/MItCHeLPL"
            ),
            create_button(
                style=ButtonStyle.URL,
                label="SupBOT",
                url="https://github.com/MItCHeLPL/Discord-SupBOT"
            ),
        ]
        action_row = create_actionrow(*buttons)

        if self.bot.settings["debug"]["info"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][info][_botinfo]Requested info about SupBOT')

        await self._userinfo(ctx, discord.utils.get(ctx.guild.members, id=self.bot.user.id), embed, action_row) #show rest of user info about bot
        

def setup(bot):
    bot.add_cog(Info(bot))