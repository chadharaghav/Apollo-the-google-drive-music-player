import json
import os


class playlistsHandler:
	def makeFile():
		playlists_file =  "data/playlists.json"

		data = {
			"favourites" : []
		}
		
		if not os.path.exists(playlists_file):
			with open(playlists_file, "w") as file:
				json.dump(data, file, indent=2)



	def createNewPlaylist(playlist_name):
		playlists_file = "data/playlists.json"

		with open(playlists_file, "r") as file:
			data = json.load(file)
			data[playlist_name] = list()

		with open(playlists_file, "w") as file:
			json.dump(data, file, indent=2)



	def addToPlaylist(playlist_name, song_name, song_location):
		playlists_file =  "data/playlists.json"

		with open(playlists_file, "r") as file:
			data = json.load(file)
			data_to_append = [song_name, song_location]
			data[playlist_name].append(data_to_append)

		
		with open(playlists_file, "w") as file:
			json.dump(data, file, indent=2)



	def getPlaylistsName():
		# RETURNS A LIST OF NAMES OF PLAY LISTS
		playlists_file =  "data/playlists.json"
		playlists = list()
		with open(playlists_file, "r") as file:
			data = json.load(file)
			for playlists_name in data:
				playlists.append(playlists_name)

		return playlists
				


	def displayPlaylist(name):
		# A FUNCTION THAT RETURNS A LIST OF SINGS THAT EXIST IN A PLAYLIST
		playlists_file = "data/playlists.json"
		songs_in_playlist = []
		with open(playlists_file, "r") as file:
			data = json.load(file)
			playlist_to_display = data[name]
			for song in playlist_to_display:
				songs_in_playlist.append(song)

		return songs_in_playlist



	def deletePlaylist(name):
		# FUNCTION TO DELETE A PLAYLIST
		playlists_file = "data/playlists.json"

		with open (playlists_file, "r") as file:
			data = json.load(file)

		if name in data:
			del data[name]

		with open (playlists_file, "w") as file:
			json.dump(data, file, indent=2)


	def deleteSongFromPlaylist(playlist_name, song_name):
		playlists_file = "data/playlists.json"

		with open (playlists_file, "r") as file:
			data = json.load(file)

		for i in range (0, len(data[playlist_name])):
			if data[playlist_name][i][0] == song_name:
				data[playlist_name].pop(i)
				break
		

		with open (playlists_file, "w") as file:
			json.dump(data, file, indent=2)



playlistsHandler.makeFile()
