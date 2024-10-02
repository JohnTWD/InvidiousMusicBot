'''
import discord
import shlex

class Command:
	def __init__(self, fullName: str, alias: str):
		self.fullName: str = fullName
		self.alias:	  str = alias

	def isCalled(self, command: discord.Message):
		fullInput: list[str] = shlex.split(command.content, posix=False)
		return (("--" + self.fullName) in fullInput) or (('-' + self.alias) in fullInput)

	def getArgs(self, command: discord.Message) -> list[str]:
		# Handler to get arguments from subcommands
		# If a subcommand exists, it returns a list with [0] being the subcommand and the rest, passed arguments
		# If it does not, it returns an empty list
		# NOTE: not gonna perform validation on the correct prefix, since it is assumed that there is a check in `on_message`
		fullInput: list[str] = shlex.split(command.content, posix=False)
		retArgs: list[str] = []

		shouldCapture: bool = False
		for cmdArg in fullInput:
			if ((not shouldCapture) and (cmdArg == ("--" + self.fullName) or cmdArg == ('-' + self.alias))):
				shouldCapture = True
				retArgs.append(cmdArg)
				continue	# we dont want go to the startswith check, because we are including the first argument
			
			if (shouldCapture):
				if (cmdArg.startswith('-')): # end capture when it reaches another subcommand (denoted with prefix of '-')
					break		# NOTE: MUST TELL THE USER, IF ARGUMENT OF SUBCOMMAND HAS PREFIX '-', IT MUST BE SURROUNDED...
								# ...WITH QUOTES (""), ELSE IT WILL BE INTERPRETED AS ANOTHER SUBCOMMAND AND IGNORED.

				retArgs.append(cmdArg.strip('"'))

		return retArgs
'''
