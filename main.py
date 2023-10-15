from yt_dlp import YoutubeDL
from flask import Flask, jsonify, request, send_from_directory, render_template
import os
import threading

# Create and init the needed folder structure
home = os.path.expanduser('~')
music_dir = os.path.join(home, "Music")
src_dir = os.path.join(music_dir, "src")

# Create directories that do not yet exist
for directory in (music_dir, src_dir):
    if not os.path.exists(directory):
        os.makedirs(directory)


# Configuration for yt-dlp
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


app = Flask(__name__)


def download(id, category):
    ydl_opts["paths"]["home"] = os.path.join(music_dir, category)

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://youtube.com/watch?v={id}"])


def restore(songs):
    for song in songs:
        try:
            download(song["id"], song["category"])
        except Exception:
            continue


def getCategories():
    categories = []

    for filename in os.listdir(src_dir):
        path = os.path.join(src_dir, filename)
        if os.path.isfile(path):
            categories.append(filename)

    categories.sort()
    return categories


def getSongs():
    songs = []

    for category in getCategories():
        with open(os.path.join(src_dir, category), "r") as f:
            for videoId in f.read().splitlines():
                songs.append(
                    {
                        'category': category,
                        'id': videoId,
                    }
                )

    return songs


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
    with open(os.path.join(src_dir, category), "a") as f:
        f.write(f"{id}\n")


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


@app.route('/', methods=['POST', 'GET'])
def AddSong():
    if request.method == 'POST':
        id = request.form.get("id")[-11:]
        category = request.form.get("category")
        if not any(song["id"] == id for song in getSongs()):
            addSong(id, category)
            thread = threading.Thread(target=download, args=(id, category))
            thread.start()

    return render_template('add.html')


@app.route("/play")
def GetPlayer():
    return render_template('songs.html', songs=getDownloadedSongs())


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
    songs = [song for song in getSongs() if song["category"] == category]
    return startRestore(songs)


if __name__ == '__main__':
    app.run(debug=True)
