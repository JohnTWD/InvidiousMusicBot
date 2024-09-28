import discord
import requests
from instances import currentActiveInstance, getToken
from util.invidious.PlaylistParserUtil import getPlaylist
from util.invidious.AudioStreamGetterUtil import getValidAudioStreamUrls, AudioQuality

class IVMBot(discord.Client):
	async def on_ready(self):
		print(f"{self.user} is alive...")

	async def on_message(self, message):
		if (message.author == self.user):
			return

		await message.channel.send("testing123")
		
def main():
	intents = discord.Intents.default()
	intents.message_content = True
	IVMBotClient = IVMBot(intents=intents)
	IVMBotClient.run(getToken())

if (__name__=="__main__"):	main()
