import os
import praw #reddit
import random
import math
import discord
from dotenv import load_dotenv #loading tokens
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import CommandNotFound
from discord.ext.commands import MemberConverter

#Bot initialization ----------------------------------------------------------
load_dotenv() #read from .env file
TOKEN = os.getenv('DISCORD_TOKEN') #load token

intents = discord.Intents().all() #makes reading userlist possible

#prefix yo [command]
bot = commands.Bot(command_prefix='yo ', description='''yo [komenda] [atrybut1] [atrybut2]...''', intents=intents)

client = discord.Client()

#reddit ----------------------------------------------------------------------
#reddit initialization
reddit = praw.Reddit(client_id=os.getenv('PRAW_CLIENT_ID'), client_secret=os.getenv('PRAW_CLIENT_SECRET'), user_agent='BBSCH BOT')

#post to pick
post_to_pick = 2

#Post submission from reddit
def PostFromReddit(sub : str, ctx):
    global post_to_pick
    isRandom = True #select random post or sort from top hot
    limit = 50 #select this amount of posts from hot
    allowNSFW = True #can show nsfw posts if channel is set to nsfw

    submissions = reddit.subreddit(sub).hot(limit=limit) #fetch posts

    if(isRandom):
        post_to_pick = random.randint(2, limit-1) #select random number

    i=0 #start from 0
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

    embed=discord.Embed() #create new embed
    embed.colour = random.randint(0, 0xffffff) #random color
    embed.set_image(url=submission.url) #set image
    embed.title = submission.title #set title
    embed.description = "http://reddit.com" + submission.permalink #set link
       
    #disable nsfw posts if channel is not set to nsfw
    if((submission.over_18 and allowNSFW == False) or (ctx.channel.is_nsfw() == False and submission.over_18)):
        embed.set_image(url="")
        embed.title = "Nie mogę tego tu wysłać"
        embed.description = "Posty NSFW tylko na kanałach NSFW."

    return embed

#bot events------------------------------------------------
#on bot start show this in console
@bot.event
async def on_ready():
    print('Starting...')
    print('\nName: ')
    print(bot.user.name)
    print('\nUser ID: ')
    print(bot.user.id)
    print('\nStarted.')

    #Listening to: "yo help" rich presence
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = 'yo help'))

#on messages with 'yo'
@bot.event
async def on_message(message):
    if (message.content == "yo" and message.author.bot == False):
        await message.channel.send("yo") #if somebody says yo

    if (message.content.startswith('yo') and message.author.bot == False):
        await message.add_reaction('✅') #if message starts with yo

    if(message.is_system() and message.system_content.find("pinned") == -1):
        await message.channel.send("Yo") #when new user joins server

    await bot.process_commands(message) #else

#on command not found
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.message.remove_reaction('✅', bot.user)
        await ctx.message.add_reaction('❌')
        await ctx.send('Yo, nie rozumiem,\nWpisz "**yo help**" i przestań mi bota prześladować')

#on somebody is kicked from server run kick counter
@bot.event
async def on_member_remove(member):
    ctx = member.guild.system_channel
    await kickinfo(ctx, member)

#on somebody is banned from server run ban counter
@bot.event
async def on_member_ban(guild, user):
    ctx = guild.system_channel
    await baninfo(ctx, user)

#Bot commands----------------------------------------
#sup
@bot.command()
async def sup(ctx):
    """Pytasz bota co tam u niego."""
    await ctx.send("nm u?")

#nm
@bot.command()
async def nm(ctx):
    """Reakcja bota na to że nic ciekawego się u ciebie nie dzieje."""
    await ctx.send("cool.")

#wiek
@bot.command()
async def wiek(ctx, wiek : int):
    """Czy możesz rzucać kartę dla takiego wieku? (yo wiek liczba)"""
    wynik = (wiek/2) + 7
    await ctx.send("Yo, " + str(wynik) + " i rzucasz kartę byniu.")

