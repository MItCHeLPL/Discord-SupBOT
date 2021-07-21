import discord
from discord.ext import commands
import random
from gtts import gTTS as gtts
import asyncio

class VCDoorman(commands.Cog):
    """Odźwierny"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if(self.bot.voice_clients != [] and member.id != self.bot.user.id): #if bot is in the same voice channel

            #ignore
            smute = ((before.self_mute == False and after.self_mute == True) or (before.self_mute == True and after.self_mute == False)) #ignore when bot switches mute
            mute = ((before.mute == False and after.mute == True) or (before.mute == True and after.mute == False)) #ignore when someone switches mute
            sdeaf = ((before.self_deaf == False and after.self_deaf == True) or (before.self_deaf == True and after.self_deaf == False)) #ingore when bot switches deaf
            deaf = ((before.deaf == False and after.deaf == True) or (before.deaf == True and after.deaf == False)) #ignore when someone switches deaf
            stream = ((before.self_stream == False and after.self_stream == True) or (before.self_stream == True and after.self_stream == False)) #ignore when someone switches stream
            video = ((before.self_video == False and after.self_video == True) or (before.self_video == True and after.self_video == False)) #ignore when someone switches video

            #ignore events
            if smute or mute or sdeaf or deaf or stream or video:
                return

            #somebody leaved/entered voice channel
            else:
                for server in self.bot.voice_clients: #cycle through all servers
                    if (str(server.guild.id) in self.bot.data["setting"]["vc_doorman"] and self.bot.data["setting"]["vc_doorman"][str(server.guild.id)]["enable_greeting"]) or self.bot.data["setting"]["vc_doorman"]["default"]["enable_greeting"]:
                        if(server.channel == after.channel): #someone connects
                            await self.PlaySound(after.channel, self.bot.data["audio"]["greetings"], str(member.display_name))

                    if (str(server.guild.id) in self.bot.data["setting"]["vc_doorman"] and self.bot.data["setting"]["vc_doorman"][str(server.guild.id)]["enable_farewell"]) or self.bot.data["setting"]["vc_doorman"]["default"]["enable_farewell"]:
                        if(server.channel == before.channel): #someone disconnects
                            await self.PlaySound(before.channel, self.bot.data["audio"]["farewells"], str(member.display_name))
    

    async def PlaySound(self, channel : discord.VoiceChannel, array, member:str=None):
        for server in self.bot.voice_clients: #cycle through all servers
            if(server.channel == channel): #find current voice channel
                vc = server #get voice channel

                voiceLineId = random.randint(0, (len(array)-1)) #pick random voice line

                #play voice line 
                if vc.is_playing() == False: #if not saying something
                    if array[voiceLineId].find('tts') != -1 and member != None and self.bot.data["setting"]["vc_doorman"]["enable_member_tts"]: #add member name at the end of voice line, becouse file has tts in name and there is passed member string
                        #generate tts with member name
                        message = gtts(array[voiceLineId] + " " + str(member), lang = self.bot.data["ttsLang"], tld=self.bot.data["ttsTld"])
                        message.save(self.bot.data['ttsAudioPath'] + 'tts_member_name.mp3')

                        vc.play(discord.FFmpegPCMAudio(self.bot.data['audioPath'] + array[voiceLineId]), after=lambda e: print('Player error: %s' % e) if e else None) #play voice line on channel

                        #cooldown before saying member name
                        while vc.is_playing(): #Checks if voice is playing
                            await asyncio.sleep(0.25) #While it's playing it sleeps for .25 of a second
                        
                        vc.play(discord.FFmpegPCMAudio(self.bot.data['ttsAudioPath'] + 'tts_member_name.mp3'), after=lambda e: print('Player error: %s' % e) if e else None) #play member name on channel

                    else:#play normal bind
                        vc.play(discord.FFmpegPCMAudio(self.bot.data['audioPath'] + array[voiceLineId]), after=lambda e: print('Player error: %s' % e) if e else None) #play voice line on channel

                break 

def setup(bot):
    bot.add_cog(VCDoorman(bot))