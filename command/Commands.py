import shlex
import discord
from command.I_Command import I_Command
from command.commands.TestCommand import TestCommand
from command.commands.ExamCommand import ExamCommand


class Commands:
	def __init__(self):
		self.commandList: list[I_Command] = []
		self.commandList.append(TestCommand())
		self.commandList.append(ExamCommand())

	@staticmethod
	def __getSubCmdArgs(argsArr: list[str], command: I_Command):
		# Handler to get arguments from subcommands
		# If a subcommand exists, it returns a list with [0] being the subcommand and the rest, passed arguments
		# If it does not, it returns an empty list
		# NOTE: not gonna perform validation on the correct prefix, since it is assumed that there is a check in `on_message`
		retArgs: list[str] = []

		shouldCapture: bool = False
		for cmdArg in argsArr:
			if ((not shouldCapture) and (cmdArg == (f"--{self.command}") or cmdArg == (f"-{self.command}"))):
				shouldCapture = True
				retArgs.append(cmdArg)
				continue	# we dont want go to the startswith check, because we are including the first argument
			
			if (shouldCapture):
				if (cmdArg.startswith('-')): # end capture when it reaches another subcommand (denoted with prefix of '-')
					break		# NOTE: MUST TELL THE USER, IF ARGUMENT OF SUBCOMMAND HAS PREFIX '-', IT MUST BE SURROUNDED...
								# ...WITH QUOTES (""), ELSE IT WILL BE INTERPRETED AS ANOTHER SUBCOMMAND AND IGNORED.

				retArgs.append(cmdArg.strip('"'))

		return retArgs

	async def tryInvokes(self, dcMsg: discord.Message):
		argsArr: list[str] = shlex.split(dcMsg.content, posix=False)

		for command in self.commandList:
			assert issubclass(type(command), I_Command) # need this or else linter will not recognize command
			if (command.isCalled(argsArr)):
				await command.onInvoke(dcMsg, self.__getSubCmdArgs(argsArr, command))