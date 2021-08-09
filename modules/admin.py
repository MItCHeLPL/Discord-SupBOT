import discord
from discord.ext import commands
import datetime
import random
import math
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import SlashCommandPermissionType
import json


def Get_slash_admin_permissions():
    #load settings to create admin slash permissions before slash commands are loaded
    #load admins ids from settings.json
    with open('settings.json') as file:
        settings = json.load(file)
    #load connected guilds from data.json
    with open('data.json') as file:
        data = json.load(file)

    slash_admin_permissions = {}

    #cycle through connected guilds
    for guild in data["connected_guilds"]:
            
        guild_permissions = []

        #for every guild create permission for each admin to use admin commadns
        for id in settings["setting"]["admin"]["admin_ids"]:
            guild_permissions.append(create_permission(int(id), SlashCommandPermissionType.USER, True))

        #save permissions for this guild
        slash_admin_permissions[int(guild)] = guild_permissions

    #if settings["debug"]["admin"]:
        #print(f"[{str(datetime.datetime.utcnow())[0:-7]}][admin][Get_slash_admin_permissions]Created slash admin permissions")
    
    return slash_admin_permissions


class Admin(commands.Cog):
    """Admin-only"""

    global slash_admin_permissions #create global variable to save slash commands
    slash_admin_permissions = Get_slash_admin_permissions() #get settings

    def __init__(self, bot):
        self.bot = bot

        #make global bot variable for admin check
        global globbot
        globbot = self.bot

        if self.bot.settings["debug"]["admin"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][admin]Loaded")


    #check if sender is admin
    def is_admin(ctx):
        return (str(ctx.author.id) in globbot.settings["setting"]["admin"]["admin_ids"])


    #allows admin to write as bot on every text channel
    async def _say(self, ctx, channel_id, userText : str):
        #find text channel in bots guilds
        for guild in ctx.bot.guilds:
            for channel in guild.channels:
                if str(channel.id) == channel_id:

                    await channel.send(userText) #send text

                    if isinstance(ctx, SlashContext): #slash command
                        await ctx.send("Wysłano wiadomość na wskazany kanał tekstowy", hidden=True)
                    else: #normal command
                        await ctx.reply("Wysłano wiadomość na wskazany kanał tekstowy", delete_after=10)

                    if self.bot.settings["debug"]["admin"]:
                        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][admin][_say]Admin ({str(ctx.author.name)}) sent {userText} on channel {channel.name}\n')

    #normal command
    @commands.command(name = 'say',
        aliases = ['sayadmin', 'ownersay', 'sayowner', 'admin_say', 'say_admin', 'owner_say', 'say_owner', 'adminsay'], 
        brief = "Wypisz tekst na dowolnym kanale (yo say [id_kanału] [tekst])", 
        help = "Będąc adminem tego bota możesz wypisać dowolną wiadomość na dowolnym serwerze, na którym jest ten bot", 
        usage = "yo say [id_kanału] [tekst]"
    )
    @commands.check(is_admin)
    async def _say_command(self, ctx, channel_id, text : str, *args):
        #combine text to one string
        spaceText = ""
        for txt in args:
            spaceText += (" " + str(txt))
        text += spaceText

        if self.bot.settings["debug"]["admin"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][admin][_say_command]{ctx.author.name} requested normal command')

        await self._say(ctx, channel_id, text)

    #slash command
    @cog_ext.cog_slash(name="say", 
        description="Wyślij wiadomość na dowolnym kanale", 
        options=[
            create_option(
                name="channel_id", 
                description="Podaj id kanału tekstowego", 
                option_type=3, 
                required=True
            ),
            create_option(
                name="text", 
                description="Podaj tekst wiadomości", 
                option_type=3, 
                required=True
            )
        ],
        default_permission = False,
        permissions = slash_admin_permissions
    )
    async def _say_slash(self, ctx:SlashContext, channel_id, text : str):
        if self.bot.settings["debug"]["admin"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][admin][_say_slash]{ctx.author.name} requested slash command')

        await self._say(ctx, channel_id, text)


    #allows admin to see bot's output log in dms
    async def _log(self, ctx):
        #read output file
        with open("output.log") as file:
            log = file.read()
        
        if log != None:
            txt = log[log.rfind("[main][__main__]--------SETUP STARTED--------"):] #find newest log header

            #4096 - limit of characters in embed description
            #split log into chunks of 4096 characters and send them as separate embeds
            for x in range(0, math.ceil(len(txt)/4096)):
                embed=discord.Embed() #create embed
                embed.colour = random.randint(0, 0xffffff) #set random color to embed
                embed.title = f'Dziennik zdarzeń ({x+1}/{str(math.ceil(len(txt)/4096))})' #set title
                embed.timestamp = datetime.datetime.utcnow() #set timestamp

                embed.description = txt[x*4096:(x+1)*4096] #type chunk of 4096 characters into embed

                await ctx.author.send(embed=embed) #send embed

            if isinstance(ctx, SlashContext): #slash command
                await ctx.send("Wysłano dziennik zdarzeń w dm", hidden=True)
            else: #normal command
                await ctx.reply("Wysłano dziennik zdarzeń w dm", delete_after=10)

            if self.bot.settings["debug"]["admin"]:
                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][admin][_log]Sent debug log to {str(ctx.author.name)}\n')

    #normal command
    @commands.command(name = 'showeventlog',
        aliases = ['showoutput', 'log', 'botlog', 'printlog', 'logprint', 'adminlog', 'adminoutput', 'dziennik', 'zdarzenia', 'showlog'], 
        brief = "Wysyła dziennik zdarzeń bota w wiadomości prywatnej", 
        help = "Będąc adminem tego bota możesz zobaczyć dziennik zdarzeń SupBOT w wiadomości prywatnej od niego", 
        usage = "yo showeventlog"
    )
    @commands.check(is_admin)
    async def _log_command(self, ctx):
        if self.bot.settings["debug"]["admin"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][admin][_log_command]{ctx.author.name} requested normal command')

        await self._log(ctx)

    #slash command
    @cog_ext.cog_slash(name="showeventlog", 
        description="Wysyła dziennik zdarzeń bota w wiadomości prywatnej",
        default_permission = False,
        permissions = slash_admin_permissions
    )
    async def _log_slash(self, ctx:SlashContext):
        if self.bot.settings["debug"]["admin"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][admin][_log_slash]{ctx.author.name} requested slash command')

        await self._log(ctx)


    #allows admin to send dm to any user as a bot
    async def _dmuser(self, ctx, user : discord.Member, text : str):
        if(user != None):
            if text != None:
                await user.send(text) #send text to user

                if isinstance(ctx, SlashContext): #slash command
                    await ctx.send("Wysłano dm do " + str(user.mention) + ".", hidden=True)
                else: #normal command
                    await ctx.reply("Wysłano dm do " + str(user.mention) + ".", delete_after=10)

                if self.bot.settings["debug"]["other"]:
                    print(f'[{str(datetime.datetime.utcnow())[0:-7]}][admin][_dmuser]Sent DM to {user.name}, text: {text}\n')
        else: #didnt found user
            if isinstance(ctx, SlashContext): #slash command
                await ctx.send("Nie znaleziono użytkownika", hidden=True)
            else: #normal command
                await ctx.reply("Nie znaleziono użytkownika", delete_after=5)

            if self.bot.settings["debug"]["other"]:
                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][admin][_dmuser]Didnt find user to sent DM to\n')

    #normal command
    @commands.command(name = 'dmuser',
        aliases = ['dm', 'pm', 'priv', 'admindmuser', 'dmadmin', 'pmadmin', 'adminpm', 'admindm', 'dmuseradmin', 'privadmin', 'adminpriv'], 
        brief = "Napisz prywatną wiadomość do dowolnego użytkownika (yo dmuser [@użytkownik] [tekst])", 
        help = "Będąc adminem tego bota możesz napisz prywatną wiadomość do dowolnego użytkownika, którego widzi ten bot", 
        usage = "yo dmuser [@użytkownik] [tekst]"
    )
    @commands.check(is_admin)
    async def _dmuser_command(self, ctx, user : discord.Member, text : str, *args):
        #combine text into one string
        spaceText = ""
        for txt in args:
            spaceText += (" " + str(txt))
        text += spaceText

        if self.bot.settings["debug"]["admin"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][admin][_dmuser_command]{ctx.author.name} requested normal command')

        await self._dmuser(ctx, user, text)

    #slash command
    @cog_ext.cog_slash(name="dmuser", 
        description="Wysyła prywatną wiadomość do dowolnego użytkownika", 
        options=[
            create_option(
                name="user", 
                description="Podaj @użytkownika", 
                option_type=6, 
                required=True
            ),
            create_option(
                name="text", 
                description="Podaj tekst wiadomości", 
                option_type=3, 
                required=True
            )
        ],
        default_permission = False,
        permissions = slash_admin_permissions
    )
    async def _dmuser_slash(self, ctx:SlashContext, user : discord.Member, text : str):
        if self.bot.settings["debug"]["admin"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][admin][_dmuser_slash]{ctx.author.name} requested slash command')

        await self._dmuser(ctx, user, text)


    #user isn't admin and used normal command
    @_say_command.error
    @_log_command.error
    @_dmuser_command.error
    async def _error(self, ctx, error):
        await ctx.reply('Nie masz uprawnień do tej komendy', delete_after=10)

        if self.bot.settings["debug"]["admin"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][admin][_error]{ctx.author.name} doesnt have permission to use admin command\n')

    #user isn't admin and used slash command
    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx: SlashContext, error):
        if isinstance(error, commands.errors.MissingPermissions) or isinstance(error, commands.errors.CheckFailure):
            await ctx.send("Nie masz uprawnień do tej komendy", hidden=True)

            if self.bot.settings["debug"]["admin"]:
                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][admin][on_slash_command_error]{ctx.author.name} doesnt have permission to use admin command\n')


def setup(bot):
    bot.add_cog(Admin(bot))