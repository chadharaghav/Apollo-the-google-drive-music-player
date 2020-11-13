import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import audio_metadata
from io import BytesIO
from mutagen.mp3 import MP3
import random
import shutil
import pygame
import stagger
import urllib
import time
import os
import os.path
import atexit
import time

import cloud_backend
from playlists_handler import playlistsHandler
from settings_handler import themeHandler



BG = "#272a30"
FG = "white"
ACCENT = themeHandler.setAccent()
BG_SP = BG
FONT = ("Helvetica", 15)

# initialising pygame mixer
pygame.mixer.init()



class myApp:
	def __init__(self, master):
		# ****************** VARIABLES AND LISTS AND OTHER MISC THINGIES **********************
		self.libraryPlay = True
		self.onlinePlay = False
		self.queuePlay = False
		self.playlistPlay = False
		self.songsList = os.listdir(r"data/local")
		self.isPlaying = False
		self.isPaused = False
		self.initial = True
		self.nowPlaying = ""
		self.currSongPath = ""
		self.currSongLength = ""
		self.currSongPosition = 0
		self.sliderPosition = 0
		self.job = None
		self.queue = list()
		self.queueFlag = -1
		self.donePlaying = False
		self.selectedPlaylist = str()


		# ******************** DECLARING CONTAINERS ******************************
		
		# FOR THE MAIN ELEMENTS (LEFT SIDE)
		self.toolBar = tk.Menu(master)
		self.toolBar.config(background=BG)
		master.config(menu=self.toolBar)

		self.playerContainer = tk.Canvas(master, background=BG, borderwidth=0, highlightthickness=0)
		self.playerContainer.grid(row=0, column=0)

		self.topBar = tk.Frame(self.playerContainer, bg=BG, borderwidth=0, highlightthickness=0)
		self.topBar.pack()

		self.playerFrame = tk.Frame(self.playerContainer, bg=BG , borderwidth=0, highlightthickness=0)
		self.playerFrame.pack()

		self.optionsFrame = tk.Frame(self.playerContainer, bg=BG, borderwidth=0, highlightthickness=0)
		self.optionsFrame.pack()

		self.buttonFrame = tk.Frame(self.playerContainer, bg=ACCENT, borderwidth=0, highlightthickness=0)
		self.buttonFrame.pack(fill=tk.X, pady=20)

		self.sliderFrame = tk.Frame(self.buttonFrame, bg=ACCENT, borderwidth=0, highlightthickness=0)
		self.sliderFrame.grid(row=0, column=4, padx=50, pady=10, sticky="e")


		# FOR THE SIDE PLAYER (RIGHT SIDE)
		self.sidePlayerContainer = tk.Canvas(master, background=BG_SP)
		self.sidePlayerContainer.grid(row=0, column=1)

		self.sidePlayer = tk.Frame(self.sidePlayerContainer, background=BG_SP)
		self.sidePlayer.pack()

		# FOR STATUS LABEL
		self.statusBar = tk.Frame(master, bg=BG, relief=tk.SUNKEN)
		self.statusBar.grid(row=1, column=0, columnspan=2, sticky="ew")

		self.statusLabel = tk.Label(self.statusBar, bg=BG, fg=FG, font=('Helevetica', 10, 'bold'))
		self.statusLabel.grid(row=0, column=0)



		# *********************** MAIN ELEMENTS *****************************
		# TOOLBAR
		self.file = tk.Menu(self.toolBar, tearoff=0)
		self.toolBar.add_cascade(label="File", menu=self.file)
		self.file.add_command(label="Add Songs To Library", command=self.addSongsToLibrary)
		self.file.add_command(label="Delete Songs From Library", command=self.deleteSongsFromLibrary)

		self.settings = tk.Menu(self.toolBar, tearoff=0)
		self.toolBar.add_cascade(label="Settings", menu=self.settings)
		
		self.theme = tk.Menu(self.settings, tearoff=0)
		self.settings.add_cascade(label="Theme", menu=self.theme)

		self.theme.add_cascade(label="red", command=lambda: self.changeTheme("red"))
		self.theme.add_cascade(label="green", command=lambda: self.changeTheme("green"))
		self.theme.add_cascade(label="blue", command=lambda: self.changeTheme("blue"))
		self.theme.add_cascade(label="purple", command=lambda: self.changeTheme("purple"))
		self.theme.add_cascade(label="pink", command=lambda: self.changeTheme("pink"))
		self.theme.add_cascade(label="aqua", command=lambda: self.changeTheme("aqua"))
		self.theme.add_cascade(label="yellow", command=lambda: self.changeTheme("yellow"))
		self.theme.add_cascade(label="orange", command=lambda: self.changeTheme("orange"))


		# TOP BAR
		TOPBAR_FONT = ('Helvetica', 15, 'bold')
		UNCLICKED = FG
		CLICKED = ACCENT

		self.libraryButton = tk.Button(self.topBar, text="LIBRARY",bg=BG, fg=CLICKED, font=TOPBAR_FONT, borderwidth=0)
		self.libraryButton.config(command=self.library)
		self.libraryButton.grid(row=0, column=0, padx=10, pady=10)

		self.onlineButton = tk.Button(self.topBar, text="ONLINE", bg=BG, fg=UNCLICKED, font=TOPBAR_FONT, borderwidth=0)
		self.onlineButton.config(command=self.online)
		self.onlineButton.grid(row=0, column=1, padx=10, pady=10)

		self.queueDispButton = tk.Button(self.topBar, text="QUEUE", bg=BG, fg=UNCLICKED, font=TOPBAR_FONT, borderwidth=0)
		self.queueDispButton.config(command=self.showQueue)
		self.queueDispButton.grid(row=0, column=2, padx=10, pady=10)

		self.playlistButton = tk.Button(self.topBar, text="PLAYLISTS", bg=BG, fg=UNCLICKED, font=TOPBAR_FONT, borderwidth=0)
		self.playlistButton.config(command=self.showPlaylists)
		self.playlistButton.grid(row=0, column=3, padx=10, pady=10)


		self.libraryButton.bind("<Enter>", lambda x: self.buttonHoverEnter(x,6))
		self.onlineButton.bind("<Enter>", lambda x: self.buttonHoverEnter(x,7))
		self.queueDispButton.bind("<Enter>", lambda x: self.buttonHoverEnter(x,8))
		self.playlistButton.bind("<Enter>", lambda x: self.buttonHoverEnter(x,9))

		self.libraryButton.bind("<Leave>", lambda x: self.buttonHoverLeave(x,6))
		self.onlineButton.bind("<Leave>", lambda x: self.buttonHoverLeave(x,7))
		self.queueDispButton.bind("<Leave>", lambda x: self.buttonHoverLeave(x,8))
		self.playlistButton.bind("<Leave>", lambda x: self.buttonHoverLeave(x,9))


		# SCROLL BAR FOR SONGS DISPLAY
		listScrollBar = ttk.Scrollbar(self.playerFrame, orient=tk.VERTICAL)

		
		# SONGS DISPLAY 
		self.listOfSongs = tk.Listbox(self.playerFrame, bg=BG, fg=FG, width=52, font=FONT, selectbackground=ACCENT)
		self.listOfSongs.config(yscrollcommand=listScrollBar.set)
		self.listOfSongs.grid(row=0, column=0, padx=10)

		styleScrollBar = ttk.Style()
		styleScrollBar.theme_use('alt')
		styleScrollBar.configure("Vertical.TScrollbar", gripcount=0,
                background=ACCENT, darkcolor=ACCENT, lightcolor=ACCENT,
                troughcolor=BG, bordercolor=BG, arrowcolor="white")

		listScrollBar.config(command=self.listOfSongs.yview)
		listScrollBar.grid(row=0, column=1, sticky='ns')


		# OPTIONS
		options_font = ('Helvetica', 10, 'bold')
		self.queueButton = tk.Button(self.optionsFrame, text="Queue Song", bg = BG, fg=FG ,font=options_font, borderwidth=0)
		self.queueButton.grid(row=0, column=0, padx=10, pady=5)

		self.stopButton = tk.Button(self.optionsFrame, text="Stop Playback", bg = BG, fg=FG ,font=options_font, borderwidth=0)
		self.stopButton.grid(row=0, column=1, padx=10, pady=5)

		self.favouriteButton = tk.Button(self.optionsFrame, text="Add To Favourites", bg = BG, fg=FG ,font=options_font, borderwidth=0)
		self.favouriteButton.grid(row=0, column=2, padx=10, pady=5)

		self.playlistsActionButton = tk.Button(self.optionsFrame, text="Add To Playlist", bg = BG, fg=FG ,font=options_font, borderwidth=0)
		self.playlistsActionButton.grid(row=0, column=3, padx=10, pady=5)


		# OPTIONS ACTIONS
		self.queueButton.config(command=self.addToQueue)
		self.stopButton.config(command=self.resetEverything)
		self.favouriteButton.config(command=self.addToFavourite)
		self.playlistsActionButton.config(command=self.addToPlaylist)


		# BUTTONS
		BUTTONS_FONT = ('Helvetica', 20, 'bold')

		self.rewind = tk.Button(self.buttonFrame, text = "I<",bg=ACCENT, fg=FG, font=BUTTONS_FONT, borderwidth=0)
		self.rewind.grid(row=0, column=0, padx=10, pady=10)

		self.playPause = tk.Button(self.buttonFrame, text = "I>", bg=ACCENT, fg=FG, font=BUTTONS_FONT, borderwidth=0)
		self.playPause.grid(row=0, column=1, padx=10, pady=10)

		self.fastForward = tk.Button(self.buttonFrame, text=">I", bg=ACCENT, fg=FG, font=BUTTONS_FONT, borderwidth=0)
		self.fastForward.grid(row=0, column=3, padx=10, pady=10)


		# DEFINING BUTTON ACTIONS
		self.playPause.config(command=self.playPauseSongButton)
		self.rewind.config(command=self.prevSongButton)
		self.fastForward.config(command=self.nextSongButton)


		# KEYBOARD BINDINGS
		master.bind("<Left>", self.prevSongButton)
		master.bind("<Right>", self.nextSongButton)
		master.bind("<space>", self.playPauseSongButton)

		self.rewind.bind("<Enter>", lambda x: self.buttonHoverEnter(x,0))
		self.playPause.bind("<Enter>", lambda x: self.buttonHoverEnter(x,1))
		self.fastForward.bind("<Enter>", lambda x: self.buttonHoverEnter(x,2))

		self.rewind.bind("<Leave>", lambda x: self.buttonHoverLeave(x,0))
		self.playPause.bind("<Leave>", lambda x: self.buttonHoverLeave(x,1))
		self.fastForward.bind("<Leave>", lambda x: self.buttonHoverLeave(x,2))



		# *********************** SIDE PLAYER ELEMENTS *****************************

		# ALBUM ART AND SONG INFO DISPLAY
		INFO_FONT = ('Helvetica', 10, 'bold')

		self.albumArtContainer = tk.Canvas(self.sidePlayer, background=BG_SP, borderwidth=0, highlightthickness=0)
		self.albumArtContainer.pack(padx=5, pady=13)

		self.albumArt = tk.Canvas(self.albumArtContainer, width=200, height=200, background="black", highlightbackground=ACCENT, highlightthickness=2)
		self.albumArt.pack()

		self.songNameLabel = tk.Label(self.albumArtContainer, bg=BG_SP, fg=FG, font=INFO_FONT)
		self.songNameLabel.pack()

		self.artistNameLabel = tk.Label(self.albumArtContainer, bg=BG_SP, fg=FG, font=INFO_FONT)
		self.artistNameLabel.pack()


		# SONG PROGRESS BAR
		self.progressBarFrame = tk.Frame(self.sidePlayer, background=BG_SP, borderwidth=0, highlightthickness=0)
		self.progressBarFrame.pack()

		self.startLabel = tk.Label(self.progressBarFrame, text="00:00", bg=BG_SP, fg="white", font=('Helvetica', 10))
		self.startLabel.grid(row=0, column=0)

		self.songSlider = ttk.Scale(self.progressBarFrame, length=150, from_=0, to=100)
		STYLE = ttk.Style()
		STYLE.configure('Horizontal.TScale', background=BG_SP)
		self.songSlider.grid(row=0, column=1)
		self.songSlider.config(command=self.slideAction)

		self.endLabel = tk.Label(self.progressBarFrame, text="00:00", bg=BG_SP, fg="white", font=('Helvetica', 10))
		self.endLabel.grid(row=0, column=2)



		# PLAY, PAUSE , NEXT SONG, PREV SONG BUTTONS
		self.buttonsContainer = tk.Canvas(self.sidePlayer, background=BG_SP, borderwidth=0, highlightthickness=0)
		self.buttonsContainer.pack()

		SP_BUTTONS_FONT = ('Helvetica', 20, 'bold')
		ROW = 1
		CONTAINER = self.buttonsContainer

		self.SP_rewind = tk.Button(self.buttonsContainer, text = "I<",bg=BG_SP, fg=ACCENT, font=SP_BUTTONS_FONT, borderwidth=0)
		self.SP_rewind.grid(row=ROW, column=0, padx=15, pady=15)

		self.SP_playPause = tk.Button(self.buttonsContainer, text = "I>", bg=BG_SP, fg=ACCENT, font=SP_BUTTONS_FONT, borderwidth=0)
		self.SP_playPause.grid(row=ROW, column=1, padx=15, pady=15)

		self.SP_fastForward = tk.Button(self.buttonsContainer, text=">I", bg=BG_SP, fg=ACCENT, font=SP_BUTTONS_FONT, borderwidth=0)
		self.SP_fastForward.grid(row=ROW, column=3, padx=15, pady=15)

		# DEFINING BUTTON ACTIONS
		self.SP_playPause.config(command=self.playPauseSongButton)
		self.SP_rewind.config(command=self.prevSongButton)
		self.SP_fastForward.config(command=self.nextSongButton)

		self.SP_rewind.bind("<Enter>", lambda x: self.buttonHoverEnter(x,3))
		self.SP_playPause.bind("<Enter>", lambda x: self.buttonHoverEnter(x,4))
		self.SP_fastForward.bind("<Enter>", lambda x: self.buttonHoverEnter(x,5))

		self.SP_rewind.bind("<Leave>", lambda x: self.buttonHoverLeaveSP(x,3))
		self.SP_playPause.bind("<Leave>", lambda x: self.buttonHoverLeaveSP(x,4))
		self.SP_fastForward.bind("<Leave>", lambda x: self.buttonHoverLeaveSP(x,5))

		
		# VOLUME SLIDER
		self.volumeSliderFrame = tk.Frame(self.sidePlayer, background=BG_SP, borderwidth=0, highlightthickness=0)
		self.volumeSliderFrame.pack(pady=10)

		self.volumeLabel = tk.Label(self.volumeSliderFrame, text="VOLUME - 100", bg=BG_SP, fg="white", font=('Helvetica', 10, 'bold'))
		self.volumeLabel.grid(row=0, column=1, pady=3)

		self.zeroLabel = tk.Label(self.volumeSliderFrame, text="0", bg=BG_SP, fg=FG, font=('Helvetica', 10))
		self.zeroLabel.grid(row=1, column=0, padx=10)

		self.volumeSlider = ttk.Scale(self.volumeSliderFrame, length=150, from_=0, to=1, value=1) # VOLUME IN PYGAME IS SCALED FROM 0 TO 1
		STYLE = ttk.Style()
		STYLE.configure('Horizontal.TScale', background=BG_SP)
		self.volumeSlider.grid(row=1, column=1)
		self.volumeSlider.config(command=self.changeVolume)

		self.hundredLabel = tk.Label(self.volumeSliderFrame, text="100", bg=BG_SP, fg=FG, font=('Helvetica', 10))
		self.hundredLabel.grid(row=1, column=2, padx=10)




		# ******** FOR INITIAL APP SETUP *****************
		self.library()

		# LIST OF BUTTONS FOR HOVER COLOUR CHANGES
		self.listOfButtons =   {0 : self.rewind, 
								1 : self.playPause, 
								2 : self.fastForward, 
								3 : self.SP_rewind, 
								4 : self.SP_playPause, 
								5 : self.SP_fastForward,
								6 : self.libraryButton,
								7 : self.onlineButton,
								8 : self.queueDispButton,
								9 : self.playlistButton}




	def library(self):
		# FUNCTION TO DISPLAY THE SONGS STORED LOCALLY
		self.queueButton.config(text="Queue Song")
		self.queueButton.config(command=self.addToQueue)

		self.favouriteButton.config(text="Add To Favourites")
		self.favouriteButton.config(command=self.addToFavourite)

		self.playlistsActionButton.config(text="Add To Playlist")
		self.playlistsActionButton.config(command=self.addToPlaylist)

		self.changeSelection('library')
		self.listOfSongs.delete(0,'end')

		for song in self.songsList:
			self.listOfSongs.insert(tk.END, song)



	def online(self):
		# FUNCTION TO DISPLAY LIST OF SONGS ON THE SERVER
		if cloud_backend.credentialsFound():
			if self.internetConnected():
				self.queueButton.config(text="Queue Song")
				self.queueButton.config(command=self.addToQueue)

				self.favouriteButton.config(text="Add To Favourites")
				self.favouriteButton.config(command=self.addToFavourite)

				self.playlistsActionButton.config(text="Add To Playlist")
				self.playlistsActionButton.config(command=self.addToPlaylist)

				self.changeSelection('online')
				self.listOfSongs.delete(0, 'end')

				cloud_backend.updateCloudList()

				for song in cloud_backend.cloudList:
					self.listOfSongs.insert(tk.END, song)

			else:
				messagebox.showwarning("INTERNET NOT CONNECTED", "this feature requires internet connection. Please connect your device to the internet.")

		else:
			messagebox.showwarning("CREDENTIALS NOT FOUND", "could not locate credentials.json")


	
	def showPlaylists(self):
		self.changeSelection('playlists')
		self.listOfSongs.delete(0, 'end')
		playlists = playlistsHandler.getPlaylistsName()
		
		for playlist in playlists:
			self.listOfSongs.insert(tk.END, playlist)


		self.playlistsActionButton.config(text="open playlist")
		self.playlistsActionButton.config(command=self.displaySongsInPlaylist)

		self.queueButton.config(text="Delete Playlist")
		self.queueButton.config(command=self.deletePlaylist)

		self.favouriteButton.config(text="New Playlist")
		self.favouriteButton.config(command=self.newPlaylistMenu)



	def displaySongsInPlaylist(self):
		if self.listOfSongs.curselection():
			name_of_playlist = self.listOfSongs.get(tk.ACTIVE)
			self.selectedPlaylist = name_of_playlist
			songs_in_playlist = playlistsHandler.displayPlaylist(name_of_playlist)

			self.listOfSongs.delete(0, 'end')
			for song in songs_in_playlist:
				self.listOfSongs.insert(tk.END, song[0])


			self.queueButton.config(text="queue playlist")
			self.queueButton.config(command=self.queuePlaylist)

			self.playlistsActionButton.config(text="Delete From Playlist")
			self.playlistsActionButton.config(command=lambda: self.deleteSongFromPlaylist(name_of_playlist))

			self.favouriteButton.config(text="Shuffle Play")
			self.favouriteButton.config(command=self.shufflePlaylist)

			self.statusUpdate(f"displaying '{self.selectedPlaylist}' playlist")

		else:
			self.statusUpdate("no playlist selected...")



	def deleteSongFromPlaylist(self, playlist_name):
		if self.listOfSongs.curselection():
			song_name = self.listOfSongs.get(tk.ACTIVE)
			playlistsHandler.deleteSongFromPlaylist(playlist_name, song_name)
			self.statusUpdate(f" '{song_name}' has been deleted from '{playlist_name}' playlist...")
			song_idx = self.listOfSongs.get(0, 'end').index(song_name)
			self.listOfSongs.delete(song_idx)

		else:
			self.statusUpdate("no song selected...")



	def queuePlaylist(self):
		self.resetEverything()
		cloud_backend.updateCloudList()
		songs_in_playlist = playlistsHandler.displayPlaylist(self.selectedPlaylist)

		for song in songs_in_playlist:
			self.queue.append(song)

		self.queueFlag = 0
		self.queueHandler()
		self.showQueue()

		self.statusUpdate(f" '{self.selectedPlaylist}' playlist queued...")




	def shufflePlaylist(self):
		# FOR SHUFFLE PLAYING A PLAYLIST
		self.resetEverything()
		cloud_backend.updateCloudList()
		songs_in_playlist = playlistsHandler.displayPlaylist(self.selectedPlaylist)

		for song in songs_in_playlist:
			self.queue.append(song)

		random.shuffle(self.queue)

		self.queueFlag = 0
		self.queueHandler()
		self.showQueue()

		self.statusUpdate(f" '{self.selectedPlaylist}' playlist queued...")




	def addToFavourite(self):
		if self.listOfSongs.curselection():
			song_name = self.listOfSongs.get(tk.ACTIVE)
			song_idx = self.listOfSongs.curselection()[0]

			if self.libraryPlay:
				song_location = "library"

			elif self.onlinePlay:
				song_location = "online"

			elif self.queuePlay:
				song_location = self.queue[song_idx][1]

			playlistsHandler.addToPlaylist("favourites", song_name, song_location)
			print(song_name)
			print(song_location)
			self.statusUpdate(f" '{song_name}' added to favourites...")

		else:
			self.statusUpdate("no song selected...")



	def addToPlaylist(self):
		if not self.listOfSongs.curselection():
			self.statusUpdate("no song selected....")


		elif self.listOfSongs.curselection():
			if self.libraryPlay:
				song_name = self.listOfSongs.get(tk.ACTIVE)
				song_location = "library"

			elif self.onlinePlay:
				song_name = self.listOfSongs.get(tk.ACTIVE)
				song_location = "online"

			elif self.queuePlay:
				song_name = self.listOfSongs.get(tk.ACTIVE)
				song_idx = self.listOfSongs.get(0, "end").index(song_name)
				song_location = self.queue[song_idx][1]

			self.addToPlaylistMenu(song_name, song_location)



	def deletePlaylist(self):
		# FUNCTION TO DELETE A PLAYLIST
		if self.listOfSongs.curselection():
			playlist_name = self.listOfSongs.get(tk.ACTIVE)

			if not playlist_name == "favourites":		
				playlistsHandler.deletePlaylist(playlist_name)
				self.statusUpdate(f"playlist '{playlist_name}' has been deleted...")

				playlist_idx = self.listOfSongs.get(0, 'end').index(playlist_name)
				self.listOfSongs.delete(playlist_idx)

			else:
				messagebox.showwarning("PLAYLIST HANDLER", "YOU CANNOT DELETE THIS PLAYLIST!")

		else:
			self.statusUpdate("no playlist selected...")



	def addToPlaylistMenu(self, song_name, song_location):
		# FUNCTION TO DISPLAY THE "ADD SONG TO PLAYLIST" PROMPT
		selectPlaylistWindow = tk.Toplevel(bg=BG)
		selectPlaylistWindow.title("PLAYLISTS")
		selectPlaylistWindow.resizable(False, False)

		
		# DEFINING FRAMES AND CONTAINERS
		titleFrame = tk.Frame(selectPlaylistWindow, bg=ACCENT)
		titleFrame.pack(fill=tk.X, padx=10, pady=10)

		titleLabel = tk.Label(titleFrame, text="CHOOSE PLAYLIST", font=('Helvetica', 15, 'bold'), fg=FG, bg=ACCENT)
		titleLabel.pack(fill=tk.X)
		
		playlistFrame = tk.Frame(selectPlaylistWindow, bg=BG)
		playlistFrame.pack(padx=10, pady=10)

		buttonFrame = tk.Frame(selectPlaylistWindow, bg=BG)
		buttonFrame.pack(padx=10, pady=10, fill=tk.X)


		# SCROLL BAR FOR PLAYLISTS DISPLAY
		scrollBar = ttk.Scrollbar(playlistFrame, orient=tk.VERTICAL)

		
		# PLAYLISTS DISPLAY 
		listOfPlaylists = tk.Listbox(playlistFrame, bg=BG, fg=FG, width=52, font=FONT, selectbackground=ACCENT)
		listOfPlaylists.config(yscrollcommand=scrollBar.set)
		listOfPlaylists.grid(row=0, column=0)

		styleScrollBar = ttk.Style()
		styleScrollBar.theme_use('alt')
		styleScrollBar.configure("Vertical.TScrollbar", gripcount=0,
                background=ACCENT, darkcolor=ACCENT, lightcolor=ACCENT,
                troughcolor=BG, bordercolor=BG, arrowcolor="white")

		scrollBar.config(command=listOfPlaylists.yview)
		scrollBar.grid(row=0, column=1, sticky='ns')

		
		# ADDING PLAYLISTS TO THE LIST
		playlists = playlistsHandler.getPlaylistsName()

		for playlist in playlists:
			listOfPlaylists.insert(tk.END, playlist)


		# DEFINING BUTTON ACTIONS
		def cancel():
			selectPlaylistWindow.destroy()

		def select():
			playlist = listOfPlaylists.get(tk.ACTIVE)
			playlistsHandler.addToPlaylist(playlist, song_name, song_location)
			self.statusUpdate(f" '{song_name}' added to '{playlist}' playlist...")
			selectPlaylistWindow.destroy()




		# ADDING BUTTONS TO THE BUTTON FRAME
		selectButton = tk.Button(buttonFrame ,text="Select", bg=BG, fg= FG, font=('Helvetica', 10, 'bold'), borderwidth=0)
		selectButton.config(command=select)
		selectButton.grid(row=0, column=0, padx=10)

		cancelButton = tk.Button(buttonFrame ,text="Cancel", bg=BG, fg= FG, font=('Helvetica', 10, 'bold'), borderwidth=0)
		cancelButton.config(command=cancel)
		cancelButton.grid(row=0, column=1, padx=10)

		selectPlaylistWindow.mainloop()



	def newPlaylistMenu(self):
		# FUNCTION TO DISPLAY THE "CREATE NEW PLAYLIST" PROMPT
		newPlaylistMenu = tk.Toplevel(bg=BG)
		newPlaylistMenu.title("CREATE NEW PLAYLIST")
		newPlaylistMenu.resizable(False, False)

		titleFrame = tk.Frame(newPlaylistMenu, bg=ACCENT)
		titleFrame.pack(padx=10, pady=10, fill=tk.X)

		titleLabel = tk.Label(titleFrame, text="CREATE NEW PLAYLIST", bg=ACCENT, fg=FG, font=('Helvetica', 15, 'bold'))
		titleLabel.pack()

		mainFrame = tk.Frame(newPlaylistMenu, bg=BG)
		mainFrame.pack()

		label = tk.Label(mainFrame, text="ENTER THE NAME OF THE PLAYLIST", font=('Helvetica', 10), bg=BG, fg=FG)
		label.pack(padx=10, pady=10)

		entrybox = tk.Entry(mainFrame, width=50)
		entrybox.pack(padx=10)

		buttons = tk.Frame(mainFrame, bg=BG, borderwidth=0)
		buttons.pack()


		# BUTTON ACTIONS
		def cancel():
			newPlaylistMenu.destroy()

		def submit():
			playlist_name = entrybox.get()
			playlistsHandler.createNewPlaylist(playlist_name)
			self.statusUpdate(f" '{playlist_name}' has been created...")
			self.listOfSongs.insert(tk.END, playlist_name)
			newPlaylistMenu.destroy()


		# BUTTONS
		submitButton = tk.Button(buttons, text="OK", font=('Helvetica', 10), borderwidth=0, bg=BG, fg=FG)
		submitButton.config(command=submit)
		submitButton.grid(row=0, column=0, padx=10, pady=10)

		cancelButton = tk.Button(buttons, text="CANCEL", font=('Helvetica', 10), borderwidth=0, bg=BG, fg=FG)
		cancelButton.config(command=cancel)
		cancelButton.grid(row=0, column=1, padx=10, pady=10)


		newPlaylistMenu.mainloop()



	def changeSelection(self, btn):
		# MAKES MISC CHANGES WHEN DIFFERENT TABS ARE SELECTED
		if(btn == 'library'):
			self.libraryPlay = True
			self.onlinePlay = False
			self.queuePlay = False
			self.playlistPlay = False
			self.queueDispButton.config(fg=FG)
			self.libraryButton.config(fg=ACCENT)
			self.onlineButton.config(fg=FG)
			self.playlistButton.config(fg=FG)

			

		elif(btn == 'online'):
			self.libraryPlay = False
			self.onlinePlay = True
			self.queuePlay = False
			self.playlistPlay = False
			self.queueDispButton.config(fg=FG)
			self.libraryButton.config(fg=FG)
			self.onlineButton.config(fg=ACCENT)
			self.playlistButton.config(fg=FG)


		elif(btn == 'queue'):
			self.libraryPlay = False
			self.onlinePlay = False
			self.queuePlay = True
			self.playlistPlay = False
			self.queueDispButton.config(fg=ACCENT)
			self.onlineButton.config(fg=FG)
			self.libraryButton.config(fg=FG)
			self.playlistButton.config(fg=FG)

		elif(btn == 'playlists'):
			self.libraryPlay = False
			self.onlinePlay = False
			self.queuePlay = False
			self.playlistPlay = True
			self.queueDispButton.config(fg=FG)
			self.onlineButton.config(fg=FG)
			self.libraryButton.config(fg=FG)
			self.playlistButton.config(fg=ACCENT)



	def playPauseSongButton(self, event=None):
		# FUNCTION TRIGGERED WHEN THE PLAY/PAUSE BUTTON IS PRESSED
		if self.initial and not self.listOfSongs.curselection():
			pass


		elif self.isPlaying:
			self.pause()

		elif self.isPaused:
			self.resume()


		elif self.libraryPlay:
			if self.initial or len(self.queue) == 1:
				self.inititial = False
				currentSelection = self.listOfSongs.get(tk.ACTIVE)
				self.queue.clear()
				self.queue.append([currentSelection, "library"])
				self.queueFlag = 0
				self.queueHandler()


		elif self.onlinePlay:
			if self.initial or len(self.queue) == 1:
				self.initial = False
				song_name = self.listOfSongs.get(tk.ACTIVE)
				self.queue.clear()
				self.queue.append([song_name, "online"])
				print(self.queue)
				self.queueFlag = 0
				self.queueHandler()


		elif self.queuePlay:
			if not self.isPlaying and not self.isPaused:
				self.queueFlag = 0
				self.queueHandler()



	def play(self):
		# FUNCTION TO LOAD A SONG INTO THE PYGAME MIXER AND START PLAYING IT
		pygame.mixer.music.load(self.currSongPath)
		pygame.mixer.music.play(loops=0, start=self.currSongPosition)
		self.isPlaying = True
		self.playPause.config(text="||")
		self.SP_playPause.config(text="||")
		self.updateSongLength()
		self.updateAlbumArt()
		startingPos = self.currSongPosition
		self.songSlider.config(value=startingPos, from_=0, to=self.currSongLength)
		self.activateSlider()

			
	def pause(self):
		# FUNCTION TO PAUSE THE CURRENT SONG CURRENTLY LOADED ON THE MIXER 
		pygame.mixer.music.pause()
		self.pauseSlider()
		self.isPlaying = False
		self.isPaused = True
		self.playPause.config(text= "I>")
		self.SP_playPause.config(text= "I>")


	def resume(self):
		# FUNCTION TO RESUME PLAYING THE SONG CURRENTLY LOADED IN THE MIXER
		pygame.mixer.music.unpause()
		self.resumeSlider()
		self.isPlaying = True
		self.isPaused = False
		self.playPause.config(text= "||")
		self.SP_playPause.config(text= "||")



	def prevSongButton(self, event=None):
		# FUNCTION TO PLAY THE PREVIOUS SONG ON THE QUEUE
		if self.queueFlag == -1 or self.queueFlag == 0:
			if self.queueFlag == 0:
				self.statusUpdate("you are at the beginning of the queue...")
			else:
				self.statusUpdate("queue empty...")
			pass

		else:
			self.interruptSlider()
			self.currSongPosition = 0
			self.queueFlag = self.queueFlag - 1
			self.queueHandler()



	def nextSongButton(self, event=None):
		# FUNCTION TO PLAY THE NEXT SONG ON THE QUEUE
		if self.queueFlag == -1 or self.queueFlag == len(self.queue)-1:
			if self.queueFlag == len(self.queue)-1 and not self.queueFlag == -1:
				self.statusUpdate("you are at the end of the queue...")
			else:
				self.statusUpdate("queue empty...")
			pass

		else:
			self.interruptSlider()
			self.currSongPosition = 0
			self.queueFlag = self.queueFlag + 1
			self.queueHandler()



	def activateSlider(self):
		# FUNCTION THAT ACTIVATES THE SONG SLIDER
		if self.initial == True:
			pass

		else:
			currentTime = self.currSongPosition
			self.songSlider.config(value=currentTime)
			displayCurrentTime = time.strftime('%M:%S', time.gmtime(currentTime))
			self.startLabel.config(text=displayCurrentTime)
			songLength = time.strftime('%M:%S', time.gmtime(self.currSongLength))
			self.endLabel.config(text=songLength)

			self.currSongPosition = currentTime + 1

			# RESETTING THINGS WHEN THE SONG IS DONE PLAYING!!
			if(currentTime - 1 == self.currSongLength):
				self.startLabel.config(text="00:00")
				self.endLabel.config(text="00:00")
				self.songSlider.config(value=0)
				self.playPause.config(text="I>")
				self.SP_playPause.config(text="I>")
				pygame.mixer.music.stop()
				isPlaying = False
				self.currSongPosition = 0
				# FOR STARTING THE NEXT SONG
				self.queueFlag = self.queueFlag + 1
				self.queueHandler()

			else:
				self.job = self.songSlider.after(1000, self.activateSlider)



	def interruptSlider(self):
		# FUNTION TO RESET THE SLIDER IF PLAYBACK IS STOPPED
		if self.job is not None:
			self.songSlider.after_cancel(self.job)
			self.job = None

		pygame.mixer.music.stop()
	

	def pauseSlider(self):
		# FUNCTION TO PAUSE THE SLIDER IF THE SONG IS PAUSED
		if self.job is not None:
			self.songSlider.after_cancel(self.job)
			self.job = None


	def resumeSlider(self):
		# RESUMES THE SLIDER WHEN THE SONG IS UNPAUSED
		self.job = self.songSlider.after(1000, self.activateSlider)



	def slideAction(self, position):
		# FUNCTION THAT HELPS SEEK THE SONG FORWARD OR BACKWARD THROUGH THE SLIDER
		position = int(float(position))
		self.sliderPosition = position
		self.currSongPosition = self.sliderPosition
		self.interruptSlider()
		pygame.mixer.music.stop()

		self.play()


	def updateSongLength(self):
		# FOR UPDATING THE LENGTH OF THE SONG
		songMUTAGEN = MP3(self.currSongPath)
		self.currSongLength = songMUTAGEN.info.length
		self.currSongLength = int(self.currSongLength)


	def updateAlbumArt(self):
		# FOR UPDATING THE ALBUM ART AND THE SONG NAME AND THE ARTIST NAME
		try:
			metadata = audio_metadata.load(self.currSongPath)
			album_art = metadata.pictures[0].data
			stream = BytesIO(album_art)
			img = ImageTk.PhotoImage(Image.open(stream).resize((200,200)))
			self.albumArt.image = img
			self.albumArt.create_image(0, 0, anchor="nw", image=img)

			brackets = ['{', '}']
			artist = ''.join(filter(lambda i: i not in brackets, metadata.tags.artist))
			songName = ''.join(filter(lambda i : i not in brackets, metadata.tags.title))
			self.songNameLabel.config(text=songName)
			self.artistNameLabel.config(text=artist)

		except:
			self.albumArt.delete('all')
			self.songNameLabel.config(text=self.nowPlaying)
			self.artistNameLabel.config(text="unknown")


	def changeVolume(self, position):
		# FOR CHANGING THE VOLUME
		position = float(position)
		pygame.mixer.music.set_volume(position)
		
		position = int(position * 100)
		position = str(position)
		
		self.volumeLabel.config(text = f"VOLUME - {position}")


	def buttonHoverEnter(self, event, button):
		# FOR HANDLING COLOR CHANGES WHEN MOUSE HOVER OVER THE BUTTONS
		if button == 6 or button == 7 or button == 8 or button == 9:
			self.listOfButtons[button].config(bg=FG)
			self.listOfButtons[button].config(fg=BG)			

		else:
			self.listOfButtons[button].config(bg=ACCENT)
			self.listOfButtons[button].config(fg=BG)


	def buttonHoverLeave(self, event, button):
		# FOR HANDLING COLOR CHANGES WHEN MOUSE HOVER OVER THE BUTTONS
		if button == 6 or button == 7 or button == 8 or button == 9:
			if button == 6 and not self.libraryPlay:
				self.listOfButtons[button].config(bg=BG)
				self.listOfButtons[button].config(fg="white")

			elif button == 7 and not self.onlinePlay:
				self.listOfButtons[button].config(bg=BG)
				self.listOfButtons[button].config(fg="white")

			elif button == 8 and not self.queuePlay:
				self.listOfButtons[button].config(bg=BG)
				self.listOfButtons[button].config(fg="white")

			elif button == 9 and not self.playlistPlay:
				self.listOfButtons[button].config(bg=BG)
				self.listOfButtons[button].config(fg="white")

			else:
				self.listOfButtons[button].config(bg=BG)
				self.listOfButtons[button].config(fg=ACCENT)


		else:
			self.listOfButtons[button].config(bg=ACCENT)
			self.listOfButtons[button].config(fg=FG)


	def buttonHoverLeaveSP(self, event, button):
		# FOR HANDLING COLOR CHANGES WHEN MOUSE HOVER OVER THE BUTTONS
		self.listOfButtons[button].config(bg=BG)
		self.listOfButtons[button].config(fg=ACCENT)


	def addToQueue(self):
		# ADDS SELECTED SONG TO THE QUEUE
		if self.listOfSongs.curselection():
			songName = self.listOfSongs.get(tk.ACTIVE)

			if self.queueFlag == -1:
				self.queueFlag = 0
			
			if self.libraryPlay:
				self.queue.append([songName, "library"])

			elif self.onlinePlay:
				self.queue.append([songName, "online"])

			self.statusUpdate(f" '{songName}' added to the queue")

		else:
			self.statusUpdate("no song selected...")



	def deleteFromQueue(self):
		# DELETES THE SELECTED SONG FROM THE QUEUE
		if self.listOfSongs.curselection():
			song_name = self.listOfSongs.get(tk.ACTIVE)
			song_idx = self.listOfSongs.get(0, "end").index(song_name)
			self.listOfSongs.delete(song_idx)
			self.queue.pop(song_idx)

			if song_name == self.nowPlaying:
				if len(self.queue) == 0 or self.queueFlag == len(self.queue):
					self.resetEverything()
				elif not len(self.queue) == 0:
					self.queueHandler()

		else:
			self.statusUpdate("no song selected...")



	def showQueue(self):
		# TRIGGERED WHEN THE QUEUE TAB IS SELECTED; DISPLAYS THE QUEUE
		self.queueButton.config(text="Remove From queue")
		self.queueButton.config(command=self.deleteFromQueue)

		self.favouriteButton.config(text="Add To Favourites")
		self.favouriteButton.config(command=self.addToFavourite)

		self.playlistsActionButton.config(text="Add To Playlist")
		self.playlistsActionButton.config(command=self.addToPlaylist)

		self.changeSelection('queue')
		self.listOfSongs.delete(0,'end')

		for song in range(0, len(self.queue)):
			self.listOfSongs.insert(tk.END, self.queue[song][0])

		if not self.queueFlag == -1:
			self.listOfSongs.selection_clear(0, tk.END)
			self.listOfSongs.activate(self.queueFlag)
			self.listOfSongs.selection_set(self.queueFlag)



	def queueHandler(self):
		# HANDLES THE SONGS ON THE QUEUE; CHECKS IF THE SONG IS LOCATED ON THE SERVER (CALLS ONLINE HANDLER) OR THE LIBRARY (CALLS LIBRARY HANDLER)
		if self.queueFlag < len(self.queue):
			
			if self.queuePlay:	
				self.listOfSongs.selection_clear(0, tk.END)
				self.listOfSongs.activate(self.queueFlag)
				self.listOfSongs.selection_set(self.queueFlag)

			songName = self.queue[self.queueFlag][0]
			songLocation = self.queue[self.queueFlag][1]

			if self.initial:
				self.initial = False

			if songLocation == "library":
				self.libraryHandler(songName)

			elif songLocation == "online":
				self.onlineHandler(songName)



	def libraryHandler(self, song_name):
		# FOR HANDLING SONGS IN LIBRARY
		if not(song_name == self.nowPlaying):
			self.interruptSlider()
			self.currSongPath = f"data/local/{song_name}"
			self.currSongPosition = 0
			self.nowPlaying = song_name
			self.play()


		elif not self.isPlaying and song_name == self.nowPlaying:
			pygame.mixer.music.unpause()
			self.resumeSlider()
			self.isPlaying = True
			self.playPause.config(text= "||")
			self.SP_playPause.config(text= "||")

		elif self.isPlaying:
			pygame.mixer.music.pause()
			self.pauseSlider()
			self.isPlaying = False
			self.playPause.config(text= "I>")
			self.SP_playPause.config(text= "I>")



	def onlineHandler(self, song_name):
		#  FOR HANDLING SONGS LOCATED ON THE SERVER
		if self.internetConnected():
			if not(song_name == self.nowPlaying):
				self.interruptSlider()
				self.currSongPosition = 0
				song_id = cloud_backend.cloudList[song_name]

				if not self.isInCache(song_name):
					while(not cloud_backend.downloadFile(song_id, song_name)):
						pass

				self.nowPlaying = song_name
				self.currSongPath = f"data/online/{song_name}"
				self.play()


			elif not self.isPlaying and song_name == self.nowPlaying:
				pygame.mixer.music.unpause()
				self.resumeSlider()
				self.isPlaying = True
				self.playPause.config(text= "||")
				self.SP_playPause.config(text= "||")


			elif self.isPlaying:
				pygame.mixer.music.pause()
				self.pauseSlider()
				self.isPlaying = False
				self.playPause.config(text= "I>")
				self.SP_playPause.config(text= "I>")

		else:
			messagebox.showinfo("NO INTERNET", "skipping to the next song...")
			self.queueFlag = self.queueFlag + 1
			self.queueHandler()



	def isInCache(self, song_name):
		# TO CHECK IF AN ONLINE SONG IS ALREADY CACHED FOR FASTER PLAYBACK
		file_path = f"data/online/{song_name}"

		if os.path.exists(file_path):
			return True

		else:
			return False



	def resetEverything(self):
		# THIS FUNCTION RESETS EVERYTHING; TRIGGERED WHEN THE 'STOP PLAYBACK' BUTTON IS CLICKED AND THROUGH SOME OTHER FUNCTIONS.
		self.startLabel.config(text="00:00")
		self.endLabel.config(text="00:00")
		self.songSlider.config(value=0)
		self.playPause.config(text="I>")
		self.SP_playPause.config(text="I>")
		pygame.mixer.music.stop()
		self.nowPlaying = False
		self.currSongPosition = 0
		self.interruptSlider()
		self.isPlaying = False
		self.isPaused = False
		self.initial = True
		self.nowPlaying = ""
		self.currSongPath = ""
		self.currSongLength = ""
		self.currSongPosition = 0
		self.sliderPosition = 0
		self.job = None
		self.queueFlag = -1
		self.donePlaying = False
		self.songNameLabel.config(text="")
		self.artistNameLabel.config(text="")
		self.albumArt.delete('all')
		self.statusUpdate("")
		self.queue.clear()

		if self.queuePlay:
			self.listOfSongs.delete(0, 'end')



	def addSongsToLibrary(self):
		# A FUNCTION TO ADD SONGS TO THE LIBRARY
		songs_to_add = filedialog.askopenfilenames(initialdir="/" ,title="choose song(s)", filetypes=(("MP3 File", "*.mp3"), ("WAV File", "*.wav")))
		list_of_songs_to_add = list(songs_to_add)
		destination = "data/local"
		
		for song in list_of_songs_to_add:
			shutil.copy2(song, destination)

		self.refreshLibrary()
		messagebox.showinfo("SONG(S) ADDED SUCCESSFULLY", "the song(s) have been succefully added to your library....")



	def deleteSongsFromLibrary(self):
		# A FUNCTION TO DELETE SONGS FROM THE LIBRARY
		songs_to_remove = filedialog.askopenfilenames(initialdir="data/local" ,title="choose songs", filetypes=(("MP3 File", "*.mp3"), ("WAV Files", "*.wav")))
		list_of_songs_to_remove = list(songs_to_remove)

		response = messagebox.askyesno(f"DELETE SONG(S)", "the selected songs will be permanently deleted from your library... do you wish to continue?")

		if response == 1:
			for song in list_of_songs_to_remove:
				os.remove(song)
			self.refreshLibrary()
			messagebox.showinfo("DELETION SUCCESSFUL", "the selected song(s) have been succefully removed from your library...")



	def refreshLibrary(self):
		# FUNCTION TO REFRESH THE LIST OF SONGS IN LIBRARY AFTER INSERTION OR DELETION
		self.listOfSongs.delete(0,'end')
		self.songsList = os.listdir(r"data/local")
		self.library()



	def statusUpdate(self, msg):
		# UPDATES THE STATUS
		self.statusLabel.config(text=msg)



	def internetConnected(self):
		# FUNCTION CHECKS IF THE DEVICE IS CONNECTED TO THE INTERNET
		try:
			urllib.request.urlopen("http://www.google.com")
			return True

		except:
			return False



	def changeTheme(self, new_theme):
		themeHandler.changeTheme(new_theme)
		messagebox.showinfo("RESTART REQUIRED", "restart is required for the changes to take place.")



def clearCache():
	# FUNCTION TO DELETE CACHE ON EXIT AND FREE UP OTHER RESOURCES
	pygame.mixer.quit()
	dirpath = r"data\online"
	for root, dirs, files in os.walk(dirpath):
		for file in files:
			os.remove(os.path.join(root, file))


def main():
	root = tk.Tk()
	root.title("Apollo - Google Drive Music Player")
	root.iconbitmap("icon.ico")
	root.resizable(False, False)

	app = myApp(root)

	root.mainloop()

	# FOR CLEARING THE CACHE WHEN THE APP CLOSES
	atexit.register(clearCache)


if __name__ == "__main__":
	main()
