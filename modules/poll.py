import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord_slash import cog_ext, SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_select, create_select_option, create_button, create_actionrow
from discord_slash.model import ButtonStyle
import random
import datetime

class Poll(commands.Cog):
    """Ankieta"""
    def __init__(self, bot):
        self.bot = bot

        if self.bot.settings["debug"]["poll"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][poll]Loaded")


    #old system for making polls based on reactions and limited to 10 fields
    async def _poll_reaction(self, ctx, options):
        emojis = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']

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

        if self.bot.settings["debug"]["poll"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][poll][_poll_reaction]Generated poll message')

        #add react emojis
        for emoji in emojis:
            if i > 0: 
                await msg.add_reaction(emoji)
                i -= 1

        if self.bot.settings["debug"]["poll"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][poll][_poll_reaction]Added reactions to poll message\n')

    #normal command
    @commands.command(name = 'ankieta',
        aliases = ['poll', 'glosowanie', 'głosowanie'], 
        brief = "Tworzy ankietę (max 10 pól) (yo ankieta [opcja1] [opcja2] ...)", 
        help = "Tworzy ankietę, w której każdy może zagłosować za pomocą reakcji. Max 10 pól na ankietę", 
        usage = "yo ankieta [opcja1] [opcja2] [...]"
    )
    async def _poll_command(self, ctx, option0 : str, *args):
        if self.bot.settings["debug"]["poll"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][poll][_poll_command]{ctx.author.name} requested normal command')

        #add options to array and pass it to generate poll
        options = []
        options.append(option0)

        #set text after space to options
        for option in args:
            options.append(str(option))    

        await self._poll_reaction(ctx, options)
        #await self._poll_component(ctx, options)

    #slash command
    #current implementation on discord_slash requires each option to have separate argument
    @cog_ext.cog_slash(name="ankieta", 
        description="Tworzy ankietę, w której każdy może zagłosować za pomocą reakcji. Max 10 pól na ankietę", 
        options=[
            create_option(
                name="option_0", 
                description="Podaj opcję #0", 
                option_type=3, 
                required=True
            ),
            create_option(
                name="option_1", 
                description="Podaj opcję #1", 
                option_type=3, 
                required=False
            ),
            create_option(
                name="option_2", 
                description="Podaj opcję #2", 
                option_type=3, 
                required=False
            ),
            create_option(
                name="option_3", 
                description="Podaj opcję #3", 
                option_type=3, 
                required=False
            ),
            create_option(
                name="option_4", 
                description="Podaj opcję #4", 
                option_type=3, 
                required=False
            ),
            create_option(
                name="option_5", 
                description="Podaj opcję #5", 
                option_type=3, 
                required=False
            ),
            create_option(
                name="option_6", 
                description="Podaj opcję #6", 
                option_type=3, 
                required=False
            ),
            create_option(
                name="option_7", 
                description="Podaj opcję #7", 
                option_type=3, 
                required=False
            ),
            create_option(
                name="option_8", 
                description="Podaj opcję #8", 
                option_type=3, 
                required=False
            ),
            create_option(
                name="option_9", 
                description="Podaj opcję #9", 
                option_type=3, 
                required=False
            )
        ]
    )
    async def _poll_slash(self, ctx:SlashContext, 
        option_0 : str, 
        option_1 : str = None, 
        option_2 : str = None, 
        option_3 : str = None, 
        option_4 : str = None, 
        option_5 : str = None, 
        option_6 : str = None, 
        option_7 : str = None, 
        option_8 : str = None, 
        option_9 : str = None
    ):
        if self.bot.settings["debug"]["poll"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][poll][_poll_slash]{ctx.author.name} requested slash command')

        #add options to array
        options = [option_0, option_1, option_2, option_3, option_4, option_5, option_6, option_7, option_8, option_9]

        #remove empty options from array
        options = [i for i in options if i]

        await self._poll_reaction(ctx, options)
        #await self._poll_component(ctx, options)


    #update poll
    @commands.Cog.listener()
    @has_permissions(manage_messages=True)
    async def on_reaction_add(self, reaction, user):
        message = reaction.message
        emoji_id = self.emoji_to_id(reaction.emoji)

        if message.embeds != []:
            if message.embeds[0].title == "Ankieta" and user != self.bot.user and emoji_id != -1: #detect that user reacted to poll

                new_embed = discord.Embed() #create new embed
                new_embed.title = "Ankieta" #set title

                for emb in message.embeds:
                    new_embed.timestamp = emb.timestamp #set time of old embed
                    new_embed.colour = emb.colour #set color of old embed

                    i = 0 #option id
                    for field in emb.fields:
                        if emoji_id == i:
                            new_embed.add_field(name=field.name, value='`'+str(int(field.value[1:-1]) + 1)+'`', inline=True) #add +1 to option corresponding to selected reaction
                        else:
                            new_embed.add_field(name=field.name, value=field.value, inline=True) #rest of options
                        i+=1

                await message.edit(embed=new_embed) #update message

                if self.bot.settings["debug"]["poll"]:
                    print(f'[{str(datetime.datetime.utcnow())[0:-7]}][poll][on_reaction_add]Updated poll with vote on {emoji_id}\n')


    @commands.Cog.listener()
    @has_permissions(manage_messages=True)
    async def on_reaction_remove(self, reaction, user):
        message = reaction.message
        emoji_id = self.emoji_to_id(reaction.emoji)

        if message.embeds != []:
            if message.embeds[0].title == "Ankieta" and user != self.bot.user and emoji_id != -1: #detect that user reacted to poll

                new_embed = discord.Embed() #create new embed
                new_embed.title = "Ankieta" #set title
                for emb in message.embeds:
                    new_embed.timestamp = emb.timestamp #set time of old embed
                    new_embed.colour = emb.colour #set color of old embed
                    i = 0 #option id

                    for field in emb.fields:
                        if emoji_id == i:
                            new_embed.add_field(name=field.name, value='`'+str(int(field.value[1:-1]) - 1)+'`', inline=True) #add +1 to option corresponsing to selected reaction
                        else:
                            new_embed.add_field(name=field.name, value=field.value, inline=True) #rest of options
                        i+=1

                await message.edit(embed=new_embed) #update message

                if self.bot.settings["debug"]["poll"]:
                    print(f'[{str(datetime.datetime.utcnow())[0:-7]}][poll][on_reaction_remove]Updated poll with vote on {emoji_id}\n')


    #convert emoji to option id
    def emoji_to_id(self, emoji):
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



    #New system based on components, limited to 25 fields, can't limit to one interaction per user yet
    async def _poll_component(self, ctx, options):
        #generate embed
        embed=discord.Embed() #create new embed
        embed.colour = random.randint(0, 0xffffff) #random color
        embed.title = "Ankieta" #set title
        embed.timestamp = datetime.datetime.utcnow() #set time

        #generate embed fields
        i = 1 #option id
        for option in options:
            if i<=25:
                embed.add_field(name=str(i) + '. ' + str(option), value='`0`', inline=True) #add option field
                i += 1
            else:
                break

        action_rows = []

        #generate buttons
        buttons = []

        i:int = 1 #option id
        for option in options:
            if i<=25:

                label = str(option).strip() if len(str(option).strip()) < 80 else str(i) #max characters in label = 80
                buttons.append(create_button(style=ButtonStyle.primary, label=label, custom_id=str(i)),) #add button

                if i%5 == 0 or i==len(options): #every fifth action row + rest of options
                    action_rows.append(create_actionrow(*buttons)) #add action row
                    buttons = [] #reset buttons array every 5 buttons

                i += 1

            else:
                break

        #generate select
        #select_options = []
        #
        #i : int = 1 #option id
        #for option in options:
        #    if i<=25: #max 25 options in select
        #        description = str(option).strip() if len(str(option).strip()) < 50 else str(i) #max #characters in description = 50
