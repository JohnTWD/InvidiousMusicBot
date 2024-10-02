import discord
from abc import ABC, abstractmethod

class I_Command(ABC): # interface for commands

	def __init__(self, command: str, alias: str, description: str):
		self.command: str = command
		self.alias: str = alias
		self.description: str = description

	@abstractmethod 
	async def onInvoke(self, dcMsg: discord.Message, argsArr: list[str]): pass

	def isCalled(self, argsArr: list[str]):
		return ((f"--{self.command}") in argsArr) or ((f"-{self.command}") in argsArr)

	def getDescription(self):
		return self.description

	def getAlias(self):
		return self.alias

	def getCommand(self):
		return self.command