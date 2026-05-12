import os
import threading
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import uuid
import re

app = Flask(__name__, static_folder='static')
CORS(app)

DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

tasks = {}

def download_audio_task(task_id, url, metadata):
    # Absolute path to local ffmpeg
    ffmpeg_path = os.path.abspath('ffmpeg.exe') 
    
    def hook(d):
        if d['status'] == 'downloading':
            try:
                percent_str = d.get('_percent_str', '')
                # Remove ANSI escape sequences
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                percent_str = ansi_escape.sub('', percent_str).strip()
                percent_str = percent_str.replace('%', '')
                percent = float(percent_str)
                tasks[task_id]['progress'] = percent
                tasks[task_id]['status'] = 'downloading'
            except Exception as e:
                pass
        elif d['status'] == 'finished':
            tasks[task_id]['status'] = 'processing'
            tasks[task_id]['progress'] = 100

    outtmpl = os.path.join(DOWNLOAD_DIR, f"{task_id}_%(title)s.%(ext)s")
    
    audio_format = metadata.get('audioFormat', 'mp3') if metadata else 'mp3'
    
    # Determine yt-dlp format string and postprocessor codec
    if audio_format == 'm4a':
        ydl_format = 'bestaudio[ext=m4a]/bestaudio'
        preferredcodec = 'm4a'
    elif audio_format == 'alac':
        ydl_format = 'bestaudio/best'
        preferredcodec = 'alac'
    else:
        ydl_format = 'bestaudio/best'
        preferredcodec = 'mp3'

    ydl_opts = {
        'format': ydl_format,
        'ffmpeg_location': ffmpeg_path,
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': preferredcodec, 'preferredquality': '0'}, 
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'},
        ],
        'writethumbnail': True,
        'outtmpl': outtmpl,
        'progress_hooks': [hook],
        'quiet': True,
        'no_warnings': True
    }
    
    ffmpeg_args = []
    if metadata:
        if metadata.get('title'):
            ffmpeg_args.extend(['-metadata', f'title={metadata["title"]}'])
        if metadata.get('artist'):
            ffmpeg_args.extend(['-metadata', f'artist={metadata["artist"]}'])
        if metadata.get('album'):
            ffmpeg_args.extend(['-metadata', f'album={metadata["album"]}'])
            
    if ffmpeg_args:
        ydl_opts['postprocessor_args'] = {'ffmpeg': ffmpeg_args}

    import shutil
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Find the actual output file name
            filename = ydl.prepare_filename(info)
            # The extension will be changed to the preferred codec by postprocessor
            base, _ = os.path.splitext(filename)
            
            # For ALAC, yt-dlp usually puts it in an m4a container
            ext = 'm4a' if preferredcodec == 'alac' else preferredcodec
            final_filename = base + f'.{ext}'
            
            # Just in case yt-dlp names it .alac
            if not os.path.exists(final_filename) and preferredcodec == 'alac':
                final_filename = base + '.alac'
                
            tasks[task_id]['file'] = final_filename
            tasks[task_id]['title'] = metadata.get('title') if metadata and metadata.get('title') else info.get('title', 'Audio')
            
            # Auto Import to Apple Music
            if metadata and metadata.get('autoImport') and metadata.get('importPath'):
                import_path = metadata.get('importPath')
                if os.path.isdir(import_path):
                    try:
                        shutil.copy2(final_filename, import_path)
                        tasks[task_id]['title'] += " (已推送到 Apple Music)"
                    except Exception as e:
                        print("Auto import failed:", e)
            
            tasks[task_id]['status'] = 'completed'
    except Exception as e:
        tasks[task_id]['status'] = 'error'
        tasks[task_id]['error'] = str(e)


@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/download', methods=['POST'])
def start_download():
    data = request.json
    url = data.get('url')
    metadata = data.get('metadata', {})
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        'status': 'starting',
        'progress': 0,
        'file': None,
        'title': None,
        'error': None
    }
    
    thread = threading.Thread(target=download_audio_task, args=(task_id, url, metadata))
    thread.start()
    
    return jsonify({"task_id": task_id})

@app.route('/api/status/<task_id>')
def check_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)

@app.route('/api/file/<task_id>')
def get_file(task_id):
    task = tasks.get(task_id)
    if not task or task['status'] != 'completed':
        return "File not ready or not found", 404
    
    filepath = task['file']
    filename = os.path.basename(filepath)
    # Extract original title from filename
    original_title = filename.split('_', 1)[1] if '_' in filename else filename
    
    return send_file(filepath, as_attachment=True, download_name=original_title)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
