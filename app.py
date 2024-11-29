import os
import socket
import string
import webbrowser
from ctypes import windll

import tinytag
from flask import Flask, request, render_template
from jinja2 import Environment
from mutagen import File
from mutagen.id3 import TRCK, TIT2, TALB, TPE1

app = Flask(__name__)
username = os.environ['username']
home = os.path.abspath(f'C:\\Users\\{username}\\')
# reference: https://stackoverflow.com/questions/827371/is-there-a-way-to-list-all-the-available-windows-drives
drives = []
bitmask = windll.kernel32.GetLogicalDrives()
for letter in string.ascii_uppercase:
    drive_root_path = str(letter + ':')
    if bitmask & 1:
        drives.append((drive_root_path, drive_root_path))
    bitmask >>= 1
# reference end


def none_to_empty(value):
    return '' if value is None else value


env = Environment()
env.filters['none_to_empty'] = none_to_empty


def get_folder(path):
    path_split = path.split('\\')
    path_cascade = []
    for i in range(len(path_split)):
        path_cascade.append((
            path_split[i],
            r'\\'.join(path_split[:i+1])
        ))
    if path.endswith(':'):  # root directory of a disk
        # os.listdir('C:') will return current folder
        # os.listdir('C:\\') is correct
        path += '\\'
    if os.path.isdir(path):
        sub_folders = []
        isdir = True
        try:
            for x in os.listdir(path):
                x_full_path = r'\\'.join(path_split) + r'\\' + x
                if os.path.isdir(x_full_path) or os.path.isfile(x_full_path):
                    sub_folders.append((x, x_full_path))
        except PermissionError:
            sub_folders = None
            isdir = False
    elif os.path.isfile(path):
        sub_folders = None
        isdir = False
    else:
        sub_folders = None
        isdir = False
    return {'path_cascade': path_cascade, 'sub_folders': sub_folders, 'isdir': isdir,
            'current_folder': path, 'drives': drives}


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/fs', methods=['GET'])
def cd():
    path = request.args.get('path', type=str, default=home)
    container_id = request.args.get('container_id', type=str)
    kwargs = get_folder(path)
    return render_template(
        'fs_widget.html', container_id=container_id, web_path='/fs', **kwargs)


@app.route('/view_album', methods=['POST'])
def view_album():
    data = request.get_json()
    album_path = data.get('album_path')
    if not album_path:
        return "The program didn't get the folder path."
    metas = []
    for file_dir, _, file_names in os.walk(album_path):
        for file_name in file_names:
            file_path = os.path.join(file_dir, file_name)
            # "try" has 0 cost if the file is supported. In a folder where most files are
            # supported, using try-except is better than "if tinytag.TinyTag.is_supported".
            try:
                meta = tinytag.TinyTag.get(file_path)
            except (tinytag.tinytag.UnsupportedFormatError, PermissionError):
                continue
            if file_name.endswith('.wav'):
                continue
            meta.filepath = file_path
            meta.filename = file_name
            metas.append(meta)
    return render_template('album.html', metas=metas, n=len(metas))

@app.route('/modify_meta', methods=['POST'])
def modify_meta():
    data = request.form
    n = data.get('total_files', default=0, type=int)
    messages = []
    for i in range(n):
        i1 = i + 1
        file_path = data.get(f'filepath-{i1}')
        file = File(file_path, easy=True)
        if file is None:
            messages.append(f"File type of {file_path} is unsupported.")
            continue
        track_number = data.get(f'track-{i1}', '', str)
        title = data.get(f'title-{i1}', '', str)
        album = data.get(f'album-{i1}', '', str)
        artist = data.get(f'artist-{i1}', '', str)
        if not file.tags:
            file.add_tags()
            messages.append(f"{file_path} don't have tags, and is now added.")
        if track_number:
            try:
                file.tags['tracknumber'] = track_number
            except TypeError:
                file.tags.add(TRCK(encoding=3, text=track_number))
                messages.append(f"{file_path} don't have track number attribute, now added.")
        elif 'tracknumber' in file.tags:
            del file.tags['tracknumber']
            messages.append(f"{file_path} track number attribute is deleted.")
        try:
            file['title'] = title
        except TypeError:
            file.tags.add(TIT2(encoding=3, text=title))
            messages.append(f"{file_path} don't have title attribute, now added.")
        try:
            file['album'] = album
        except TypeError:
            file.tags.add(TALB(encoding=3, text=album))
            messages.append(f"{file_path} don't have album attribute, now added.")
        try:
            file['artist'] = artist
        except TypeError:
            file.tags.add(TPE1(encoding=3, text=artist))
            messages.append(f"{file_path} don't have artist attribute, now added.")
        try:
            file.save()
            messages.append(f"Successfully save {file_path}")
        except Exception as e:
            messages.append(f"Fail to save {file_path} Reason: {e}")
    messages = "".join("<li>" + m + "</li>" for m in messages)
    return messages


def find_available_port(start_port: int, tries: int = 100):
    """
    Find the first available port from {start_port} to {start_port + tries}
    :param start_port: The port that the program starts to scan, if it's occupied, the
    program will scan {start_port + 1}. If it's occupied again, try the next one...
    :param tries: Default 100, the maximum trying times from the start port.
    :return:
    """
    for i in range(tries):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(("127.0.0.1", start_port + i))
            s.close()
            return start_port + i
        except OSError:
            pass
    raise Exception(f"Tried {tries} times, no available port from {start_port} to "
                    f"{start_port + tries}.")


if __name__ == '__main__':
    port = find_available_port(5000)
    webbrowser.open_new_tab(f'http://localhost:{port}')
    app.run(port=port)
