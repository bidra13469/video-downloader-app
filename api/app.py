import os
import json
import uuid
import secrets
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
from datetime import timedelta
from functools import wraps

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Generate a secure API key if not already set
API_KEY = os.environ.get('VIDEO_DOWNLOADER_API_KEY')
if not API_KEY:
    # Generate a secure random API key
    API_KEY = secrets.token_urlsafe(32)
    print(f"\n[INFO] Generated new API key: {API_KEY}")
    print("[INFO] You should set this as an environment variable 'VIDEO_DOWNLOADER_API_KEY' for production use.\n")

# API key authentication decorator
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get('X-API-Key')
        if provided_key and provided_key == API_KEY:
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized: Invalid or missing API key"}), 401
    return decorated_function

# Function to extract video info using yt-dlp
def get_video_info(video_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'best',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return info
    except yt_dlp.utils.DownloadError as e:
        error_message = str(e)
        return {"error": error_message}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

# Function to format duration
def format_duration(duration_seconds):
    return str(timedelta(seconds=duration_seconds))

# Function to format view count
def format_views(views):
    if views >= 1000000:
        return f"{views/1000000:.1f}M views"
    elif views >= 1000:
        return f"{views/1000:.1f}K views"
    else:
        return f"{views} views"

# Root endpoint
@app.route('/')
def index():
    return jsonify({
        "name": "Video Downloader API",
        "version": "1.0.0",
        "description": "API for downloading videos from various platforms using yt-dlp"
    })

# API key endpoint - for testing only, not for production
@app.route('/api/get-key', methods=['GET'])
def get_api_key():
    return jsonify({"api_key": API_KEY})

# Video info endpoint
@app.route('/api/video-info', methods=['POST'])
@require_api_key
def video_info():
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({"error": "URL is required"}), 400
    
    video_url = data['url']
    info = get_video_info(video_url)
    
    if "error" in info:
        return jsonify({"error": info["error"]}), 400
    
    # Extract only the necessary information to reduce response size
    formatted_info = {
        "id": info.get('id'),
        "title": info.get('title'),
        "thumbnail": info.get('thumbnail'),
        "duration": format_duration(info.get('duration', 0)),
        "view_count": format_views(info.get('view_count', 0)),
        "uploader": info.get('uploader'),
        "formats": []
    }
    
    # Process video formats
    for format in info.get('formats', []):
        if 'url' in format:
            format_info = {
                "format_id": format.get('format_id'),
                "ext": format.get('ext', 'mp4'),
                "height": format.get('height'),
                "width": format.get('width'),
                "filesize": format.get('filesize'),
                "filesize_formatted": f"{format.get('filesize', 0)/1024/1024:.1f} MB" if format.get('filesize') else None,
                "vcodec": format.get('vcodec'),
                "acodec": format.get('acodec'),
                "url": format.get('url'),
                "format_note": format.get('format_note'),
                "abr": format.get('abr')
            }
            formatted_info["formats"].append(format_info)
    
    return jsonify(formatted_info)

# Download links endpoint
@app.route('/api/download-links', methods=['POST'])
@require_api_key
def download_links():
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({"error": "URL is required"}), 400
    
    video_url = data['url']
    info = get_video_info(video_url)
    
    if "error" in info:
        return jsonify({"error": info["error"]}), 400
    
    # Organize formats by type
    video_with_audio = []
    video_only = []
    audio_only = []
    
    for format in info.get('formats', []):
        if 'url' in format:
            format_info = {
                "format_id": format.get('format_id'),
                "ext": format.get('ext', 'mp4'),
                "height": format.get('height'),
                "filesize": format.get('filesize'),
                "filesize_formatted": f"{format.get('filesize', 0)/1024/1024:.1f} MB" if format.get('filesize') else None,
                "url": format.get('url'),
                "format_note": format.get('format_note'),
                "abr": format.get('abr')
            }
            
            vcodec = format.get('vcodec')
            acodec = format.get('acodec')
            
            if vcodec != 'none' and acodec != 'none':
                if 'height' in format and format['height']:
                    format_info["quality"] = f"{format['height']}p"
                    video_with_audio.append(format_info)
            elif vcodec != 'none' and acodec == 'none':
                if 'height' in format and format['height']:
                    format_info["quality"] = f"{format['height']}p"
                    video_only.append(format_info)
            elif vcodec == 'none' and acodec != 'none':
                abr = format.get('abr', '')
                format_info["quality"] = f"{abr}kbps" if abr else "Unknown quality"
                audio_only.append(format_info)
    
    return jsonify({
        "video_with_audio": video_with_audio,
        "video_only": video_only[:5],  # Limit to top 5 formats
        "audio_only": audio_only[:3]   # Limit to top 3 formats
    })

if __name__ == '__main__':
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
