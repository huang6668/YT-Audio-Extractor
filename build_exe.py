import os
import PyInstaller.__main__

if __name__ == '__main__':
    PyInstaller.__main__.run([
        'app.py',
        '--name=YT2Audio',
        '--windowed', # 隐藏控制台窗口 (可选，如果你想看到日志可以去掉)
        '--onefile',  # 打包为单文件，而不是文件夹
        '--icon=NONE', # 这里可以指定 .ico 图标文件
        '--add-data=static;static', # 将前端文件打包进去
        '--add-data=ffmpeg.exe;.', # 将当前目录下的 ffmpeg.exe 打包进去
        '--add-data=ffprobe.exe;.', 
        '--clean'
    ])
