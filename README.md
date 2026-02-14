<div align="center">

# 🎵 YouTube Mashup Creator

### *Create seamless audio mashups from YouTube videos*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Educational-orange.svg)](LICENSE)

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎯 Core Functionality
- 🔍 Search & download YouTube videos by artist
- 🎵 Extract high-quality audio streams
- ✂️ Smart audio trimming & processing
- 🔗 Seamless clip concatenation

</td>
<td width="50%">

### 🌐 Web Interface
- 📊 Real-time progress tracking
- 🎨 Modern, responsive design
- 📧 Optional email delivery
- 🎧 Built-in audio preview

</td>
</tr>
</table>

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Youtube-mashup-creator.git
cd Youtube-mashup-creator

# Install dependencies
pip install -r requirements.txt
```

> **Prerequisites:** Python 3.8+, FFmpeg

---

## 🖥️ CLI Usage

### Quick Start

```bash
python 102317096.py <singer_name> <num_videos> <duration> <output_file>
```

### Example

```bash
python 102317096.py "Arijit Singh" 15 30 output.mp3
```

### Parameters

| Parameter | Description | Constraint |
|-----------|-------------|------------|
| `singer_name` | Artist/Singer name | Use quotes for spaces |
| `num_videos` | Number of videos to download | Must be > 10 |
| `duration` | Duration per clip (seconds) | Must be > 20 |
| `output_file` | Output filename | `.mp3` extension |

---

## 🌐 Web Application

### Setup & Run

```bash
# Navigate to web directory
cd mashup_website

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

🌍 Open your browser at: **http://localhost:5000**

### Email Configuration (Optional)

Create a `.env` file in the `mashup_website` directory:

```env
SENDER_EMAIL=your-email@gmail.com
APP_PASSWORD=your-app-password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
```

> 💡 **Tip:** Use Gmail App Password, not your regular password

---

## 📸 Screenshots

<div align="center">

### Main Interface
<img width="900" alt="YouTube Mashup Creator Interface" src="https://github.com/user-attachments/assets/dc33e973-cb9d-4c87-bf0e-8261612c04cf" />

### Processing & Download
<img width="730" alt="Mashup Processing" src="https://github.com/user-attachments/assets/5055905b-9b1a-4fd6-9b2b-975e6a22c3ee" />

</div>

---

## 📦 Dependencies

| Package | Purpose | Version |
|---------|---------|---------|
| `pytubefix` | YouTube video downloads | Latest |
| `moviepy` | Audio processing & editing | 1.0.3 |
| `Flask` | Web framework | 3.0.0 |
| `imageio-ffmpeg` | FFmpeg integration | Latest |

---

## 🏗️ Project Structure

```
Youtube-mashup-creator/
├── 102317096.py              # CLI application
├── requirements.txt          # CLI dependencies
├── mashup_website/           # Web application
│   ├── app.py               # Flask server
│   ├── requirements.txt     # Web dependencies
│   ├── static/              # CSS, JS, downloads
│   └── templates/           # HTML templates
└── README.md                # Documentation
```

---

## 👨‍💻 Author

<div align="center">

**Samiksha Bansal**  
Student ID: `102317096`

---

Made with ❤️ for music lovers

</div>