#send dm to user
@bot.command()
async def dmuser(ctx, user : discord.Member, text : str):
    """Pisze dm do użytkownika. (yo dmuser @użytkownik tekst)"""

    await user.send('\nYo,\n' + text)
    await ctx.send("Yo, wysłano dm do " + str(user.mention) + ".")

#send dm to Szary
#@bot.command()
#async def dmszary(ctx, text : str):
#    """Pisze dm do szarego. (yo dmszary tekst)"""
#
#    user = bot.get_user(os.getenv('DISCORD_ID_SZARY')) #Szary ID
#    await user.send('\nYo,\n' + text)
#    await ctx.send("Yo, wysłano dm do Szarego.")

#picks random person from voicechannel you are in
@bot.command()
async def impostor(ctx):
    """Kto z kanału jest impostorem"""

    channel = discord.utils.get(ctx.guild.voice_channels,  name=ctx.message.author.voice.channel.name) #get voice channel that caller is in

    member_ids = list(channel.voice_states.keys()) #list of user ids

    pickedUserId = random.randint(0, len(member_ids)-1) #random user from list

    user = await bot.fetch_user(member_ids[pickedUserId]) #id to user
    
    await ctx.send("Yo, " + str(user.mention) + " jest impostorem.")

#ban counter
#get entries from audit log about said user and count ban entries
@bot.command()
async def baninfo(ctx, user : discord.Member):
    """Ile razy dany użytkownik został zbanowany (yo baninfo @użytkownik)"""

    entries = []

    async for x in ctx.guild.audit_logs(before=None, after=None, oldest_first=None, action=discord.AuditLogAction.ban):
        if(x.target == user):
            entries.append(x)

    await ctx.send("Yo, " + str(user.mention) + " został zbanowany " + str(len(entries)) + " razy.")

#kick counter
#get entries from audit log about said user and count kick entries
@bot.command()
async def kickinfo(ctx, user : discord.Member):
    """Ile razy dany użytkownik został zkickowany (yo kickinfo @użytkownik)"""

    entries = []

    async for x in ctx.guild.audit_logs(before=None, after=None, oldest_first=None, action=discord.AuditLogAction.kick):
        if(x.target == user):
            entries.append(x)

    await ctx.send("Yo, " + str(user.mention) + " został zkickowany " + str(len(entries)) + " razy.")

#vote kick---------------------------------------------------------------
#TODO IMPROVE
kickArray = {} #global array
@bot.command()
async def votekick(ctx, user : discord.Member):
    """Głosowanie na rozłączenie użytkownika z kanału. (yo votekick @użytkownik)"""

    global kickArray

    canceled = False

    channel = discord.utils.get(ctx.guild.voice_channels,  name=ctx.message.author.voice.channel.name) #get voice channel that caller is in

    member_ids = list(channel.voice_states.keys()) #list of user ids

    usercount = len(member_ids) #how many users are in the voice channel

    if(ctx.message.author.voice.channel.id == user.voice.channel.id):#if user and target are on the same channel
        if(user not in kickArray):#initial user add
            kickArray[user] = {}
            kickArray[user]["votes"] = 1
            kickArray[user]["callers"] = [ctx.message.author]  
            kickArray[user]["usercount"] = usercount
        else: #user is already in array
            if(usercount != kickArray[user]["usercount"] and kickArray[user]["usercount"] != None): #clears array of user when number of people changes
                kickArray.clear()
                canceled = True
                await ctx.send("Yo, Zmieniła się liczba użytkowników na kanale, rozpoczęto nowe głosowanie.")
                await votekick(ctx, user) #add first vote
            else: #add vote
                if(ctx.message.author not in kickArray[user]['callers']):#adds new caller
                    kickArray[user]['votes'] += 1 
                    kickArray[user]['callers'].append(ctx.message.author)

    #output text
    text = "Votekick: " + str(user.mention) + " " + str(kickArray[user]['votes']) + "/"
    if((usercount/2) % 2 == 0 or usercount == 2): #if 2 users or 4,6...
        text += str(math.ceil(usercount/2) + 1)
    else:
        text += str(math.ceil(usercount/2)) #if 3,5... users

    #successful vote
    if(kickArray[user]['votes'] > usercount/2): #if more than 50% users on vc voted
        text += "\nWyrzucono: " + str(user.mention)
        kickArray.clear()
        await user.edit(voice_channel=None) #kick user from vc

    if(canceled == False):#avoid double message
        await ctx.send(text) #send output

