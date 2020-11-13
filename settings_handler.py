import json
import os


class themeHandler:
	def makeFile():
		settings_file = "data/settings.json"
		
		data = {
			"theme" : "red"
		}

		if not os.path.exists(settings_file):
			with open(settings_file, "w") as file:
				json.dump(data, file, indent=2)


	def changeTheme(new_theme):
		settings_file = "data/settings.json"

		with open(settings_file, "r") as file:
			data = json.load(file)

		data['theme'] = new_theme

		with open(settings_file, "w") as file:
			json.dump(data, file, indent=2)




	def setAccent():
		settings_File = "data/settings.json"

		with open(settings_File, "r") as file:
			data = json.load(file)

		theme = data['theme']

		if theme == "red":
			ACCENT = "#e02222"  # RED-ISH

		elif theme == "green":
			ACCENT = "#08964f"  # GREEN-ISH

		elif theme == "blue":
			ACCENT = "#1c6199"  # BLUE-ISH
		
		elif theme == "purple":
			ACCENT = "#941692"  # PURPLE-ISH 
		
		elif theme == "pink":
			ACCENT = "#f533ff"  # PINK-ISH  
		
		elif theme == "aqua":
			ACCENT = "#19a69f"  # AQUA

		elif theme == "yellow":
			ACCENT = "#9aa619"  # YELLOW-ISH

		elif theme == "orange":
			ACCENT = "#ff5900"  # ORANGE-ISH

		return ACCENT




themeHandler.makeFile()
