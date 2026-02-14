"""
YouTube Mashup Web Application
Student: Samiksha Bansal
ID: 102317096
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import threading
import uuid
import shutil
from pathlib import Path
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key-change-this')

# Email configuration from environment variables
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
APP_PASSWORD = os.getenv('APP_PASSWORD')
EMAIL_FROM_NAME = os.getenv('EMAIL_FROM_NAME', 'YouTube Mashup Creator')

# Flask configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
PORT = int(os.getenv('PORT', '5000'))

# Store for tracking jobs
jobs = {}


def send_email_with_attachment(to_email, singer, file_path):
    """Send email with mashup attachment"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{EMAIL_FROM_NAME} <{SENDER_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = f"Your {singer} Mashup is Ready! 🎵"
        
        # Email body
        body = f"""
Hello!

Your custom mashup of {singer}'s songs is ready!

The mashup has been attached to this email. You can also download it from the website.

Enjoy your music!

---
YouTube Mashup Creator
Student ID: 102317096
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach file
        filename = f"{singer.replace(' ', '_')}_mashup.mp3"
        
        with open(file_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {filename}'
        )
        
        msg.attach(part)
        
        # Send email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Email error: {str(e)}")
        return False


def process_mashup(job_id, singer, count, duration, email=None):
    """Background task to create mashup"""
    job = jobs[job_id]
    
    try:
        from pytubefix import YouTube, Search
        from moviepy.editor import AudioFileClip, concatenate_audioclips
        
        # Update status
        job['status'] = 'downloading'
        job['progress'] = 10
        job['current_step'] = f'Searching for {singer} videos...'
        
        # Create workspace
        workspace = Path(f"temp_{job_id}")
        vids_folder = workspace / "vids"
        audio_folder = workspace / "audio"
        cuts_folder = workspace / "cuts"
        
        for folder in [vids_folder, audio_folder, cuts_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Download videos
        job['current_step'] = 'Downloading videos from YouTube...'
        downloaded = []
        search = Search(singer)
        
        for video in search.videos:
            if len(downloaded) >= count:
                break
            try:
                yt = YouTube(video.watch_url)
                stream = yt.streams.get_audio_only()
                if stream:
                    filepath = stream.download(
                        output_path=str(vids_folder),
                        filename_prefix=f"vid_{len(downloaded)}_"
                    )
                    downloaded.append(filepath)
                    job['progress'] = 10 + (30 * len(downloaded) / count)
                    job['current_step'] = f'Downloaded {len(downloaded)}/{count} videos'
            except:
                continue
        
        if not downloaded:
            job['status'] = 'failed'
            job['error'] = 'Could not download any videos'
            return
        
        # Extract audio
        job['status'] = 'extracting'
        job['current_step'] = 'Extracting audio from videos...'
        audio_files = []
        
        for i, vid in enumerate(downloaded):
            try:
                clip = AudioFileClip(vid)
                audio_path = audio_folder / f"audio_{i}.mp3"
                clip.write_audiofile(str(audio_path), verbose=False, logger=None)
                clip.close()
                audio_files.append(str(audio_path))
                job['progress'] = 40 + (20 * (i + 1) / len(downloaded))
                job['current_step'] = f'Extracted {i+1}/{len(downloaded)} audio files'
            except:
                continue
        
        if not audio_files:
            job['status'] = 'failed'
            job['error'] = 'Could not extract audio'
            return
        
        # Trim clips
        job['status'] = 'trimming'
        job['current_step'] = f'Trimming audio to {duration} seconds...'
        trimmed = []
        
        for i, audio in enumerate(audio_files):
            try:
                clip = AudioFileClip(audio)
                length = min(duration, clip.duration)
                cut = clip.subclip(0, length)
                cut_path = cuts_folder / f"cut_{i}.mp3"
                cut.write_audiofile(str(cut_path), verbose=False, logger=None)
                clip.close()
                cut.close()
                trimmed.append(str(cut_path))
                job['progress'] = 60 + (20 * (i + 1) / len(audio_files))
                job['current_step'] = f'Trimmed {i+1}/{len(audio_files)} clips'
            except:
                continue
        
        if not trimmed:
            job['status'] = 'failed'
            job['error'] = 'Could not trim audio'
            return
        
        # Create mashup
        job['status'] = 'merging'
        job['current_step'] = 'Creating final mashup...'
        job['progress'] = 80
        
        output_path = Path('static') / 'downloads' / f"{job_id}.mp3"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        audio_clips = [AudioFileClip(c) for c in trimmed]
        final = concatenate_audioclips(audio_clips)
        final.write_audiofile(str(output_path), verbose=False, logger=None)
        
        size = os.path.getsize(output_path) / (1024 * 1024)
        
        for c in audio_clips:
            c.close()
        final.close()
        
        # Cleanup workspace
        shutil.rmtree(workspace)
        
        # Update job
        job['status'] = 'completed'
        job['progress'] = 100
        job['current_step'] = 'Mashup created successfully!'
        job['download_url'] = f"/download/{job_id}"
        job['file_size'] = f"{size:.1f} MB"
        job['duration'] = f"{final.duration:.0f}s"
        job['clips_count'] = len(trimmed)
        
        # Send email if provided
        if email and SENDER_EMAIL and APP_PASSWORD:
            job['current_step'] = 'Sending email...'
            email_sent = send_email_with_attachment(email, singer, output_path)
            job['email_sent'] = email_sent
            job['email'] = email
        else:
            job['email_sent'] = None
        
    except Exception as e:
        job['status'] = 'failed'
        job['error'] = str(e)
        job['current_step'] = f'Error: {str(e)}'
        try:
            shutil.rmtree(workspace)
        except:
            pass


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create-mashup', methods=['POST'])
def create_mashup():
    try:
        data = request.json
        
        singer = data.get('singer', '').strip()
        count = int(data.get('count', 0))
        duration = int(data.get('duration', 0))
        email = data.get('email', '').strip() or None
        
        # Validate
        if not singer:
            return jsonify({'error': 'Singer name is required'}), 400
        
        if count <= 10:
            return jsonify({'error': 'Number of videos must be greater than 10'}), 400
        
        if duration <= 20:
            return jsonify({'error': 'Duration must be greater than 20 seconds'}), 400
        
        # Validate email if provided
        if email:
            if '@' not in email or '.' not in email:
                return jsonify({'error': 'Invalid email address'}), 400
        
        # Create job
        job_id = str(uuid.uuid4())
        jobs[job_id] = {
            'id': job_id,
            'singer': singer,
            'count': count,
            'duration': duration,
            'status': 'queued',
            'progress': 0,
            'current_step': 'Initializing...',
            'created_at': datetime.now().isoformat()
        }
        
        # Start processing in background
        thread = threading.Thread(
            target=process_mashup,
            args=(job_id, singer, count, duration, email)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({'job_id': job_id}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/status/<job_id>')
def get_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job)


@app.route('/download/<job_id>')
def download(job_id):
    job = jobs.get(job_id)
    if not job or job['status'] != 'completed':
        return "File not found", 404
    
    file_path = Path('static') / 'downloads' / f"{job_id}.mp3"
    if not file_path.exists():
        return "File not found", 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"{job['singer']}_mashup.mp3"
    )


if __name__ == '__main__':
    # Create downloads folder
    Path('static/downloads').mkdir(parents=True, exist_ok=True)
    
    # Check email configuration
    if not SENDER_EMAIL or not APP_PASSWORD:
        print("\n⚠️  WARNING: Email credentials not configured!")
        print("   Email functionality will be disabled.")
        print("   Set SENDER_EMAIL and APP_PASSWORD in .env file\n")
    else:
        print(f"\n✅ Email configured: {SENDER_EMAIL}")
    
    print("\n" + "="*60)
    print("  YouTube Mashup Web Application")
    print("  Student: Samiksha Bansal")
    print("  ID: 102317096")
    print("="*60)
    print(f"\n  Server running at: http://localhost:{PORT}")
    print("  Press Ctrl+C to stop")
    print("\n" + "="*60 + "\n")
    
    debug_mode = FLASK_ENV == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=PORT)