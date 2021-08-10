import discord
from discord.ext import commands
import math
import datetime
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

class VCVoteKick(commands.Cog):
    """Wyrzuć z kanału głosowego"""
    def __init__(self, bot):
        self.bot = bot
        self.kickArray = {} #array of users to kick from vc

        if self.bot.settings["debug"]["vc_votekick"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][vc_votekick]Loaded")


    async def _votekick(self, ctx, user : discord.Member):
        canceled = False

        channel = discord.utils.get(ctx.guild.voice_channels,  name=ctx.author.voice.channel.name) #get voice channel that caller is in

        member_ids = list(channel.voice_states.keys()) #list of user ids

        usercount = len(member_ids) #how many users are in the voice channel

        #if bot on channel subtract from usercount
        for member_id in member_ids:
            if(member_id == self.bot.user.id):
                usercount = len(member_ids) - 1

        if(ctx.author.voice.channel.id == user.voice.channel.id):#if user and target are on the same channel
            if(user not in self.kickArray):#initial user add
                self.kickArray[user] = {}
                self.kickArray[user]["votes"] = 1
                self.kickArray[user]["callers"] = [ctx.author]  
                self.kickArray[user]["usercount"] = usercount

            else: #user is already in array
                if(usercount != self.kickArray[user]["usercount"] and self.kickArray[user]["usercount"] != None): #clears array of user when number of people changes
                    self.kickArray.clear()

                    canceled = True

                    await ctx.send("Zmieniła się liczba użytkowników na kanale, rozpoczęto nowe głosowanie.", delete_after=10)

                    if self.bot.settings["debug"]["vc_votekick"]:
                        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_votekick][_votekick]Canceled vote on {user.name}\n')

                    await self._votekick(ctx, user) #add first vote

                    if self.bot.settings["debug"]["vc_votekick"]:
                        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_votekick][_votekick]New vote on {user.name}\n')

                else: #add vote
                    if(ctx.author not in self.kickArray[user]['callers']):#adds new caller
                        self.kickArray[user]['votes'] += 1 
                        self.kickArray[user]['callers'].append(ctx.author)

                        if self.bot.settings["debug"]["vc_votekick"]:
                            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_votekick][_votekick]{ctx.author.name} voted on {user.name}\n')

        else:
            if isinstance(ctx, SlashContext): #slash command
                await ctx.send("Nie ma takiego użytkownika na twoim kanale głosowym", hidden=True)
            else: #normal command
                await ctx.reply("Nie ma takiego użytkownika na twoim kanale głosowym", delete_after=5)

            if self.bot.settings["debug"]["vc_votekick"]:
                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_votekick][_votekick]No such user on vc\n')

        #output text
        text = "Głosowanie na wyrzucenie: " + str(user.mention) + " `" + str(self.kickArray[user]['votes']) + "/"
        if((usercount/2) % 2 == 0 or usercount == 2): #if 2 users or 4,6...
            text += str(math.ceil(usercount/2) + 1)+'`'
        else:
            text += str(math.ceil(usercount/2))+'`' #if 3,5... users

        #successful vote
        if(self.kickArray[user]['votes'] > usercount/2): #if more than 50% users on vc voted
            text += "\nWyrzucono: " + str(user.mention)
            self.kickArray.clear()
            await user.edit(voice_channel=None) #kick user from vc

            if self.bot.settings["debug"]["vc_votekick"]:
                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_votekick][_votekick]Kicked {user.name} from vc\n')

        if(canceled == False):#avoid double message
            if isinstance(ctx, SlashContext): #slash command
                await ctx.send(text)
            else: #normal command
                await ctx.reply(text)

    #normal command
    @commands.command(name = 'votekick',
        aliases = ['wyrzuc', 'wyrzuć', 'rozlacz', 'rozłącz'], 
        brief = "Zagłosuj na rozłączenie użytkownika z kanału głosowego (yo votekick [@użytkownik])", 
        help = "Zagłosuj na rozłączenie użytkownika z twojego kanału głosowego. Do rozłączenia potrzeba większości głosów", 
        usage = "yo votekick [@użytkownik]"
    )
    async def _votekick_command(self, ctx, user : discord.Member):
        if self.bot.settings["debug"]["vc_votekick"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_votekick][_votekick_command]{ctx.author.name} requested normal command')

        await self._votekick(ctx, user)

    #slash command
    @cog_ext.cog_slash(name="votekick", 
        description="Zagłosuj na rozłączenie użytkownika z kanału głosowego", 
        options=[
            create_option(
                name="user", 
                description="Użytkownik do rozłączenia", 
                option_type=6, 
                required=True
            )
        ]
    )
    async def _votekick_slash(self, ctx:SlashContext, user : discord.Member):
        if self.bot.settings["debug"]["vc_votekick"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][vc_votekick][_votekick_slash]{ctx.author.name} requested slash command')

        await self._votekick(ctx, user)


def setup(bot):
    bot.add_cog(VCVoteKick(bot))