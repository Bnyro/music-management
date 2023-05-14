from yt_dlp import YoutubeDL
from flask import Flask, jsonify, request, send_from_directory, render_template
import os
import json
import threading

home = os.path.expanduser('~')
app = Flask(__name__)

ydl_opts = {
    'format': 'opus/bestaudio/best',
    'paths': {'home': ''},
    'outtmpl': '%(title)s.%(ext)s',
    'quiet': True,
    'extractaudio': True
}


def download(id, category):
    ydl_opts["paths"]["home"] = os.path.join(
        home, "Music", category.capitalize())

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://youtube.com/watch?v={id}"])


def restore():
    for song in getSongs():
        download(song["id"], song["category"])


def getSongs():
    with open("songs.json", "r") as f:
        return json.load(f)


def addSong(id, category):
    songs = getSongs() + {"id": id, "category": category}
    with open("songs.json", "w") as f:
        json.dump(songs, f)


@app.route('/static/<path:path>')
def SendStatic(path):
    return send_from_directory('static', path)


@app.route('/', methods=['POST', 'GET'])
def GetHome():
    if request.method == 'POST':
        id = request.form.get("id")[-11:]
        category = request.form.get("category")
        if not any(song["id"] == id for song in getSongs()):
            addSong(id, category)
            thread = threading.Thread(target=download, args=(id, category))
            thread.start()

    return render_template('index.html')


@app.route('/api')
def GetAll():
    return jsonify(getSongs())


@app.route('/restore')
def RestoreAll():
    thread = threading.Thread(target=restore)
    thread.start()
    return jsonify({"message": "Started"})


if __name__ == '__main__':
    # Run with `gunicorn main:app -b 127.0.0.1:5000` in production
    app.run(debug=True)
