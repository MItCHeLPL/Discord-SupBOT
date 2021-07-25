import discord
from discord.ext import commands
import random
from gtts import gTTS as gtts
import asyncio
import datetime

class VCDoorman(commands.Cog):
    """Odźwierny"""
    def __init__(self, bot):
        self.bot = bot

        if self.bot.data["debug"]["vc_doorman"]:
            print(f"[vc_doorman]Loaded")


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        #ignore
        smute = ((before.self_mute == False and after.self_mute == True) or (before.self_mute == True and after.self_mute == False))#ignore when bot switches mute
        mute = ((before.mute == False and after.mute == True) or (before.mute == True and after.mute == False)) #ignore when someoneswitches mute
        sdeaf = ((before.self_deaf == False and after.self_deaf == True) or (before.self_deaf == True and after.self_deaf == False))#ingore when bot switches deaf
        deaf = ((before.deaf == False and after.deaf == True) or (before.deaf == True and after.deaf == False)) #ignore when someoneswitches deaf
        stream = ((before.self_stream == False and after.self_stream == True) or (before.self_stream == True and after.self_stream ==False)) #ignore when someone switches stream
        video = ((before.self_video == False and after.self_video == True) or (before.self_video == True and after.self_video == False)) #ignore when someone switches video
        suppress = ((before.suppress == False and after.suppress == True) or (before.suppress == True and after.suppress == False)) #ignore when the user is suppressed from speaking

        #ignore events
        if smute or mute or sdeaf or deaf or stream or video or suppress:
            return
        else:

            if(self.bot.voice_clients != [] and member.id != self.bot.user.id): #if bot is in the same voice channel
                
                #somebody leaved/entered voice channel
                for server in self.bot.voice_clients: #cycle through all servers

                    if (str(server.guild.id) in self.bot.data["setting"]["vc_doorman"] and self.bot.data["setting"]["vc_doorman"][str(member.guild.id)]["enable_greeting"]) or (str(server.guild.id) not in self.bot.data["setting"]["vc_doorman"] and self.bot.data["setting"]["vc_doorman"]["default"]["enable_greeting"]):
                        if(server.channel == after.channel): #someone connects
                            await self.PlaySound(after.channel, self.bot.data["audio"]["greetings"], str(member.display_name))

                            if self.bot.data["debug"]["vc_doorman"]:
                                print(f'[vc_doorman][on_voice_state_update]Greeted {member.name}')

                    if (str(server.guild.id) in self.bot.data["setting"]["vc_doorman"] and self.bot.data["setting"]["vc_doorman"][str(member.guild.id)]["enable_farewell"]) or (str(server.guild.id) not in self.bot.data["setting"]["vc_doorman"] and self.bot.data["setting"]["vc_doorman"]["default"]["enable_farewell"]):
                        if(server.channel == before.channel): #someone disconnects

                            if len(before.channel.members) > 1:
                                await self.PlaySound(before.channel, self.bot.data["audio"]["farewells"], str(member.display_name))

                                if self.bot.data["debug"]["vc_doorman"]:
                                    print(f'[vc_doorman][on_voice_state_update]Said goodbye to {member.name}')


            #bot was moved to another channel
            elif(self.bot.voice_clients != [] and member.id == self.bot.user.id and after.channel != None):
                async for x in after.channel.guild.audit_logs(limit=3, before=datetime.datetime.utcnow(), after=(datetime.datetime.utcnow() - datetime.timedelta(seconds=5)), oldest_first=False, action=discord.AuditLogAction.member_move): #look through audit log

                    if(x.extra.channel.id == after.channel.id and x.guild.id == after.channel.guild.id): #action was done to bot

                        #if self.bot.data["debug"]["vc_doorman"]:
                            #print(f'[vc_doorman][on_voice_state_update]Bot was last moved {("from " + before.channel.name) if before.channel != None else None} to {after.channel.name}{(" by " + x.user.name) if x.user != None else None}\n')

                        for server in self.bot.voice_clients: #cycle through all servers

                            if (str(server.guild.id) in self.bot.data["setting"]["vc_doorman"] and self.bot.data["setting"]["vc_doorman"][str(member.guild.id)]["enable_greeting"]) or (str(server.guild.id) not in self.bot.data["setting"]["vc_doorman"] and self.bot.data["setting"]["vc_doorman"]["default"]["enable_greeting"]):
                                if(server.channel == after.channel): #connected

                                    if len(after.channel.members) > 1: #if someone is on vc
                                        await asyncio.sleep(0.5) #wait to get vc
                                        await self.PlaySound(after.channel, self.bot.data["audio"]["greetings"]) #greet users on vc

                                        if self.bot.data["debug"]["vc_doorman"]:
                                            print(f'[vc_doorman][on_voice_state_update]Greeted everyone after being moved {("from " + before.channel.name) if before.channel != None else None} to {after.channel.name}{(" by " + x.user.name) if x.user != None else None}')

                                        break
                        break    
                    

    async def PlaySound(self, channel : discord.VoiceChannel, array, member:str=None):
        for vc in self.bot.voice_clients: #cycle through all servers
            if(vc.channel == channel): #find current voice channel

                voiceLineId = random.randint(0, (len(array)-1)) #pick random voice line

                #play voice line 
                if vc.is_playing() == False: #if not saying something
                    if array[voiceLineId].find('tts') != -1 and member != None and self.bot.data["setting"]["vc_doorman"]["enable_member_tts"]: #add member name at the end of voice line, becouse file has tts in name and there is passed member string
                        #generate tts with member name
                        message = gtts(str(member), lang = self.bot.data["setting"]["tts"]["ttsLang"], tld=self.bot.data["setting"]["tts"]["ttsTld"])
                        message.save(self.bot.data['ttsAudioPath'] + 'tts_member_name.mp3')

                        vc.play(discord.FFmpegPCMAudio(self.bot.data['audioPath'] + array[voiceLineId], options = "-loglevel error"), after=lambda e: print('Player error: %s' % e) if e else (print(f'[vc_doorman][PlaySound]Played voiceline on {vc.channel.name}') if self.bot.data["debug"]["vc_doorman"] else None)) #play voice line on channel

                        #cooldown before saying member name
                        while vc.is_playing(): #Checks if voice is playing
                            await asyncio.sleep(0.1) #While it's playing it sleeps for .1 of a second
                        
                        vc.play(discord.FFmpegPCMAudio(self.bot.data['ttsAudioPath'] + 'tts_member_name.mp3', options = "-loglevel error"), after=lambda e: print('Player error: %s' % e) if e else (print(f'[vc_doorman][PlaySound]Played TTS on {vc.channel.name}\n') if self.bot.data["debug"]["vc_doorman"] else None)) #play member name on channel

                    else:#play normal bind
                        vc.play(discord.FFmpegPCMAudio(self.bot.data['audioPath'] + array[voiceLineId], options = "-loglevel error"), after=lambda e: print('Player error: %s' % e) if e else (print(f'[vc_doorman][PlaySound]Played voiceline on {vc.channel.name}\n') if self.bot.data["debug"]["vc_doorman"] else None)) #play voice line on channel

                break 

def setup(bot):
    bot.add_cog(VCDoorman(bot))