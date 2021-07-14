import discord
from discord.ext import commands

class VCVoteKick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.kickArray = {} #array of users to kick from vc

    @commands.command(name = 'votekick', aliases = ['wyrzuc', 'wyrzuć'])
    async def _votekick(self, ctx, user : discord.Member):
        canceled = False

        channel = discord.utils.get(ctx.guild.voice_channels,  name=ctx.message.author.voice.channel.name) #get voice channel that caller is in

        member_ids = list(channel.voice_states.keys()) #list of user ids

        usercount = len(member_ids) #how many users are in the voice channel

        #if bot on channel subtract from usercount
        for member_id in member_ids:
            if(member_id == self.bot.user.id):
                usercount = len(member_ids) - 1

        if(ctx.message.author.voice.channel.id == user.voice.channel.id):#if user and target are on the same channel
            if(user not in self.kickArray):#initial user add
                self.kickArray[user] = {}
                self.kickArray[user]["votes"] = 1
                self.kickArray[user]["callers"] = [ctx.message.author]  
                self.kickArray[user]["usercount"] = usercount
            else: #user is already in array
                if(usercount != self.kickArray[user]["usercount"] and self.kickArray[user]["usercount"] != None): #clears array of user when number of people changes
                    self.kickArray.clear()
                    canceled = True
                    await ctx.send("Yo, Zmieniła się liczba użytkowników na kanale, rozpoczęto nowe głosowanie.")
                    await self._votekick(ctx, user) #add first vote
                else: #add vote
                    if(ctx.message.author not in self.kickArray[user]['callers']):#adds new caller
                        self.kickArray[user]['votes'] += 1 
                        self.kickArray[user]['callers'].append(ctx.message.author)

        #output text
        text = "Votekick: " + str(user.mention) + " " + str(self.kickArray[user]['votes']) + "/"
        if((usercount/2) % 2 == 0 or usercount == 2): #if 2 users or 4,6...
            text += str(math.ceil(usercount/2) + 1)
        else:
            text += str(math.ceil(usercount/2)) #if 3,5... users

        #successful vote
        if(self.kickArray[user]['votes'] > usercount/2): #if more than 50% users on vc voted
            text += "\nWyrzucono: " + str(user.mention)
            self.kickArray.clear()
            await user.edit(voice_channel=None) #kick user from vc

        if(canceled == False):#avoid double message
            await ctx.reply(text) #send output

def setup(bot):
    bot.add_cog(VCVoteKick(bot))