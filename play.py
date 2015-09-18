#!/usr/bin/env python

import spotify
import sys


session = spotify.Session()
session.login(spotify_id, spotify_passwort)

session.process_events()
session.connection.state

session.process_events()
session.connection.state

print session.user
