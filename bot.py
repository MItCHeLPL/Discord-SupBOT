import os
import random
import math
import asyncio
import praw #reddit
import discord
import youtube_dl
from dotenv import load_dotenv #loading tokens
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import CommandNotFound
from discord.ext.commands import MemberConverter
from gtts import gTTS as gtts

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

#Sounds----------------------------------------------------------------------------------------
#arrays for sounds
global hellos
hellos = [11, 'mp3/yo.mp3', 'mp3VoiceLines/czesc.mp3', 'mp3VoiceLines/eloeloelo.mp3', 'mp3VoiceLines/hello_there.mp3', 'mp3VoiceLines/owitam.mp3', 'mp3VoiceLinesradczesc.mp3', 'mp3VoiceLines/radczesc.mp3', 'mp3VoiceLines/radczesc.mp3', 'mp3VoiceLines/siema.mp3', 'mp3VoiceLines/siemkaa.mp3', 'mp3VoiceLines/yczesc.mp3', 'jołsap', 'cześć', 'witam', 'dzień dobry'] #greetings list, first element is the last mp3
global goodbyes
goodbyes = [13, 'mp3/yo.mp3', 'mp3VoiceLines/czesc.mp3', 'mp3VoiceLines/eloeloelo.mp3', 'mp3VoiceLines/naura.mp3', 'mp3VoiceLines/radczesc.mp3', 'mp3VoiceLinesradczesc.mp3', 'mp3VoiceLines/radczesc.mp3', 'mp3VoiceLines/siema.mp3', 'mp3VoiceLines/siemkaa.mp3', 'mp3VoiceLines/yczesc.mp3', 'mp3VoiceLines/adios.mp3','mp3VoiceLines/gnight_girl_no_earrape.mp3', 'mp3VoiceLines/ja_spierdalam.mp3', 'joł', 'cześć', 'nara', 'do widzenia'] #goodbyes list, first element is the last mp3

#Play sound from array
def PlaySound(channel : discord.VoiceChannel, array):
    for server in bot.voice_clients: #cycle through all servers
        if(server.channel == channel): #connect

            vc = server #get voice channel

            voiceLineId = random.randint(1, (len(array)-1)) #random from greetings list

            #play yo audio
            if vc.is_playing() == False:

                if voiceLineId > array[0]: #if use tts   
                    message = gtts(array[voiceLineId], lang = 'pl', tld='pl')
                    message.save('mp3/tts.mp3')
                    vc.play(discord.FFmpegPCMAudio('mp3/tts.mp3'), after=lambda e: print('Player error: %s' % e) if e else None)

                else:#play normal bind
                    vc.play(discord.FFmpegPCMAudio(array[voiceLineId]), after=lambda e: print('Player error: %s' % e) if e else None)

            break       

#Channel editing--------------------------------------------------------------------------------
async def RefreshInfoChannels():
    for guild in bot.guilds:
        if(guild.id == 495666208939573248): #boberschlesien
                channel = discord.utils.get(guild.voice_channels, id=817042848490586152) #get info channel

                #Calculate online/all members
                online = 0
                for user in guild.members:
                    if user.status != discord.Status.offline:
                        online += 1
                
                total = guild.member_count

                await channel.edit(name='Online: ' + str(online) + '/' + str(total))

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

    print('\n Connected to:')
    for guild in bot.guilds:
        print(guild.name)

        if(guild.id == 495666208939573248): #boberschlesien
            channel = discord.utils.get(guild.voice_channels, id=615196854082207755) #get voice channel
            
            await channel.connect() #connect to channel

            PlaySound(channel, hellos) #play hello sound

        elif(guild.id == 536251306994827285): #scamelot
            channel = discord.utils.get(guild.voice_channels, id=788503046685458502) #get voice channel

            await channel.connect() #connect to channel

            PlaySound(channel, hellos) #play hello sound

    await RefreshInfoChannels() #refresh info channel


#on messages with 'yo'
@bot.event
async def on_message(message):
    if (message.content == "yo" and message.author.bot == False):
        await message.reply("yo") #if somebody says yo

    if (message.content.startswith('yo') and message.author.bot == False):
        await message.add_reaction('✅') #if message starts with yo

    await bot.process_commands(message) #else

#on command not found
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.message.remove_reaction('✅', bot.user)
        await ctx.message.add_reaction('❌')
        await ctx.reply('Yo, nie rozumiem,\nWpisz "**yo help**" i przestań mi bota prześladować')

