import discord
from discord.ext import commands
import asyncpraw
import random
import os
from dotenv import load_dotenv
import datetime
from discord_slash import cog_ext, SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle

load_dotenv()

reddit = asyncpraw.Reddit(client_id=os.getenv('PRAW_CLIENT_ID'), client_secret=os.getenv('PRAW_CLIENT_SECRET'), user_agent=os.getenv('PRAW_USER_AGENT')) #initialize reddit


class Reddit(commands.Cog):
    """Posty z reddita"""
    def __init__(self, bot):
        self.bot = bot

        if self.bot.settings["debug"]["reddit"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][reddit]Loaded")
    

    #Post submission from reddit
    async def PostFromReddit(self, sub : str, ctx):
        post_to_pick = 2 #start post to pick     
        isRandom = self.bot.settings["setting"]["reddit"]["pickRandom"] #true -> select random post, false -> sort from top hot
        limit = self.bot.settings["setting"]["reddit"]["postToPickLimit"] #select this amount of posts from hot
        allowNSFW = self.bot.settings["setting"]["reddit"]["allowNSFW"] #true -> can show nsfw posts if channel is set to nsfw, false -> doesn't show nsfw posts at all

        subreddit = await reddit.subreddit(sub, fetch=True)

        if(isRandom):
            post_to_pick = random.randint(2, limit-1) #select random post number

        i=0 #post id
        async for post in subreddit.hot(limit=limit):
            if(i == post_to_pick): #if this is the submission to post
                if(post_to_pick == limit-1): #refresh post to pick if over limit
                    post_to_pick = 2
                    i = 0
                if(post.post_hint != 'image'): #take next submission if this isn't image
                    post_to_pick += 1
                    i += 1
                else:
                    submission = post #save submission

                    #select next post
                    if(isRandom):
                        post_to_pick = random.randint(2, limit-1) 
                    else:
                        post_to_pick += 1

                    break #finish browsing subreddit
            else:
                i += 1 #next post

        #embed
        embed=discord.Embed() #create new embed
        embed.colour = 0xfd4500 #reddit orange color
        embed.set_image(url=submission.url) #set image
        embed.title = submission.title #set title
        embed.url= "http://reddit.com" + submission.permalink
        embed.description = "[u/"+submission.author.name+"](http://reddit.com/u/"+submission.author.name+")"

        embed.timestamp = datetime.datetime.utcnow() #set timestamp

        embed.set_author(name="r/"+subreddit.display_name, url="http://reddit.com/r/"+sub, icon_url=subreddit.icon_img)

        #create buttons
        buttons = [
            create_button(
                style=ButtonStyle.URL,
                label=str(f"Post"),
                url=str("http://reddit.com" + submission.permalink)
            ),
            create_button(
                style=ButtonStyle.URL,
                label=str(f"u/{submission.author.name}"),
                url=str("http://reddit.com/u/"+submission.author.name)
            ),
            create_button(
                style=ButtonStyle.URL,
                label=str(f"r/{subreddit.display_name}"),
                url=str("http://reddit.com/r/"+sub)
            ),
        ]
        action_row = create_actionrow(*buttons)

        if self.bot.settings["debug"]["reddit"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][reddit][PostFromReddit]Generated post ({submission.url}) from reddit: {sub}')
        
        #disable nsfw posts if channel is not set to nsfw
        if(not isinstance(ctx.channel, discord.channel.DMChannel)):
            if((submission.over_18 and allowNSFW == False) or (ctx.channel.is_nsfw() == False and submission.over_18)):
                embed=discord.Embed()
                embed.title = "Nie mogę tego tu wysłać"
                embed.description = "`Posty NSFW tylko na kanałach NSFW lub w dm`"
                embed.timestamp = datetime.datetime.utcnow() #set time

                await ctx.send(embed=embed) #send information about nsfw posts

                if self.bot.settings["debug"]["reddit"]:
                    print(f'[{str(datetime.datetime.utcnow())[0:-7]}][reddit][PostFromReddit]Sent information about NSFW posts\n')

                return

        await ctx.send(embed=embed, components=[action_row]) #send post

        if self.bot.settings["debug"]["reddit"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][reddit][PostFromReddit]Sent reddit post\n')


    #normal commands
    @commands.command(name = 'subreddit',
        aliases = ['sub', 'reddit'], 
        brief = "Wysyła losowy post z danego subreddita (yo subreddit [subreddit])", 
        help = "Wysyła losowy post z podanego przez użytkownika subreddita. Posty NSFW wysyłane tylko na kanałach NSFW lub w wiadomościach prywatnych", 
        usage = "yo subreddit [subreddit]"
    )
    async def _sub(self, ctx, sub : str):
        if self.bot.settings["debug"]["reddit"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][reddit][_sub]{ctx.author.name} requested normal command')

        await self.PostFromReddit(sub, ctx)

    @commands.command(name = 'beaver',
        aliases = ['beavers'], 
        brief = "Wysyła losowy post z r/beavers", 
        help = "Wysyła losowy post z subreddita r/beavers. Posty NSFW wysyłane tylko na kanałach NSFW lub w wiadomościach prywatnych", 
        usage = "yo beaver"
    )
    async def _beaver(self, ctx):
        if self.bot.settings["debug"]["reddit"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][reddit][_beaver]{ctx.author.name} requested normal command')

        await self.PostFromReddit('beavers', ctx)

    @commands.command(name = 'meme',
        aliases = ['memes'], 
        brief = "Wysyła losowy post z r/memes", 
        help = "Wysyła losowy post z subreddita r/memes. Posty NSFW wysyłane tylko na kanałach NSFW lub w wiadomościach prywatnych", 
        usage = "yo meme"
    )
    async def _meme(self, ctx):
        if self.bot.settings["debug"]["reddit"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][reddit][_meme]{ctx.author.name} requested normal command')

        await self.PostFromReddit('memes', ctx)

    @commands.command(name = 'dankmeme',
        aliases = ['dankmemes', 'makemyday'], 
        brief = "Wysyła losowy post z r/dankmemes", 
        help = "Wysyła losowy post z subreddita r/dankmemes. Posty NSFW wysyłane tylko na kanałach NSFW lub w wiadomościach prywatnych", 
        usage = "yo dankmeme"
    )
    async def _dankmeme(self, ctx):
        if self.bot.settings["debug"]["reddit"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][reddit][_dankmeme]{ctx.author.name} requested normal command')

        await self.PostFromReddit('dankmemes', ctx)

    #slash command
    @cog_ext.cog_slash(name="reddit",
        description="Wysyła losowy post z danego subreddita",
        options=[
            create_option(
                name="subreddit",
                description="Wybierz subreddit",
                option_type=3,
                required=True
            )
        ]
    )
    async def _sub_slash(self, ctx:SlashContext, subreddit:str=None):
        if self.bot.settings["debug"]["reddit"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][reddit][_sub_slash]{ctx.author.name} requested slash command')

        await self.PostFromReddit(subreddit, ctx)


def setup(bot):
    bot.add_cog(Reddit(bot))