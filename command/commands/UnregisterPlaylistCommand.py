import discord
from command.I_Command import I_Command
from util.databasing.DatabaseUtils import deletePlaylist

class UnregisterPlaylistCommand(I_Command):
	def __init__(self):
		super().__init__(
			"unregisterplaylist",
			"rem",
			"Remove playlist from database and stop tracking it permanently",
			"[Invidious playlist ID]"
		)

	async def onInvoke(self, dcMsg: discord.Message, argsArr: list[str]) -> None:
		deletePlaylist(argsArr[1], dcMsg.guild.id, dcMsg.channel.id)
		await dcMsg.reply(f"If the playlist, `{argsArr[1]}`, has existed in our databases, it is now long gone...")

		