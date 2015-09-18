#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from socket import *

# Welcome Message
print 
print "#############################"
print "###  WELCOME TO SPYFY  ###"
print "#############################"
print
print "STARTING THE SYSTEM..."


# IMPORTS
import sys
import threading
import alsaaudio
import spotify
import pyaudio
import urllib2
import time
import wave
import speech_recognition as sr
print "- Got all Imports"


reload(sys)
sys.setdefaultencoding("utf-8")


track_end = True


# Assuming a spotify_appkey.key in the current dir
session = spotify.Session()
print("- Initialized Session")

# Process events in the background
loop = spotify.EventLoop(session)
loop.start()
print("- Added and started EventLoop")

# Connect an audio sink
audio = spotify.AlsaSink(session)
print("- Connected the Audio Sink")

# Events for coordination
logged_in = threading.Event()
end_of_track = threading.Event()
print("- Added libspotify events")


r = sr.Recognizer(language = str("de-DE"))
r.energy_threshold = 0
print "- Initialized Speech Recognizer"





def record_wav():
	try:
		FORMAT = pyaudio.paInt16
		CHANNELS = 1
		RATE = 44100
		CHUNK = 8192
		RECORD_SECONDS = 6
		WAVE_OUTPUT_FILENAME = "temp.wav"
		 
		audio = pyaudio.PyAudio()
		 
		# start Recording
		stream = audio.open(format=FORMAT, channels=CHANNELS,
		                rate=RATE, input=True,
		                frames_per_buffer=CHUNK)
		print "recording..."
		frames = []
		 
		for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
		    data = stream.read(CHUNK)
		    frames.append(data)
		print "finished recording"
		 
		 
		# stop Recording
		stream.stop_stream()
		stream.close()
		audio.terminate()
		 
		waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
		waveFile.setnchannels(CHANNELS)
		waveFile.setsampwidth(audio.get_sample_size(FORMAT))
		waveFile.setframerate(RATE)
		waveFile.writeframes(b''.join(frames))
		waveFile.close()
	except:
		print "recording failed"





def listen():

	global track_end
	track_end = False

	recognized = False
	text = ""
	record_wav()
	filename = "temp.wav"
	filename = filename.encode('utf-8')

	try:
		with sr.WavFile(filename) as source: 
		    try:
		    	print("Listening...")
		    	audio = r.record(source)              		# listen for the first phrase and extract it into audio data
		    	print("Listened")
		    except: 
		    	print("Listening timed out")
	except:
		print "Listening to file not possible"

	#try:
	#	os.remove(filename)
	#except:
	#	print "can not remove temp.wav"

	# Try to recognize recorded soung
	try:
		text = r.recognize(audio)
		recognized = True
	except IndexError:                                  # the API key didn't work
	    print("No internet connection")
	except KeyError:                                    # the API key didn't work
	    print("Invalid API key or quota maxed out")
	except LookupError:                            		# speech is unintelligible
	    print("Could not understand audio")
	except: 
		print("General Error")

	# analyze if recognized
	if recognized is True:
		try:
			playlist = session.get_playlist('spotify:user:SPOTIFY_USER_ID:playlist:SPOTIFY_PLAYLIST_ID').load()
			print("You said " + text) 		# recognize speech using Google Speech Recognition
			words = text.split(" ")
			for i in range(0, len(words)):
				search = session.search(str(words[i]))
				search.load()
				playlist.add_tracks(search.tracks[0].load(), 1)
				current_artist = str(search.tracks[0].load().artists[0])
				current_artist = current_artist.replace("Artist(u'", "")
				current_artist = current_artist.replace("')", "")
				current_artist_name = session.get_artist(current_artist).load().name
				print("Added '" + search.tracks[0].load().name + "' by '" + current_artist_name + "' for keyword '" + words[i] + "' to Playlist")
		except:
			print "Adding to playlist failed"

	track_end = True









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

	# Songtitle
	title = track.name

	# Artist Name
	current_artist = str(track.artists[0])
	current_artist = current_artist.replace("Artist(u'", "")
	current_artist = current_artist.replace("')", "")
	current_artist_name = session.get_artist(current_artist).load().name

	# Calculate Song Duration
	ms	= track.duration
	seconds = ms/1000
	minutes = 0
	if seconds > 60:
		minutes = seconds/60
		seconds = seconds-(minutes*60)

	# Putting together Info-Message
	info = "Now playing '" + title + "' by '" + current_artist_name + "' (Duration: " + "%02d" % minutes + ":" + "%02d" % seconds + ")"

	# Print Info-Message
	print
	print info

	# Play Track
	session.player.load(track)
	session.player.play()



def on_connection_state_updated(session):
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in.set()



def on_end_of_track(self):
    #end_of_track.set()
    if track_end is True:
    	print("Track finished")
    	print
    	listen()
    	play_track()



def internet_on():
    try:
        response=urllib2.urlopen('http://google.de',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False



def start_process():

	#try:
	#	os.remove(filename)
	#except:
	#	print "can not remove temp.wav"

	if internet_on() is True:
		try:
			# LOGIN
			session.login(SPOTIFY_USER_ID, SPOTIFY_USER_PASSWORT)
			# Wait for Login
			logged_in.wait()
			print("- Logged in succesfully")
			print

			print "Start Playback now"
			play_track()
		except:
			print "Couldn't connect!"
			time.sleep(10)
			start_process()
	else:
		print "No internet connection. Retry in ten seconds"
		time.sleep(10)
		start_process()

    



# Register event listeners
session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, on_connection_state_updated)
session.on(spotify.SessionEvent.END_OF_TRACK, on_end_of_track)
print("- Added event listeners")

start_process()












# Wait for playback to complete or Ctrl+C
try:
    while True:
        pass
except KeyboardInterrupt:
    pass