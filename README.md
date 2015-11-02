# MPDroid-CoverServer
Python application for serving covers used by [MPDroid](https://github.com/abarisain/dmix).
Uses [Flask](http://flask.pocoo.org/) microframework for network communications and [mutagen](https://bitbucket.org/lazka/mutagen) for extracting informations and cover images from audio files.

## Installation
Install Flask and mutagen with:
```
$ sudo pip3 install flask mutagen
```

Clone repo:
```
$ git clone https://github.com/mamins1376/MPDroid-CoverServer.git
```

Run it. by default, this app uses port 80 on your machine, which needs superuser access level:
```
$ sudo ./server.py <MUSICS DIRECTORY>
```

It may take some minutes, depending on count of your music files.