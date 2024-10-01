import os

INSTANCELIST: tuple = ("https://inv.nadeko.net", )
currentActiveInstance = INSTANCELIST[0]

CMD_PREFIX: str = "$ivm "

def getToken() -> str:
	if (not os.path.exists(".privatetoken")):
		open(".privatetoken", 'x').close()
		raise Exception("Bot token file does not exist, we've created a new one for you; please add the token to the file.")

	rtn: str = ""
	with open(".privatetoken", 'r') as btk:
		rtn = btk.readline().strip()
	btk.close()

	return rtn

# TODO: add more from https://api.invidious.io/ and properly implement backup instances