#when somebody joins server
@bot.event
async def on_member_join(member): 
    ctx = member.guild.system_channel #server messages channel

    await ctx.send('Yo, witamy na serwerze ' + str(member.guild.name) + ', ' + str(member.mention)) #send hello message

    if(member.guild.id == 495666208939573248): #if on boberschlesien
        rank = discord.utils.get(member.guild.roles, id=503297149698572302) #Bot get guild(server) dj role
        await member.add_roles(rank) #add role

    await RefreshInfoChannels() #refresh info channel

#on somebody is kicked from server run kick counter
@bot.event
async def on_member_remove(member):
    ctx = member.guild.system_channel

    await ctx.send(str(member.mention) + ' opuścił serwer.')

    await kickinfo(ctx, member)

    await RefreshInfoChannels() #refresh info channel

#on somebody is banned from server run ban counter
@bot.event
async def on_member_ban(guild, user):
    ctx = guild.system_channel

    await ctx.send(str(user.name) + ' został zbanowany z serwera.')

    await baninfo(ctx, user)

#when somebody goes online etc.
@bot.event
async def on_member_update(before, after):
    await RefreshInfoChannels() #refresh info channel

#on something changes on bots vc
@bot.event
async def on_voice_state_update(member, before, after):
    if(bot.voice_clients != [] and member.id != bot.user.id): #if bot is in the same voice channel

        #ignore bools
        smute = ((before.self_mute == False and after.self_mute == True) or (before.self_mute == True and after.self_mute == False))
        mute = ((before.mute == False and after.mute == True) or (before.mute == True and after.mute == False))
        sdeaf = ((before.self_deaf == False and after.self_deaf == True) or (before.self_deaf == True and after.self_deaf == False))
        deaf = ((before.deaf == False and after.deaf == True) or (before.deaf == True and after.deaf == False))
        stream = ((before.self_stream == False and after.self_stream == True) or (before.self_stream == True and after.self_stream == False))
        video = ((before.self_video == False and after.self_video == True) or (before.self_video == True and after.self_video == False))

        #ignore
        if smute or mute or sdeaf or deaf or stream or video:
            return

        #somebody leaved/entered voice channel
        else:
            for server in bot.voice_clients: #cycle through all servers
                if(server.channel == after.channel): #connect
                    PlaySound(after.channel, hellos)

                elif(server.channel == before.channel): #disconnect
                    PlaySound(before.channel, goodbyes)

#Bot commands----------------------------------------
#sup
@bot.command()
async def sup(ctx):
    """Pytasz bota co tam u niego."""
    await ctx.reply("nm u?")

#nm
@bot.command()
async def nm(ctx):
    """Reakcja bota na to że nic ciekawego się u ciebie nie dzieje."""
    await ctx.reply("cool.")

#wiek
@bot.command()
async def wiek(ctx, wiek : int):
    """Czy możesz rzucać kartę dla takiego wieku? (yo wiek liczba)"""
    wynik = (wiek/2) + 7
    await ctx.reply("Yo, " + str(wynik) + " i rzucasz kartę byniu.")

#send dm to user
@bot.command()
async def dmuser(ctx, user : discord.Member, text : str, *args):
    """Pisze dm do użytkownika. (yo dmuser @użytkownik tekst)"""

    #get text after space
    spaceText = ""
    for txt in args:
        spaceText += (" " + str(txt))

    await user.send('\nYo,\n' + text + spaceText)
    await ctx.reply("Yo, wysłano dm do " + str(user.mention) + ".")

#send dm to Szary
@bot.command()
async def dmszary(ctx, text : str, *args):
    """Pisze dm do szarego. (yo dmszary tekst)"""

    #get text after space
    spaceText = ""
    for txt in args:
        spaceText += (" " + str(txt))

    user = bot.get_user(os.getenv('DISCORD_ID_SZARY')) #Szary ID
    await user.send('\nYo,\n' + text + spaceText)
    await ctx.reply("Yo, wysłano dm do Szarego.")

#picks random person from voicechannel you are in
@bot.command()
async def impostor(ctx):
    """Kto z kanału jest impostorem"""

    channel = discord.utils.get(ctx.guild.voice_channels,  name=ctx.message.author.voice.channel.name) #get voice channel that caller is in

    member_ids = list(channel.voice_states.keys()) #list of user ids

    pickedUserId = random.randint(0, len(member_ids)-1) #random user from list

    user = await bot.fetch_user(member_ids[pickedUserId]) #id to user
    
    await ctx.reply("Yo, " + str(user.mention) + " jest impostorem.")

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
        await ctx.reply(text) #send output


