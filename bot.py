import os
import praw
import random
import math
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import CommandNotFound
from discord.ext.commands import MemberConverter

#BOT initialization
load_dotenv()

TOKEN = 'NzczNjU5MzYxNDI3ODQ5MjE2.X6McbQ.vkdnsuYVL9OT1WCL1-kHmBF1Ec8'

intents = discord.Intents().all()

bot = commands.Bot(command_prefix='yo ', description='''yo [komenda] [atrybut]''', intents=intents)

client = discord.Client()

#reddit initializatiom
reddit = praw.Reddit(client_id='uJs1B-ZjKX4sgA', client_secret='Vwn0M6_x-6hsUn2kg4toyAElJMVAOQ', user_agent='BBSCH BOT')

#post to pick
post_to_pick = 1

#Take post from reddit
def PostFromReddit(sub : str, ctx):
    global post_to_pick
    isRandom = True #select random post or sort from top hot
    limit = 20 #select this amount of posts from hot
    allowNSFW = True #can show nsfw posts

    submissions = reddit.subreddit(sub).hot(limit=limit) #pick posts

    if(isRandom):
        post_to_pick = random.randint(1, limit-1) #select random post
    
    for i in range(0, post_to_pick):
        submission = next(x for x in submissions if not x.stickied) #select post based on value

    #iterate post to pick if not random
    if(isRandom == False):
        if(post_to_pick == 20):
            post_to_pick = 1
        else:
            post_to_pick += 1

    embed=discord.Embed()
    embed.colour = random.randint(0, 0xffffff)
    embed.set_image(url=submission.url)
    embed.title = submission.title
    embed.description = "http://reddit.com" + submission.permalink
       
    #disable nsfw posts
    if((submission.over_18 and allowNSFW == False) or (ctx.channel.is_nsfw() == False and submission.over_18)):
        embed.set_image(url="")
        embed.title = "Something went wrong"
        embed.description = "NSFW tylko na kanałach NSFW."

    return embed


@bot.event
async def on_ready():
    print('Starting as:')
    print(bot.user.name)
    print(bot.user.id)
    print('...')
    print('Started.')

    #rich presence
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = 'yo help'))

#on yo
@bot.event
async def on_message(message):
    if (message.content == "yo" and message.author.bot == False):
        await message.channel.send("yo") #if somebody says yo

    if (message.content.startswith('yo') and message.author.bot == False):
        await message.add_reaction('✅')

    if(message.is_system() and message.system_content.find("pinned") == -1):
        await message.channel.send("Yo") #when new user joins server

    await bot.process_commands(message) #else

#kick
@bot.event
async def on_member_remove(member):
    ctx = member.guild.text_channels[0]
    await kickinfo(ctx, member)

#ban
@bot.event
async def on_member_ban(guild, user):
    ctx = guild.text_channels[0]
    await baninfo(ctx, user)

#command not found
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.message.remove_reaction('✅', bot.user)
        await ctx.message.add_reaction('❌')
        await ctx.send('Yo, nie rozumiem,\nWpisz "**yo help**" i przestań mi bota prześladować')

#Bot commands
@bot.command()
async def sup(ctx):
    """Pytasz bota co tam u niego."""
    await ctx.send("nm u?")

@bot.command()
async def nm(ctx):
    """Reakcja bota na to że nic ciekawego się u ciebie nie dzieje."""
    await ctx.send("cool.")

@bot.command()
async def wiek(ctx, wiek : int):
    """Czy możesz rzucać kartę dla takiego wieku? (yo wiek liczba)"""
    wynik = (wiek/2) + 7
    await ctx.send("Yo, " + str(wynik) + " i rzucasz kartę byniu.")

@bot.command()
async def dmszary(ctx, text : str):
    """Pisze dm do szarego. (yo dmszary tekst)"""

    #user = bot.get_user(680816128045350933) #ID Szarego
    user = bot.get_user(ctx.message.author.id)
    await user.send('\nYo,\n' + text)
    await ctx.send("Yo, wysłano dm do Szarego.")

