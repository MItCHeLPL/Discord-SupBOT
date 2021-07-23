import discord
from discord.ext import commands
from gtts import gTTS as gtts

class TTS(commands.Cog):
    """Text to Speech"""
    def __init__(self, bot):
        self.bot = bot

        if self.bot.data["debug"]["tts"]:
            print(f"[tts]Loaded")
            
    
    @commands.command(name = 'tts', aliases = ['texttospeech', 'tss', 'ts', 'ttts'])
    async def _tts(self, ctx, userText : str, *args):
        """Odtwarza dźwięk wpisany przez użytkownika (yo tts [tekst])"""
        #get text after space
        spaceText = ""
        for txt in args:
            spaceText += (" " + str(txt))

        txt = (userText + spaceText) #combine text

        #generate tts
        if(len(txt) > 0 and txt != ' '):
            message = gtts(txt, lang = self.bot.data["ttsLang"], tld=self.bot.data["ttsTld"])
            message.save(self.bot.data['ttsAudioPath'] + 'tts.mp3')

            if self.bot.data["debug"]["tts"]:
                print(f'[tts][_tts]Generated TTS: {txt}')

            vc = await self.Join(ctx) #join vc

            await self.PlaySound(vc) #play tts

            await ctx.reply("Odtwarzam TTS: `" + txt + "`", delete_after=5)

            if self.bot.data["debug"]["tts"]:
                print(f'[tts][_tts]Playing TTS\n')

    
    async def Join(self, ctx):
        user_vc=ctx.message.author.voice.channel #get user's vc

        same_channel = False

        if user_vc != None: #user has to be in the vc
            if(self.bot.voice_clients != []): #if bot is on any server's vc
                for vc in self.bot.voice_clients: #cycle through all servers
                    if(vc.channel == user_vc): #bot is already on the same vc
                        same_channel = True

                        if self.bot.data["debug"]["tts"]:
                            print(f'[tts][Join]Bot is in the same vc')

                        return vc #return current channel

                if same_channel == False: #User is on the same server's vc, but not the same channel
                    #await ctx.reply("Dołączam na kanał `" + str(voice_channel.name) + "`", delete_after=5)

                    if self.bot.data["debug"]["tts"]:
                        print(f'[tts][Join]Bot joined vc (bot was on the other channel)')

                    await vc.disconnect() #disconnect from old channel

                    return await user_vc.connect()

            else:
                #await ctx.reply("Dołączam na kanał `" + str(voice_channel.name) + "`", delete_after=5)

                if self.bot.data["debug"]["tts"]:
                    print(f'[tts][Join]Bot joined vc (bot wasnt connected)')

                return await user_vc.connect() #connect to the requested channel, bot isn't connected to any of the server's vc


    async def PlaySound(self, channel : discord.VoiceChannel):
        for vc in self.bot.voice_clients: #cycle through all servers
            if(vc == channel): #find current voice channel
                if vc.is_playing() == False: #if not saying something
                    vc.play(discord.FFmpegPCMAudio(self.bot.data['ttsAudioPath'] + 'tts.mp3'), after=lambda e: print('Player error: %s' % e) if e else None) #play sound on vc

                    if self.bot.data["debug"]["tts"]:
                        print(f'[tts][PlaySound]Played sound')

                break 

def setup(bot):
    bot.add_cog(TTS(bot))