#Poll
@bot.command(aliases=['poll', 'glosowanie', 'głosowanie'])
async def ankieta(ctx, option1 : str, *args):
    """Tworzy ankietę na max 10 opcji (yo ankieta [opcja1] [opcja2]...)"""

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

    i = 0 #option id
    for option in options:
        if i<10:
            embed.add_field(name=str(i), value=str(option), inline=False) #add option field
            i += 1
        else:
            break

    msg = await ctx.send(embed=embed)

    for emoji in emojis:
        if i > 0: 
            await msg.add_reaction(emoji)
            i -= 1


#send submission from reddit--------------------------------------------------
#typed-in subreddit
@bot.command(aliases=['sub'])
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
@bot.command(aliases=['Meme'])
async def meme(ctx):
    """Wysyła losowego mema z r/memes."""

    embed = PostFromReddit("memes", ctx)

    await ctx.send(embed=embed)

#dankmemes
@bot.command(aliases=['DankMeme'])
async def dankmeme(ctx):
    """Wysyła losowego mema z r/dankmemes."""

    embed = PostFromReddit("dankmemes", ctx)

    await ctx.send(embed=embed)

#dankmemes
@bot.command(aliases=['MakeMyDay'])
async def makemyday(ctx):
    """Wysyła losowego mema z r/dankmemes."""

    await dankmeme(ctx)

#stats -----------------------------------------------------------------------
@bot.command(aliases=['statystyki'])
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

    #server
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
    output += "\n**➤Ilość banów w sumie: **" + str(bans)
    output += "\n**➤Ilość kicków w sumie: **" + str(kicks)

    #bot
    output += "\n\n__**Statystyki bota:**__"
    output += "\n**➤Ilość serwerów na których jestem: **" + str(len(ctx.bot.guilds))
    output += "\n**➤Ping: **" + str(round(ctx.bot.latency * 100, 2)) + "ms"
    
    #user
    output += "\n\n__**Statystyki " + str(ctx.message.author.mention) + ":**__"
    output += "\n**➤Utworzono konto: **" + str(ctx.message.author.created_at)[0:-7]
    output += "\n**➤Dołączono do serwera: **" + str(ctx.message.author.joined_at)[0:-7]
    
    await ctx.send(output)


#VOICE---------------------------------------------------------------------------
#MP3
@bot.command(aliases=["bind"])
async def playbind(ctx, name:str, cooldown:int=None):
    """Odtwarza binda (lista: 'yo bindlist')"""

    #cooldown to leave channel
    if cooldown is None:
        cooldown = 60 #wait 60sec by default

    # grab the user who sent the command
    user=ctx.message.author
    voice_channel=user.voice.channel

    found = False #if user is in the same vc as bot

    if voice_channel != None: # only play music if user is in any voice channel

        if(bot.voice_clients != []): #if bot is on any server

            for server in bot.voice_clients: #cycle through all servers
                if(server.channel == voice_channel): #find if bot is on the same channel as user
                    vc = server #already on the same channel
                    found = True #found user on the same channel
                    break

            if found == False: #User is on the same server, but on other channel
                await leave(ctx, False, False) #switch channels
                vc = await voice_channel.connect()
                await ctx.reply("Yo, Dołączam na kanał **" + str(voice_channel.name) + "**.") #send message to chat

        else:
            vc = await voice_channel.connect() #connect to the requested channel, bot isn't connected to the server
            await ctx.reply("Yo, Dołączam na kanał **" + str(voice_channel.name) + "**.") #send message to chat

        vc.play(discord.FFmpegPCMAudio('mp3/'+name+'.mp3'), after=lambda e: print('Player error: %s' % e) if e else None) #play mp3

        #say that bot plays mp3 file
        if(name != "yo" and name != "tts" and name != "yt"):
            await ctx.send('Yo, odtwarzam "**' + name + '**".') #send message to chat


        #cooldown before leaving
        while vc.is_playing(): #Checks if voice is playing
            await asyncio.sleep(1) #While it's playing it sleeps for 1 second

        #cooldown to exit
        #else:
        #    await asyncio.sleep(cooldown) #If it's not playing it waits cooldown seconds
        #    while vc.is_playing(): #and checks once again if the bot is not playing
        #        break #if it's playing it breaks
        #    else:
        #        await asyncio.sleep(cooldown) #wait again
        #        await leave(ctx, True, True) #if not it disconnects


