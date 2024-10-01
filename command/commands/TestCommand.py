from I_Command import I_Command

class TestCommand(I_Command):
	def __init__(self):
		super().__init__("test", 't', "a test command")

	def onInvoke(self, argsArr: list[str]):
		print(argsArr)