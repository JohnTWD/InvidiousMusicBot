import discord
import requests
from classes.Command import Command
from util.invidious.PlaylistParserUtil import getPlaylist
from constants import currentActiveInstance, getToken, CMD_PREFIX
from util.invidious.AudioStreamGetterUtil import getValidAudioStreamUrls, AudioQuality


class IVMBot(discord.Client):
	async def on_ready(self):
		print(f"{self.user} is alive...")

	async def on_message(self, message: discord.Message):
		if (message.author == self.user):
			return

		if (not message.content.startswith(CMD_PREFIX)):
			return
		
		calledCmdObj: Command = Command("called", 'c')
		argTestObj	: Command = Command("argt", 'a')

		if (calledCmdObj.isCalled(message)):
			await message.channel.send("Indeed you are called")

		if (argTestObj.isCalled(message)):
			formedStr: str = "Function called with arguments:\n"
			argsTestArgs: list[str] = argTestObj.getArgs(message)

			for i in argsTestArgs:
				formedStr += f"{i}, "

			await message.channel.send(formedStr)
def main():
	intents = discord.Intents.default()
	intents.message_content = True
	IVMBotClient = IVMBot(intents=intents)
	IVMBotClient.run(getToken())

if (__name__=="__main__"):	main()
