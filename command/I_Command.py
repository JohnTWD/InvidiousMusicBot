from abc import ABC, abstractmethod

class I_Command(ABC): # interface for commands

	def __init__(self, command: str, alias: str, description: str):
		self.command: str = command
		self.alias: str = alias
		self.description: str = description

	@abstractmethod 
	def onInvoke(self, argsArr: list[str]): pass

	def isCalled(self, argsArr: list[str]):
		return (("--" + self.command) in argsArr) or (('-' + self.alias) in argsArr)

	def getDescription(self):
		return self.description

	def getAlias(self):
		return self.alias

	def getCommand(self):
		return self.command