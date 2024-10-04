import discord
from command.I_Command import I_Command

class CheckPlaylistCommand(I_Command):
	def __init__(self):
		super.__init__(
			"checkplaylist",
			"ck",
			"If playlist ID is known, checks for any changes, else we simply add to our database."
			"[Invidious playlist ID]"
		)

	async def onInvoke(self, dcMsg: discord.Message, argsArr: list[str]) -> None:
		pass