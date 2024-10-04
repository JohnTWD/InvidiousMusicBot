import discord
from abc import ABC, abstractmethod

class I_Command(ABC): # interface for commands

	def __init__(self, command: str, alias: str, description: str, usageHelp: str):
		self.command: 	   str = command
		self.alias: 	   str = alias
		self.description:  str = description
		self.usageHelp:    str = usageHelp

	@abstractmethod 
	async def onInvoke(self, dcMsg: discord.Message, argsArr: list[str]) -> None: pass

	def isCalled(self, argsArr: list[str]) -> bool:
		return ((f"--{self.command}") in argsArr) or ((f"-{self.alias}") in argsArr)

	def getDescription(self) -> str:
		return self.description

	def getAlias(self) -> str:
		return self.alias

	def getCommand(self) -> str:
		return self.command
	
	def getUsageHelp(self) -> str:
		return self.usageHelp