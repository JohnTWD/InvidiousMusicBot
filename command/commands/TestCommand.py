import discord
from command.I_Command import I_Command

class TestCommand(I_Command):
	def __init__(self):
		super().__init__("test", 't', "a test command")

	async def onInvoke(self, dcMsg: discord.Message, argsArr: list[str]):
		await dcMsg.channel.send(f"test args: {argsArr}")