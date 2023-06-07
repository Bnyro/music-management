from yt_dlp import YoutubeDL
from flask import Flask, jsonify, request, send_from_directory, render_template
import os
import json
import threading

home = os.path.expanduser('~')
music_dir = os.path.join(home, "Music")
songs_file = os.path.join(music_dir, "songs.json")
app = Flask(__name__)

ydl_opts = {
    'format': 'opus/bestaudio/best',
    'paths': {'home': ''},
    'outtmpl': '%(title)s [%(id)s].%(ext)s',
    'extractaudio': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'opus',
        'preferredquality': '192',
    }],
}


def unique(items):
    return list(set(items))


def download(id, category):
    ydl_opts["paths"]["home"] = os.path.join(music_dir, category)

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://youtube.com/watch?v={id}"])


def restore(songs):
    for song in songs:
        try:
            download(song["id"], song["category"])
        except:
            continue


def getSongs():
    with open(songs_file, "r") as f:
        return json.load(f)


def getCategories():
    categories = unique([song["category"] for song in getSongs()])
    categories.sort()
    return categories


def getDownloadedSongs():
    songs = []
    categories = getCategories()
    for category in categories:
        dir = os.path.join(music_dir, category)
        if not os.path.exists(dir):
            continue
        for file in os.listdir(dir):
            songs.append({"name": file, "category": category})
    return {"categories": categories, "downloads": songs}


def addSong(id, category):
    songs = getSongs()
    songs.append({"id": id, "category": category})
    with open(songs_file, "w") as f:
        json.dump(songs, f)


def startRestore(songs):
    thread = threading.Thread(target=restore, args=(songs,))
    thread.start()
    return jsonify({"message": "Started"})


@app.route('/static/<path:path>')
def SendStatic(path):
    return send_from_directory('static', path)


@app.route('/files/<path:path>')
def SendFiles(path):
    return send_from_directory(music_dir, path)


@app.route("/")
def GetHome():
    return render_template('songs.html', songs=getDownloadedSongs())


@app.route('/add', methods=['POST', 'GET'])
def AddSong():
    if request.method == 'POST':
        id = request.form.get("id")[-11:]
        category = request.form.get("category")
        if not any(song["id"] == id for song in getSongs()):
            addSong(id, category)
            thread = threading.Thread(target=download, args=(id, category))
            thread.start()

    return render_template('add.html')


@app.route('/api')
def GetAll():
    return jsonify(getSongs())


@app.route('/api/categories')
def GetCategories():
    return jsonify(getCategories())


@app.route('/restore')
def RestoreAll():
    start = request.args.get("start", "0")
    songs = getSongs()[int(start):]
    return startRestore(songs)


@app.route('/restore/<category>')
def RestoreByCategory(category):
    songs = [song for song in getSongs() if song.category == category]
    return startRestore(songs)


if __name__ == '__main__':
    # Run with `gunicorn main:app -b 127.0.0.1:5000` in production
    app.run(debug=True)