@bot.command()
async def impostor(ctx):
    """Kto z kanału jest impostorem"""

    channel = discord.utils.get(ctx.guild.voice_channels,  name=ctx.message.author.voice.channel.name) #get voice channel that caller is in

    member_ids = list(channel.voice_states.keys()) #list of user ids

    pickedUserId = random.randint(0, len(member_ids)-1) #random user from list

    user = await bot.fetch_user(member_ids[pickedUserId]) #id to user
    
    await ctx.send("Yo, " + str(user.mention) + " jest impostorem.")

#counter
@bot.command()
async def baninfo(ctx, user : discord.Member):
    """Ile razy dany użytkownik został zbanowany (yo baninfo @użytkownik)"""

    entries = []

    async for x in ctx.guild.audit_logs(limit=100, before=None, after=None, oldest_first=None, action=discord.AuditLogAction.ban):
        if(x.target == user):
            entries.append(x)

    await ctx.send("Yo, " + str(user.mention) + " został zbanowany " + str(len(entries)) + " razy.")

@bot.command()
async def kickinfo(ctx, user : discord.Member):
    """Ile razy dany użytkownik został zkickowany (yo kickinfo @użytkownik)"""

    entries = []

    async for x in ctx.guild.audit_logs(limit=100, before=None, after=None, oldest_first=None, action=discord.AuditLogAction.kick):
        if(x.target == user):
            entries.append(x)

    await ctx.send("Yo, " + str(user.mention) + " został zkickowany " + str(len(entries)) + " razy.")

#vote kick
kickArray = {} #global array
@bot.command()
async def votekick(ctx, user : discord.Member):
    """Głosowanie na rozłączenie użytkownika z kanału. (yo votekick @użytkownik)"""

    global kickArray

    cleared = False

    channel = discord.utils.get(ctx.guild.voice_channels,  name=ctx.message.author.voice.channel.name) #get voice channel that caller is in

    member_ids = list(channel.voice_states.keys()) #list of user ids

    usercount = len(member_ids) #how many users are in the voice channel

    if(ctx.message.author.voice.channel.name == user.voice.channel.name):#if user and target are on the same channel
        if(user not in kickArray):#initial user add
            kickArray[user] = {}
            kickArray[user]["votes"] = 1
            kickArray[user]["callers"] = [ctx.message.author]  
            kickArray[user]["usercount"] = usercount
        else:
            if(usercount != kickArray[user]["usercount"] and kickArray[user]["usercount"] != None):#clears array of user when number of people changes
                kickArray.clear()
                cleared = True
                await votekick(ctx, user)
            else:
                if(ctx.message.author not in kickArray[user]['callers']):#adds new user
                    kickArray[user]['votes'] += 1 
                    kickArray[user]['callers'].append(ctx.message.author)

    #output text
    text = "Votekick: " + str(user.mention) + " " + str(kickArray[user]['votes']) + "/"
    if(math.ceil(usercount/2) % 2 == 0 or usercount == 2):
        text += str(math.ceil(usercount/2) + 1)
    else:
        text += str(math.ceil(usercount/2))

    #succesful kick
    if(kickArray[user]['votes'] > usercount/2):
        text += "\nWyrzucono: " + str(user.mention)
        kickArray.clear()
        cleared = True
        await user.edit(voice_channel=None)

    if (cleared == false):
        await ctx.send(text)

#reddit
@bot.command()
async def meme(ctx):
    """Wysyła losowego mema z r/memes."""

    embed = PostFromReddit("memes", ctx)

    await ctx.send(embed=embed)

@bot.command()
async def dankmeme(ctx):
    """Wysyła losowego mema z r/dankmemes."""

    embed = PostFromReddit("dankmemes", ctx)

    await ctx.send(embed=embed)

@bot.command()
async def makemyday(ctx):
    """Wysyła losowego mema z r/dankmemes."""

    await dankmeme(ctx)

@bot.command()
async def beaver(ctx):
    """Wysyła losowy post z r/beavers."""

    embed = PostFromReddit("beavers", ctx)

    await ctx.send(embed=embed)

@bot.command()
async def subreddit(ctx, sub : str):
    """Wysyła losowy post z danego subreddita. (yo reddit subreddit)"""

    embed = PostFromReddit(sub, ctx)

    await ctx.send(embed=embed)

#Start bot
bot.run(TOKEN)