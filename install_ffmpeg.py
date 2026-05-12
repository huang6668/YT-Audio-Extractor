import os
import urllib.request
import zipfile

def install_ffmpeg():
    if os.path.exists('ffmpeg.exe') and os.path.exists('ffprobe.exe'):
        print("ffmpeg already installed.")
        return
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    print("Downloading ffmpeg...")
    urllib.request.urlretrieve(url, "ffmpeg.zip")
    print("Extracting ffmpeg...")
    with zipfile.ZipFile("ffmpeg.zip", 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith('ffmpeg.exe') or file.endswith('ffprobe.exe'):
                filename = os.path.basename(file)
                with open(filename, 'wb') as f:
                    f.write(zip_ref.read(file))
    os.remove("ffmpeg.zip")
    print("ffmpeg installed successfully.")

if __name__ == '__main__':
    install_ffmpeg()
