import discord
from discord.ext import commands
#from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component
#from discord_slash.model import ButtonStyle
import random
import datetime

class Poll(commands.Cog):
    """Ankieta"""
    def __init__(self, bot):
        self.bot = bot

    #old system for making polls based on reactions and limited to 10 fields
    @commands.command(name='ankieta', aliases=['poll', 'glosowanie', 'głosowanie'])
    async def _pollLegacy(self, ctx, option1 : str, *args):
        """Tworzy ankietę (max 10 pól) (yo ankieta [opcja1] [opcja2] ...)"""

        emojis = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']

        #create options tables
        options = []
        options.append(option1)

        #set text after space to options
        for option in args:
            options.append(str(option))

        embed=discord.Embed() #create new embed
        embed.colour = random.randint(0, 0xffffff) #random color
        embed.title = "Ankieta" #set title
        embed.timestamp = datetime.datetime.utcnow() #set time

        #generate embed fields
        i = 0 #option id
        for option in options:
            if i<10:
                embed.add_field(name=str(i) + '. ' + str(option), value='`0`', inline=True) #add option field
                i += 1
            else:
                break

        msg = await ctx.send(embed=embed)

        #add emojis
        for emoji in emojis:
            if i > 0: 
                await msg.add_reaction(emoji)
                i -= 1


    #update poll
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        message = reaction.message
        emoji_id = self.get_emoji_id(reaction.emoji)

        if message.embeds[0].title == "Ankieta" and user != self.bot.user: #detect that user reacted to poll

            new_embed = discord.Embed() #create new embed
            new_embed.title = "Ankieta" #set title

            for emb in message.embeds:
                new_embed.timestamp = emb.timestamp #set time
                new_embed.colour = emb.colour #set color

                i = 0 #opiton id
                for field in emb.fields:
                    if emoji_id == i:
                        new_embed.add_field(name=field.name, value='`'+(int(field.value[1:-1]) + 1)+'`', inline=True) #add +1 to option corresponing to selected reaction
                    else:
                        new_embed.add_field(name=field.name, value=field.value, inline=True) #rest of options
                    i+=1

            await message.edit(embed=new_embed) #update message


    #convert emoji to opiton id
    def get_emoji_id(self, emoji):
        return {
            '0️⃣': 0,
            '1️⃣': 1,
            '2️⃣': 2,
            '3️⃣': 3,
            '4️⃣': 4,
            '5️⃣': 5,
            '6️⃣': 6,
            '7️⃣': 7,
            '8️⃣': 8,
            '9️⃣': 9
        }.get(emoji, -1) 



#    #New system based on components, limited to 25 fileds, can't limit to one interaction per user
#    @commands.command(name='ankieta', aliases=['poll', 'glosowanie', 'głosowanie'])
#    async def _poll(self, ctx, option1 : str, *args):
#        """Tworzy ankietę (max 25 pól) (yo ankieta [opcja1] [opcja2] ...)"""
#        #create options tables
#        options = []
#        options.append(option1)
#
#        #set text after space to options
#        for option in args:
#            options.append(str(option))
#
#        #generate mebed
#        embed=discord.Embed() #create new embed
#        embed.colour = random.randint(0, 0xffffff) #random color
#        embed.title = "Ankieta" #set title
#        embed.timestamp = datetime.datetime.utcnow() #set time
#
#        #generate embed fields
#        i = 1 #option id
#        for option in options:
#            if i<=25:
#                embed.add_field(name=str(i) + '. ' + str(option), value='`0`', inline=True) #add option field
#                i += 1
#            else:
#                break
#
#        #generate buttons
#        action_rows = []
#        buttons = []
#
#        i = 1 #option id
#        for option in options:
#            if i<=25:
#
#                if i%5 == 0: #every fifth action row
#                    action_rows.append(create_actionrow(*buttons)) #add action row
#                    buttons = [] #reset buttons array every 5 buttons
#                    
#                buttons.append(create_button(style=ButtonStyle.green, label=str(i)), custom_id=str(i)) #add button
#                i += 1
#
#            else:
#                break
#
#        await ctx.send(embed=embed, components=action_rows) #post poll
#
#
#    #onclick
#    @slash.component_callback()
#    async def vote(ctx: ComponentContext):
#        pressed_button = int(ctx.custom_id)
#
#        new_embed = discord.Embed() #create new embed
#        new_embed.title = "Ankieta" #set title
#
#        for emb in ctx.origin_message.embeds:
#            new_embed.timestamp = emb.timestamp #set time
#            new_embed.colour = emb.colour #set color
#
#            i = 1 #opiton id
#            for field in emb.fields:
#                if pressed_button == i:
#                    new_embed.add_field(name=field.name, value='`'+(int(field.value[1:-1]) + 1)+'`', inline=True) #add +1 to option corresponing to selected button
#                else:
#                    new_embed.add_field(name=field.name, value=field.value, inline=True) #rest of options
#                i+=1
#
#        await ctx.edit_origin(embed=new_embed)


def setup(bot):
    bot.add_cog(Poll(bot))