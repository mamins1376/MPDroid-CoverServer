# MPDroid-CoverServer
Python application for serving covers used by [MPDroid](https://github.com/abarisain/dmix), using [Flask](http://flask.pocoo.org/) microframework. files' metadata extracted using [mutagen](https://bitbucket.org/lazka/mutagen)

# Installation
Install Flask and mutagen with:
$ sudo pip3 install flask mutagen

Clone repo:
$ git clone https://github.com/mamins1376/MPDroid-CoverServer.git

Run it. by default, MPDroid uses port 80 on your machine, which needs superuser access level:
$ sudo ./server.py <MUSICS DIRECTORY>

it may take some minutes, depending on count of your music files.