#send submission from reddit--------------------------------------------------
#typed-in subreddit
@bot.command()
async def subreddit(ctx, sub : str):
    """Wysyła losowy post z danego subreddita. (yo reddit subreddit)"""

    embed = PostFromReddit(sub, ctx)

    await ctx.send(embed=embed)

#beavers
@bot.command()
async def beaver(ctx):
    """Wysyła losowy post z r/beavers."""

    embed = PostFromReddit("beavers", ctx)

    await ctx.send(embed=embed)

#memes
@bot.command()
async def meme(ctx):
    """Wysyła losowego mema z r/memes."""

    embed = PostFromReddit("memes", ctx)

    await ctx.send(embed=embed)

#dankmemes
@bot.command()
async def dankmeme(ctx):
    """Wysyła losowego mema z r/dankmemes."""

    embed = PostFromReddit("dankmemes", ctx)

    await ctx.send(embed=embed)

#dankmemes
@bot.command()
async def makemyday(ctx):
    """Wysyła losowego mema z r/dankmemes."""

    await dankmeme(ctx)

#stats -----------------------------------------------------------------------
@bot.command()
async def stats(ctx):
    """Pokazuje statystyki bota i serwera"""

    #Calculate online/offline members
    online = 0
    for user in ctx.guild.members:
        if user.status != discord.Status.offline:
            online += 1
    
    offline = ctx.guild.member_count - online

    #Calculate total kick amount
    kicks = 0
    async for x in ctx.guild.audit_logs(before=None, after=None, oldest_first=None, action=discord.AuditLogAction.kick):
        kicks += 1

    #Calculate total ban amount
    bans = 0
    async for x in ctx.guild.audit_logs(before=None, after=None, oldest_first=None, action=discord.AuditLogAction.ban):
        bans += 1

    #Calculate current ban amount
    bansnow = await ctx.guild.bans()

    #Output
    output = "Yo,"
    output += "\n__**Statystyki serwera:**__"
    output += "\n**➤Nazwa: **" + str(ctx.guild.name)
    output += "\n**➤Utworzono: **" + str(ctx.guild.created_at)[0:-7]
    output += "\n**➤Właściciel: **" + str(ctx.guild.owner.mention)
    
    output += "\n\n**➤Ilość użytkowników online: **" + str(online)
    output += "\n**➤Ilość użytkowników offline: **" + str(offline)
    output += "\n**➤Ilość użytkowników: **" + str(ctx.guild.member_count)

    output += "\n\n**➤Ilość kanałów tekstowych: **" + str(len(ctx.guild.text_channels))
    output += "\n**➤Ilość kanałów głosowych: **" + str(len(ctx.guild.voice_channels))

    output += "\n\n**➤Ilość ról: **" + str(len(ctx.guild.roles))

    output += "\n\n**➤Ilość banów aktualnie: **" + str(len(bansnow))
    output += "\n**➤Ilość banów razem: **" + str(bans)
    output += "\n**➤Ilość kicków razem: **" + str(kicks)

    output += "\n\n__**Statystyki bota:**__"
    output += "\n**➤Ilość serwerów na których jestem: **" + str(len(ctx.bot.guilds))
    output += "\n**➤Ping: **" + str(round(ctx.bot.latency * 100, 2)) + "ms"
    
    output += "\n\n__**Statystyki " + str(ctx.message.author.mention) + ":**__"
    output += "\n**➤Utworzono konto: **" + str(ctx.message.author.created_at)[0:-7]
    output += "\n**➤Dołączono do serwera: **" + str(ctx.message.author.joined_at)[0:-7]
    
    await ctx.send(output)


#Start bot --------------------------------------------------------------------
bot.run(TOKEN)