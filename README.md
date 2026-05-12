# YT Audio Extractor

![GitHub License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)

一个轻量级、高颜值的本地 Web 应用程序，专门用于从 YouTube 链接中提取最高音质的音频，并自动嵌入视频缩略图作为专辑封面。

## ✨ 核心特性 (Features)

- 🎵 **极致音质无损提取**：支持输出 **FLAC** (无损转换避免二次折损)、**M4A** (YouTube 原生音频直取)、**MP3** (高兼容性 VBR 0 级)。
- 🖼️ **自动专辑封面**：自动抓取 YouTube 视频最高清的封面，并完美嵌入到下载的音频文件中。
- ✏️ **自定义元数据 (Metadata)**：支持在下载前手动覆盖或填写**歌曲名**、**歌手**、**专辑**等 ID3 标签。
- 🎨 **现代化 UI 设计**：采用毛玻璃 (Glassmorphism) 风格、具有动态进度反馈的精美 Web 界面。
- 📦 **支持打包为 EXE**：附带一键构建脚本，可将整个项目连同前端和 FFmpeg 打包为单个独立的 Windows 可执行文件。

## 🚀 快速开始 (Quick Start)

### 1. 安装依赖
本项目推荐使用 `uv` 进行环境管理，运行以下命令安装所需依赖：
```bash
uv init
uv add flask yt-dlp flask-cors pyinstaller
```

### 2. 获取 FFmpeg 核心组件
音频的提取和封面嵌入依赖于 FFmpeg。我们在项目中内置了自动下载脚本：
```bash
python install_ffmpeg.py
```
*(这会在当前目录自动下载并解压适配 Windows 的 `ffmpeg.exe` 与 `ffprobe.exe`)*

### 3. 运行应用
双击根目录下的 `run.bat`，或者在终端运行：
```bash
uv run app.py
```
随后在浏览器中打开：[http://127.0.0.1:5000](http://127.0.0.1:5000)

## 📦 打包为独立 EXE (Build Executable)

如果您想把软件发给没有 Python 环境的朋友，可以一键将其打包成 EXE 独立文件：
```bash
uv run build_exe.py
```
打包完成后，即可在 `dist/` 目录下找到 `YT2Audio.exe` 文件。

## 📂 目录结构 (Structure)

```text
yt2am/
├── app.py                 # Flask 后端主程序
├── install_ffmpeg.py      # FFmpeg 自动下载器
├── build_exe.py           # PyInstaller 打包配置脚本
├── run.bat                # 一键启动脚本
├── static/                # 前端静态文件 (HTML/CSS/JS)
├── downloads/             # 默认的音频输出目录
└── pyproject.toml         # UV 依赖配置
```
