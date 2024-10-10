import discord
from command.I_Command import I_Command
from util.databasing.DatabaseUtils import updatePlaylistAndGetResponse

class CheckPlaylistCommand(I_Command):
	def __init__(self):
		super().__init__(
			"checkplaylist",
			"ck",
			"If playlist ID is known, checks for any changes, else we simply add to our database.",
			"[Invidious playlist ID]"
		)

	async def onInvoke(self, dcMsg: discord.Message, argsArr: list[str]) -> None:
		await dcMsg.channel.send(f"Args passed: {argsArr[1]}...loading...")
		resp: str = await updatePlaylistAndGetResponse(argsArr[1], dcMsg.guild.id)
		await dcMsg.reply(resp)