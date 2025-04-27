import os
import json
import uuid
import secrets
import re
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

# Function to detect platform from URL
def detect_platform(url):
    url = url.lower()

    platforms = {
        'youtube': r'(youtube\.com|youtu\.be)',
        'tiktok': r'(tiktok\.com|vm\.tiktok\.com)',
        'instagram': r'(instagram\.com|instagr\.am)',
        'facebook': r'(facebook\.com|fb\.com|fb\.watch)',
        'twitter': r'(twitter\.com|x\.com)',
        'vimeo': r'vimeo\.com',
        'reddit': r'reddit\.com',
        'dailymotion': r'dailymotion\.com',
        'twitch': r'twitch\.tv',
        'soundcloud': r'soundcloud\.com',
        'pinterest': r'pinterest\.(com|ca)',
        'linkedin': r'linkedin\.com'
    }

    for platform, pattern in platforms.items():
        if re.search(pattern, url):
            return platform

    return 'unknown'

# Function to get platform-specific options
def get_platform_options(platform, url):
    # Base options for all platforms
    options = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'best',
        'extractor_args': {},
        'cookiefile': None,
        'socket_timeout': 30,  # Increase timeout for slow servers
        'nocheckcertificate': True,  # Skip HTTPS certificate validation
    }

    # Platform-specific configurations
    if platform == 'tiktok':
        # TikTok specific options
        options['extractor_args']['tiktok'] = {
            'api_hostname': 'api16-normal-c-useast1a.tiktokv.com',
            'app_version': '20.2.1',
            'manifest_app_version': '20.2.1',
            'device_id': '7165118698651100677',
            'channel': 'tiktok_web',
            'app_name': 'tiktok_web',
        }
        # Add user agent for TikTok
        options['user_agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

    elif platform == 'instagram':
        # Instagram specific options
        options['user_agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        options['cookiesfrombrowser'] = ('chrome',)

    elif platform == 'facebook':
        # Facebook specific options
        options['user_agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

    return options

# Function to extract video info using yt-dlp with enhanced platform support
def get_video_info(video_url):
    # Detect platform
    platform = detect_platform(video_url)

    # Get platform-specific options
    ydl_opts = get_platform_options(platform, video_url)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            # Add platform information to the result
            info['platform'] = platform
            return info
    except yt_dlp.utils.DownloadError as e:
        error_message = str(e)

        # Provide more user-friendly error messages based on platform
        if platform == 'tiktok' and 'Unable to download webpage' in error_message:
            return {
                "error": "Could not download this TikTok video. This might be due to TikTok's restrictions or the video being private.",
                "platform": platform,
                "original_error": error_message,
                "suggestions": [
                    "Make sure the TikTok video is public and not deleted",
                    "Try using the share link directly from the TikTok app",
                    "Some TikTok videos may be region-restricted"
                ]
            }
        elif platform == 'instagram' and 'login' in error_message.lower():
            return {
                "error": "This Instagram content requires login. The API cannot access private or login-required content.",
                "platform": platform,
                "original_error": error_message,
                "suggestions": [
                    "Make sure the Instagram content is public",
                    "Try using a different link from Instagram"
                ]
            }
        else:
            return {
                "error": f"Could not download from {platform.capitalize()}: {error_message}",
                "platform": platform,
                "original_error": error_message
            }
    except Exception as e:
        return {
            "error": f"An unexpected error occurred: {str(e)}",
            "platform": platform
        }

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
        "version": "1.1.0",
        "description": "API for downloading videos from various platforms using yt-dlp",
        "supported_platforms": list(get_supported_platforms().keys())
    })

# Get supported platforms endpoint
@app.route('/api/supported-platforms', methods=['GET'])
def supported_platforms():
    return jsonify(get_supported_platforms())

# Function to get supported platforms with examples
def get_supported_platforms():
    return {
        "youtube": {
            "name": "YouTube",
            "example_urls": [
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "https://youtu.be/dQw4w9WgXcQ"
            ],
            "supported_features": ["video", "audio", "thumbnails", "metadata"]
        },
        "tiktok": {
            "name": "TikTok",
            "example_urls": [
                "https://www.tiktok.com/@username/video/1234567890123456789",
                "https://vm.tiktok.com/ABCDEF/"
            ],
            "supported_features": ["video", "thumbnails", "metadata"],
            "notes": "Some TikTok videos may be region-restricted or require authentication"
        },
        "instagram": {
            "name": "Instagram",
            "example_urls": [
                "https://www.instagram.com/p/ABC123/",
                "https://www.instagram.com/reel/ABC123/"
            ],
            "supported_features": ["video", "thumbnails", "metadata"],
            "notes": "Private Instagram content is not supported"
        },
        "facebook": {
            "name": "Facebook",
            "example_urls": [
                "https://www.facebook.com/watch?v=1234567890123456",
                "https://fb.watch/ABC123/"
            ],
            "supported_features": ["video", "thumbnails", "metadata"],
            "notes": "Private Facebook content is not supported"
        },
        "twitter": {
            "name": "Twitter/X",
            "example_urls": [
                "https://twitter.com/username/status/1234567890123456789",
                "https://x.com/username/status/1234567890123456789"
            ],
            "supported_features": ["video", "thumbnails", "metadata"]
        },
        "vimeo": {
            "name": "Vimeo",
            "example_urls": [
                "https://vimeo.com/1234567890"
            ],
            "supported_features": ["video", "audio", "thumbnails", "metadata"]
        },
        "reddit": {
            "name": "Reddit",
            "example_urls": [
                "https://www.reddit.com/r/subreddit/comments/abcdef/title/"
            ],
            "supported_features": ["video", "thumbnails", "metadata"]
        },
        "dailymotion": {
            "name": "Dailymotion",
            "example_urls": [
                "https://www.dailymotion.com/video/x12345"
            ],
            "supported_features": ["video", "audio", "thumbnails", "metadata"]
        },
        "twitch": {
            "name": "Twitch",
            "example_urls": [
                "https://www.twitch.tv/videos/1234567890",
                "https://clips.twitch.tv/ClipName"
            ],
            "supported_features": ["video", "thumbnails", "metadata"]
        },
        "soundcloud": {
            "name": "SoundCloud",
            "example_urls": [
                "https://soundcloud.com/artist/track-name"
            ],
            "supported_features": ["audio", "thumbnails", "metadata"]
        }
    }

# API key endpoint - for testing only, not for production
@app.route('/api/get-key', methods=['GET'])
def get_api_key():
    return jsonify({"api_key": API_KEY})

# Function to get the best thumbnail URL
def get_best_thumbnail(info):
    if not info:
        return None

    # For TikTok, Instagram, etc. that might have different thumbnail structures
    if 'thumbnail' in info and info['thumbnail']:
        return info['thumbnail']

    # Some platforms provide thumbnails in a list
    if 'thumbnails' in info and info['thumbnails']:
        # Sort thumbnails by resolution (if available) and return the highest quality
        thumbnails = sorted(
            [t for t in info['thumbnails'] if 'url' in t],
            key=lambda x: x.get('width', 0) * x.get('height', 0) if x.get('width') and x.get('height') else 0,
            reverse=True
        )
        if thumbnails:
            return thumbnails[0]['url']

    return None

# Function to safely get duration
def safe_get_duration(info):
    if not info:
        return 0

    # Direct duration field
    if 'duration' in info and info['duration'] is not None:
        return info['duration']

    # Some platforms use duration_string
    if 'duration_string' in info:
        try:
            # Parse duration string like "5:20" into seconds
            parts = info['duration_string'].split(':')
            if len(parts) == 2:  # MM:SS
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:  # HH:MM:SS
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        except:
            pass

    return 0

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
        return jsonify(info), 400  # Return the full error object with suggestions

    # Get platform
    platform = info.get('platform', detect_platform(video_url))

    # Extract only the necessary information to reduce response size
    formatted_info = {
        "id": info.get('id'),
        "title": info.get('title'),
        "thumbnail": get_best_thumbnail(info),
        "duration": format_duration(safe_get_duration(info)),
        "view_count": format_views(info.get('view_count', 0)),
        "uploader": info.get('uploader'),
        "platform": platform,
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

    # Add platform-specific information
    if platform == 'tiktok':
        formatted_info["author"] = info.get('uploader') or info.get('creator') or info.get('uploader_id')
        formatted_info["description"] = info.get('description') or ""

    elif platform == 'instagram':
        formatted_info["author"] = info.get('uploader') or info.get('uploader_id')
        formatted_info["description"] = info.get('description') or ""

    elif platform == 'twitter':
        formatted_info["author"] = info.get('uploader') or info.get('uploader_id')
        formatted_info["description"] = info.get('description') or ""
        formatted_info["retweet_count"] = info.get('retweet_count', 0)
        formatted_info["like_count"] = info.get('like_count', 0)

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
        return jsonify(info), 400  # Return the full error object with suggestions

    # Get platform
    platform = info.get('platform', detect_platform(video_url))

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

    # Sort formats by quality (height for video, bitrate for audio)
    video_with_audio.sort(key=lambda x: x.get('height', 0) or 0, reverse=True)
    video_only.sort(key=lambda x: x.get('height', 0) or 0, reverse=True)
    audio_only.sort(key=lambda x: x.get('abr', 0) or 0, reverse=True)

    # For TikTok and Instagram, sometimes we need to handle direct URLs differently
    if platform in ['tiktok', 'instagram', 'twitter'] and not video_with_audio and 'url' in info:
        # Add the direct URL as a format
        direct_format = {
            "format_id": "direct",
            "ext": "mp4",
            "height": info.get('height', 720),
            "filesize": None,
            "filesize_formatted": None,
            "url": info['url'],
            "format_note": "Direct link",
            "quality": f"{info.get('height', 720)}p"
        }
        video_with_audio.append(direct_format)

    response = {
        "video_with_audio": video_with_audio,
        "video_only": video_only[:5],  # Limit to top 5 formats
        "audio_only": audio_only[:3],  # Limit to top 3 formats
        "platform": platform
    }

    # Add platform-specific information
    if platform == 'tiktok':
        response["title"] = info.get('title', '')
        response["author"] = info.get('uploader') or info.get('creator') or info.get('uploader_id', '')
        response["thumbnail"] = get_best_thumbnail(info)

    return jsonify(response)

if __name__ == '__main__':
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
