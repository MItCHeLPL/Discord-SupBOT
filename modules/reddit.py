import discord
from discord.ext import commands
import praw
import random
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

reddit = praw.Reddit(client_id=os.getenv('PRAW_CLIENT_ID'), client_secret=os.getenv('PRAW_CLIENT_SECRET'), user_agent=os.getenv('PRAW_USER_AGENT')) #initialize reddit


class Reddit(commands.Cog):
    """Posty z reddita"""
    def __init__(self, bot):
        self.bot = bot
    
    #Post submission from reddit
    def PostFromReddit(self, sub : str, ctx):
        post_to_pick = 2 #start post to pick     
        isRandom = self.bot.data["setting"]["reddit"]["pickRandom"] #true -> select random post, false -> sort from top hot
        limit = self.bot.data["setting"]["reddit"]["postToPickLimit"] #select this amount of posts from hot
        allowNSFW = self.bot.data["setting"]["reddit"]["allowNSFW"] #true -> can show nsfw posts if channel is set to nsfw, false -> doesn't show nsfw posts at all

        submissions = reddit.subreddit(sub).hot(limit=limit) #fetch posts

        if(isRandom):
            post_to_pick = random.randint(2, limit-1) #select random post number

        i=0 #post id
        for post in submissions:
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
        embed.colour = random.randint(0, 0xffffff) #random color
        embed.set_image(url=submission.url) #set image
        embed.title = submission.title #set title
        embed.url= "http://reddit.com" + submission.permalink
        embed.description = "[u/"+submission.author.name+"](http://reddit.com/u/"+submission.author.name+")"

        embed.timestamp = datetime.datetime.utcnow() #set time

        embed.set_author(name="r/+"+reddit.subreddit(sub).display_name, url="http://reddit.com/r/"+sub, icon_url=reddit.subreddit(sub).icon_img)
        
        #disable nsfw posts if channel is not set to nsfw
        if((submission.over_18 and allowNSFW == False) or (ctx.channel.is_nsfw() == False and submission.over_18)):
            embed=discord.Embed()
            embed.title = "Nie mogę tego tu wysłać"
            embed.description = "`Posty NSFW tylko na kanałach NSFW`"
            embed.timestamp = datetime.datetime.utcnow() #set time

        if self.bot.data["debug"]["reddit"]:
            print(f'[reddit][PostFromReddit]Generated post from reddit: {sub}\n')

        return embed


    @commands.command(name = 'subreddit', aliases = ['sub'])
    async def _sub(self, ctx, sub : str):
        """Wysyła losowy post z danego subreddita. (yo reddit [subreddit])"""
        embed = self.PostFromReddit(sub, ctx) #create embed

        await ctx.reply(embed=embed) #reply to user

    @commands.command(name = 'beaver', aliases = ['beavers'])
    async def _beaver(self, ctx):
        """Wysyła losowy post z r/beavers."""
        embed = self.PostFromReddit('beavers', ctx)

        await ctx.reply(embed=embed)

    @commands.command(name = 'meme', aliases = ['memes'])
    async def _meme(self, ctx):
        """Wysyła losowego mema z r/memes."""
        embed = self.PostFromReddit('memes', ctx)

        await ctx.reply(embed=embed)

    @commands.command(name = 'dankmeme', aliases = ['dankmemes', 'makemyday'])
    async def _sub(self, ctx):
        """Wysyła losowego mema z r/dankmemes."""
        embed = self.PostFromReddit('dankmemes', ctx)

        await ctx.reply(embed=embed)

def setup(bot):
    bot.add_cog(Reddit(bot))