@bot.command(aliases=['bindy'])
async def bindlist(ctx):
    """Wyświetla listę dostępnych bindów"""

    list = os.listdir("./mp3") #take all the available binds
    list = sorted(list, key=str.lower) #sort list alphabetically

    i = 0 #line counter
    j = 1 #messages counter

    color = random.randint(0, 0xffffff) #random color

    #create new embed
    embed=discord.Embed() 
    embed.colour = color
    embed.title = "Dostępne bindy: (1/" + str(math.ceil(len(list)/25)) + ")" #set title
    embed.description="'yo playbind [nazwabinda]'" #set dsc
    
    for val in list:

        #new message
        if(i == 25):
            #send embed
            await ctx.send(embed=embed)

            j += 1 #add to message counter

            #create new embed
            embed=discord.Embed() 
            embed.colour = color
            embed.title = "Yo, Dostępne bindy: (" + str(j) + "/" + str(math.ceil(len(list)/25)) + ")" #set title
            embed.description="'yo playbind [nazwabinda]'" #set dsc

            i = 0 #reset line counter

        if (str(val)[0:-4] != "tts" and str(val)[0:-4] != "yt"):
            embed.add_field(name=str(val)[0:-4], value="yo playbind " + str(val)[0:-4], inline=False) #add field without .mp3
        i += 1 #add to line counter

    await ctx.send(embed=embed) #send last message


@bot.command(aliases=["j", "J"])
async def join(ctx, cooldown:int=None):
    """Wchodzi na kanał głosowy"""

    #cooldown to leave channel
    if cooldown is None:
        cooldown = 600 #wait 10min by default

    await playbind(ctx, 'yo', cooldown)


@bot.command(aliases=["l", "L"])
async def leave(ctx, sendMessage:bool=None, sayGoodbye:bool=None):
    """Wychodzi z kanału głosowego"""
    #leave channel if is on voice channel
    server = ctx.message.guild.voice_client
    if server != None:

        if((sendMessage is not None and sendMessage == True) or (sendMessage is None)):
            await ctx.send("Yo, wychodzę z kanału głosowego.")

        #play goodbye sound
        if sayGoodbye == True or sayGoodbye is None:

            vc = server #get voice channel

            voiceLineId = random.randint(1, (len(goodbyes)-1))

            if vc.is_playing() == False:
            
                if voiceLineId > goodbyes[0]: #if use tts   
                    message = gtts(goodbyes[voiceLineId], lang = 'pl', tld='pl')
                    message.save('mp3/tts.mp3')
                    vc.play(discord.FFmpegPCMAudio('mp3/tts.mp3'), after=lambda e: print('Player error: %s' % e) if e else None)

                else: #play normal bind
                    vc.play(discord.FFmpegPCMAudio(goodbyes[voiceLineId]), after=lambda e: print('Player error: %s' % e) if e else None)

            while vc.is_playing(): #Checks if voice is playing
                await asyncio.sleep(1) #While it's playing it sleeps for 1 second
            else:
                await server.disconnect() #leave

        else:
            await server.disconnect() #leave
        

@bot.command(aliases=["s", "S"])
async def stop(ctx):
    """Zatrzymuje odtwarzanie"""
    server = ctx.message.guild.voice_client 

    if(server != None): #current voice channel   
        vc = server #get voice channel  

        #if playing stop
        if vc.is_playing() == True:
            vc.stop()


#TTS
@bot.command(aliases=["TTS", "tss", "TSS"])
async def tts(ctx, userText : str, *args):
    """Bot powtórzy co do niego napiszesz"""

    #get text after space
    spaceText = ""
    for txt in args:
        spaceText += (" " + str(txt))

    txt = (userText + spaceText)

    #generate tts
    message = gtts(txt, lang = 'pl', tld='pl')
    message.save('mp3/tts.mp3')

    #play tts
    await playbind(ctx, "tts")

#Disabled because it's too much load for Raspberry Pi Zero W
#YouTube
#@bot.command(aliases=["playt", "yt", "youtube"])
#async def playyt(ctx, youtubeLink):
#
#    #download vid
#    youtube_dl.YoutubeDL({'format': 'bestaudio/best','outtmpl': 'mp3/yt.%(ext)s', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec':'mp3', #'preferredquality': '192'}]}).download([youtubeLink])
#
#    #play yt vid
#    await playbind(ctx, "yt")


#universal play
@bot.command(aliases=["p", "P"])
async def play(ctx, txt):
    """Odtwarza dźwięk"""

    #Disabled because it's too much load for Raspberry Pi Zero W
    #if link play yt
    #if str(txt)[0:3] == "http":
    #    await playyt(ctx, "yt")
#
    ##else play bind   
    #else:
    #    await playbind(ctx, txt)


    await playbind(ctx, txt)


#Start bot --------------------------------------------------------------------
bot.run(TOKEN)