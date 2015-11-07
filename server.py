#!/usr/bin/env python3

from flask import Flask,make_response,abort
from mutagen.easyid3 import EasyID3
from mutagen import File
from threading import Timer
import sqlite3 as sqlite
import os, sys
app = Flask(__name__)

# Set musics directory
def error():
  print('USAGE: server.py <MUSIC>\n  <MUSIC> must be the absolute path of you musics folder.\n')
  exit()

### CONFIGURATIONS ###
# Database file used for indexing songs
DB_FILE = os.path.abspath('songs.db')

# The cover file that used when no cover is available.
# Replace with False to disable it
NO_COVER = os.path.abspath('no_cover.jpg')

# Host ip or name. you often don't need to change it
HOST = '0.0.0.0'

# Note: for port <= 1024, you need superuser access.
PORT = 80

# app debug. disable it for releases.
app.debug = True


class Database:

  def __init__(self):
    self.open()

  def open(self):
    self.conn = sqlite.connect(DB_FILE)
    self.cur = self.conn.cursor()

  def create_table(self):
    self.cur.executescript('''
        DROP TABLE IF EXISTS Songs;
        CREATE TABLE Songs(Artist TEXT, Album TEXT, Title TEXT, Path TEXT);
        ''')
    self.conn.commit()

  def _songs_table_exist(self):
    query = 'SELECT COUNT(*) FROM sqlite_master WHERE type="table" AND name="Songs";'
    self.cur.execute(query)
    self.conn.commit()
    result = self.cur.fetchone()[0]
    return bool(result)

  def count_records(self):
    if not self._songs_table_exist():
      return 0

    query = 'SELECT COUNT(*) FROM Songs'
    self.cur.execute(query)
    self.conn.commit()
    count = self.cur.fetchone()[0]
    return int(count)

  def __len__(self):
    return self.count_records()

  def _insert_song(self,song):
    query = 'INSERT INTO Songs VALUES(?, ?, ?, ?)'
    self.cur.execute(query,
        (
          song.artist,
          song.album,
          song.title,
          song.path,
          ),
        )

  def insert(self,song):
    self._insert_song(song)
    self.conn.commit()

  def batch_insert(self, songs):
    for song in songs:
      self._insert_song(song)
    self.conn.commit()

  def get_song(self, artist, album, title='any'):
    if title == 'any':
      query = 'SELECT Path FROM Songs WHERE Artist=? AND Album=?'
      self.cur.execute(query,(artist,album))
    else:
      query = 'SELECT Path FROM Songs WHERE Artist=? AND Album=? AND Title=?'
      self.cur.execute(query,(artist,album,title))
  
    self.conn.commit()
    path = self.cur.fetchone()
    return Song(artist,album,title,path)

  def close(self):
    self.conn.close()

  def __del__(self):
    self.close()

class Song:

  def clean_arg(string):
    string = str(string)
    if string.endswith(']'):
      return string[2:-2]
    elif string.endswith(')'):
      return string[2:-3]
    else:
      return string

  def __init__(self, artist, album, title, path):
    self.artist = Song.clean_arg(artist)
    self.album = Song.clean_arg(album)
    self.title = Song.clean_arg(title)
    self.path = Song.clean_arg(path)

  def __str__(self):
    return '{} by {} from {}'.format(self.title, self.artist, self.album)



def song_from_path(path):
  song = EasyID3(path)
  try:
    artist = song['artist']
  except:
    artist = ''

  try:
    album  = song['album']
  except:
    album = ''

  try:
    title = song['title']
  except:
    title = ''

  return Song(artist=artist,
      album=album,
      title=title,
      path=path)

def list_songs():
  songs = []
  for root, dirs, files in os.walk(MUSIC_DIR):
    for file in files:
      if file.endswith(".mp3"):
        path = os.path.join(root, file)
        song = song_from_path(path)
        songs.append(song)
  return songs


def update_database(db):
  Timer(10 * 60, update_database, [db]).start()

  songs = list_songs()
  if len(db) == len(songs):
    # no need to update
    return

  db.create_table()
  db.batch_insert(songs)

def init_database():
  if not os.path.isfile(DB_FILE):
    db = Database()
    print('Indexing musics. Please wait...')
    try:
      update_database(db)
    finally:
      db.close()

def get_cover_art(song):
  if song.path == 'None':
    return None
  file = File(song.path)
  APIC = None
  for key in file.keys():
    if 'APIC:' in key:
      APIC = key
  if APIC is None:
    return None
  artwork = file.tags[APIC].data
  return artwork
     
def generate_response(Artist, Album, Title='any'):
  db = Database()
  song = db.get_song(Artist, Album, Title)
  db.close()
  cover_raw = get_cover_art(song)
  if cover_raw is None:
    if NO_COVER == False:
      abort(404)
    else:
      with open(NO_COVER, 'rb') as f:
        cover_raw = f.read()
  resp = make_response(cover_raw)
  resp.content_type = "image/jpeg"
  return resp

def is_title(title):
  return not title in ['cover','folder','%placeholder_filename']


@app.route("/<Artist>/<Album>/Covers/front.jpg")
def album_cover(Artist, Album):
  return generate_response(Artist, Album)

@app.route("/<Artist>/<Album>/artwork/front.jpg")
def album_artwork(Artist, Album):
  return generate_response(Artist, Album)

@app.route("/<Artist>/<Album>/<Title>.jpg")
def song_cover_jpg(Artist, Album, Title):
  if is_title(Title):
    return generate_response(Artist, Album, Title)
  else:
    return generate_response(Artist, Album)

def main():
  global MUSIC_DIR

  if len(sys.argv) != 2:
    error()

  MUSIC_DIR = str(sys.argv[-1])
  if not os.path.exists(MUSIC_DIR):
    print('{} doesn\'t exist.\n'.format(MUSIC_DIR))
    error()
  
  init_database()

  try:
    app.run(host=HOST,port=PORT)
  except PermissionError:
    print('ERROR: can\'t open port {}: you have not enough premissions.'.format(PORT))
    exit()

if __name__ == '__main__':
  main()
