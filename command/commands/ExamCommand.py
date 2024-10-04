import discord
from command.I_Command import I_Command

class ExamCommand(I_Command):
	def __init__(self):
		super().__init__(
			"exam",
			'e',
			"another test command",
			"**NO ARGUMENTS**"
		)

	async def onInvoke(self, dcMsg: discord.Message, argsArr: list[str]) -> None:
		await dcMsg.channel.send(f"exam args: {argsArr}")