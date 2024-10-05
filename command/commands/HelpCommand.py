import discord
from command.I_Command import I_Command

class HelpCommand(I_Command):
	def __init__(self):
		super().__init__(
			"help",
			'h',
			"Returns the help list for all of IVMBot's functions",
			"**NO ARGUMENTS**"
		)

	async def onInvoke(self, dcMsg: discord.Message, argsArr: list[str]) -> None:
		helpMessage: str = """You can call a command via its alias or its full name. 
If you call a command via its alias, add a '-', e.g. `-e [args]`.
For its fullname, add '--': `--example [args]`
It is also possible to stack multiple commands, e.g.
```
$ivm --example1 arg1 arg2 --example2 arg1 arg2 ...
```

Available commands:"""

		from command.CommandHandler import commandList
		for command in commandList:
			assert issubclass(type(command), I_Command)
			helpMessage += f"\n{command.getCommand()} | {command.getDescription()} | Usage: `-{command.getAlias()} {command.getUsageHelp()}`"

		await dcMsg.reply(helpMessage)