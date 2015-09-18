#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

# IMPORTS
import sys
import threading
import alsaaudio
import spotify


# Assuming a spotify_appkey.key in the current dir
session = spotify.Session()

# Process events in the background
loop = spotify.EventLoop(session)
loop.start()

# Connect an audio sink
audio = spotify.AlsaSink(session)

# Events for coordination
logged_in = threading.Event()
end_of_track = threading.Event()





def search_tracks(keyword):
	playlist = session.get_playlist('spotify:user:SPOTIFY_USER_ID:playlist:SPOTIFY_PLAYLIST_ID').load()

	search = session.search(keyword)
	search.load()
	print(len(search.tracks))
	for i in range(0, len(search.tracks)-1):
		print(search.tracks[i].load().name)
	playlist.add_tracks(search.tracks[0].load(), 1)


def play_track():
	playlist = session.get_playlist('spotify:user:SPOTIFY_USER_ID:playlist:SPOTIFY_PLAYLIST_ID').load()

	current = playlist.tracks[0]
	length = len(playlist.tracks)
	playlist.reorder_tracks(0, length)

	current_uri = str(current)
	current_uri = current_uri.replace("Track(u'", "")
	current_uri = current_uri.replace("')", "")
	#print current_uri

	track_uri = current_uri


	# Play a track
	track = session.get_track(track_uri).load()

	#current_artist = str(track.artists[0])
	#current_artist = current_artist.replace("Artist(u'", "")
	#current_artist = current_artist.replace("')", "")
	#current_artist_name = session.get_artist(current_artist).load().name.encode('UTF-8')

	#info = "Now playing " + str(track.name) + " by " + str(current_artist_name) + " (Duration: " + str(track.duration) + ")"
	#print info

	session.player.load(track)
	session.player.play()



def on_connection_state_updated(session):
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in.set()


def on_end_of_track(self):
    #end_of_track.set()
    play_track()


# Register event listeners
session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, on_connection_state_updated)
session.on(spotify.SessionEvent.END_OF_TRACK, on_end_of_track)

# LOGIN
session.login(SPOTIFY_USER_ID, SPOTIFY_USER_PASSWORT)
# Wait for Login
logged_in.wait()






search_tracks('test')
play_track()




# Wait for playback to complete or Ctrl+C
try:
    while True:
        pass
except KeyboardInterrupt:
    pass