#
        #        select_options.append(create_select_option(label = str(i), value = str(i), description = #description),) #add option to select
#
        #        i += 1
#
        #    else:
        #        break
#
        #select = create_select(
        #    options=select_options,
        #    placeholder="Oddaj swój głos", #the placeholder text to show when no options have been chosen
        #    min_values=1, #the minimum number of options a user must select
        #    max_values=1, #the maximum number of options a user can select
        #)
#
        #action_rows.append(create_actionrow(select))

        await ctx.send(embed=embed, components=action_rows) #post poll

        if self.bot.settings["debug"]["poll"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][poll][_poll_component]Generated poll message')


    #button OnClick
    @commands.Cog.listener()
    @has_permissions(manage_messages=True)
    async def on_component(self, ctx: ComponentContext):
        pressed_button = int(ctx.custom_id)

        new_embed = discord.Embed() #create new embed
        new_embed.title = "Ankieta" #set title

        for emb in ctx.origin_message.embeds:
            new_embed.timestamp = emb.timestamp #set time from old embed
            new_embed.colour = emb.colour #set color from old embed

            i = 1 #option id
            for field in emb.fields:
                if pressed_button == i:
                    new_embed.add_field(name=field.name, value='`'+str(int(field.value[1:-1]) + 1)+'`',     inline=True) #add +1 to option corresponding to selected button
                else:
                    new_embed.add_field(name=field.name, value=field.value, inline=True) #rest of options
                i+=1

        await ctx.edit_origin(embed=new_embed)

        if self.bot.settings["debug"]["poll"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][poll][_vote_component]Updated poll with vote on number {pressed_button}\n')


    #select OnSelect
    #@commands.Cog.listener()
    #@has_permissions(manage_messages=True)
    #async def on_component(self, ctx: ComponentContext):
    #    selection = int(ctx.selected_options[0]) #selection value
#
    #    new_embed = discord.Embed() #create new embed
    #    new_embed.title = "Ankieta" #set title
#
    #    for emb in ctx.origin_message.embeds:
    #        new_embed.timestamp = emb.timestamp #set time from old embed
    #        new_embed.colour = emb.colour #set color from old embed
#
    #        i = 1 #option id
    #        for field in emb.fields:
    #            if selection == i:
    #                new_embed.add_field(name=field.name, value='`'+str(int(field.value[1:-1]) + 1)+'`', #inline=True) #add +1 to option corresponding to selected button
    #            else:
    #                new_embed.add_field(name=field.name, value=field.value, inline=True) #rest of options
    #            i+=1
#
    #    await ctx.edit_origin(embed=new_embed)
#
    #    if self.bot.settings["debug"]["poll"]:
    #        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][poll][_vote_component]Updated poll with vote on number {selection}\n')


def setup(bot):
    bot.add_cog(Poll(bot))