import streamlit as st
import yt_dlp
import re
from datetime import timedelta
import base64
from pathlib import Path

# Set page configuration
st.set_page_config(
    page_title="Pro Video Downloader",
    page_icon="📹",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional UI
def local_css():
    css = """
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #4F46E5;
        --secondary-color: #7C3AED;
        --background-color: #F9FAFB;
        --card-background: #FFFFFF;
        --text-color: #1F2937;
        --accent-color: #10B981;
        --error-color: #EF4444;
        --border-radius: 10px;
        --box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* Global styles */
    .main {
        background-color: var(--background-color);
        padding: 2rem;
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 {
        color: var(--text-color);
        font-weight: 700;
    }

    /* Logo animation */
    @keyframes glow {
        0% {
            filter: drop-shadow(0 0 5px rgba(79, 70, 229, 0.6));
        }
        50% {
            filter: drop-shadow(0 0 15px rgba(124, 58, 237, 0.8));
        }
        100% {
            filter: drop-shadow(0 0 5px rgba(79, 70, 229, 0.6));
        }
    }

    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 1.5rem;
    }

    .logo {
        animation: glow 3s infinite;
        width: 120px;
        height: 120px;
    }

    /* Card styles */
    .card {
        background-color: var(--card-background);
        border-radius: var(--border-radius);
        box-shadow: var(--box-shadow);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border-left: 4px solid var(--primary-color);
        transition: transform 0.2s ease-in-out;
    }

    .card:hover {
        transform: translateY(-2px);
    }

    /* Input field */
    .stTextInput > div > div > input {
        border-radius: var(--border-radius);
        border: 1px solid #E5E7EB;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.2s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2);
    }

    /* Button styles */
    .stButton > button {
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Download links */
    .download-btn {
        display: inline-block;
        background: linear-gradient(90deg, #3B82F6 0%, #2563EB 100%);
        color: white;
        text-decoration: none;
        padding: 0.5rem 1rem;
        border-radius: var(--border-radius);
        margin: 0.25rem 0;
        transition: all 0.2s ease;
        font-size: 0.9rem;
    }

    .download-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Section headers */
    .section-header {
        border-bottom: 2px solid #E5E7EB;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
        color: var(--primary-color);
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 1rem;
        font-size: 0.9rem;
        color: #6B7280;
        border-top: 1px solid #E5E7EB;
        margin-top: 2rem;
    }

    /* Success and error messages */
    .success-msg {
        background-color: rgba(16, 185, 129, 0.1);
        border-left: 4px solid var(--accent-color);
        padding: 1rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
    }

    .error-msg {
        background-color: rgba(239, 68, 68, 0.1);
        border-left: 4px solid var(--error-color);
        padding: 1rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
    }

    /* Video details */
    .video-details {
        display: flex;
        gap: 1rem;
        align-items: flex-start;
    }

    .video-info {
        flex: 1;
    }

    .video-info p {
        margin: 0.5rem 0;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: var(--primary-color) !important;
    }

    /* Tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }

    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #333;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }

    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Apply custom CSS
local_css()

# Create SVG logo with glowing effect
def get_logo_svg():
    svg = """
    <svg width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="60" cy="60" r="50" fill="url(#paint0_linear)" />
        <path d="M50 40L80 60L50 80V40Z" fill="white"/>
        <circle cx="60" cy="60" r="55" stroke="url(#paint1_linear)" stroke-width="2" stroke-dasharray="4 4"/>
        <defs>
            <linearGradient id="paint0_linear" x1="10" y1="10" x2="110" y2="110" gradientUnits="userSpaceOnUse">
                <stop stop-color="#4F46E5"/>
                <stop offset="1" stop-color="#7C3AED"/>
            </linearGradient>
            <linearGradient id="paint1_linear" x1="10" y1="10" x2="110" y2="110" gradientUnits="userSpaceOnUse">
                <stop stop-color="#4F46E5"/>
                <stop offset="1" stop-color="#7C3AED"/>
            </linearGradient>
        </defs>
    </svg>
    """
    return svg

# Display logo and app title
st.markdown(f'<div class="logo-container">{get_logo_svg()}</div>', unsafe_allow_html=True)
st.markdown('<h1 style="text-align: center; margin-bottom: 0.5rem;">Pro Video Downloader</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #6B7280; margin-bottom: 2rem;">Download high-quality videos from YouTube and other platforms</p>', unsafe_allow_html=True)

# URL input card
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<h3>Enter Video URL</h3>', unsafe_allow_html=True)
url = st.text_input("", placeholder="https://www.youtube.com/watch?v=...", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

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

# Download button
if st.button("Get Download Links", key="download_btn"):
    if not url:
        st.markdown('<div class="error-msg">Please enter a valid URL</div>', unsafe_allow_html=True)
    else:
        with st.spinner("Fetching video information..."):
            info = get_video_info(url)

            if "error" in info:
                st.markdown(f'<div class="error-msg">Error: {info["error"]}</div>', unsafe_allow_html=True)
            else:
                # Display video information
                st.markdown('<div class="success-msg">Video information retrieved successfully!</div>', unsafe_allow_html=True)

                # Video details section
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<h3 class="section-header">Video Details</h3>', unsafe_allow_html=True)

                col1, col2 = st.columns([1, 2])

                # Thumbnail in column 1
                if 'thumbnail' in info:
                    col1.image(info['thumbnail'], use_container_width=True)

                # Video details in column 2
                col2.markdown(f"<p><strong>Title:</strong> {info['title']}</p>", unsafe_allow_html=True)
                if 'duration' in info:
                    col2.markdown(f"<p><strong>Duration:</strong> {format_duration(info['duration'])}</p>", unsafe_allow_html=True)
                if 'view_count' in info:
                    col2.markdown(f"<p><strong>Views:</strong> {format_views(info['view_count'])}</p>", unsafe_allow_html=True)
                if 'uploader' in info:
                    col2.markdown(f"<p><strong>Uploader:</strong> {info['uploader']}</p>", unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

                # Download links section
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<h3 class="section-header">Download Options</h3>', unsafe_allow_html=True)

                # Video formats
                video_formats = [f for f in info['formats'] if f.get('vcodec') != 'none' and f.get('acodec') != 'none']
                if video_formats:
                    st.markdown('<h4>Video with Audio</h4>', unsafe_allow_html=True)
                    for i, format in enumerate(video_formats):
                        if 'height' in format and format['height']:
                            quality = f"{format['height']}p"
                            ext = format.get('ext', 'mp4')
                            filesize = format.get('filesize')
                            filesize_str = f" - {filesize/1024/1024:.1f} MB" if filesize else ""

                            st.markdown(f'<a href="{format["url"]}" class="download-btn" target="_blank">Download {quality} {ext.upper()}{filesize_str}</a>', unsafe_allow_html=True)

                # Video-only formats
                video_only = [f for f in info['formats'] if f.get('vcodec') != 'none' and f.get('acodec') == 'none']
                if video_only:
                    st.markdown('<h4>Video Only (No Audio)</h4>', unsafe_allow_html=True)
                    for i, format in enumerate(video_only[:5]):  # Limit to top 5 formats
                        if 'height' in format and format['height']:
                            quality = f"{format['height']}p"
                            ext = format.get('ext', 'mp4')
                            filesize = format.get('filesize')
                            filesize_str = f" - {filesize/1024/1024:.1f} MB" if filesize else ""

                            st.markdown(f'<a href="{format["url"]}" class="download-btn" target="_blank">Download {quality} {ext.upper()}{filesize_str}</a>', unsafe_allow_html=True)

                # Audio-only formats
                audio_only = [f for f in info['formats'] if f.get('vcodec') == 'none' and f.get('acodec') != 'none']
                if audio_only:
                    st.markdown('<h4>Audio Only</h4>', unsafe_allow_html=True)
                    for i, format in enumerate(audio_only[:3]):  # Limit to top 3 formats
                        abr = format.get('abr', '')
                        quality_text = f"{abr}kbps" if abr else "Unknown quality"
                        ext = format.get('ext', 'mp3')
                        filesize = format.get('filesize')
                        filesize_str = f" - {filesize/1024/1024:.1f} MB" if filesize else ""

                        st.markdown(f'<a href="{format["url"]}" class="download-btn" target="_blank">Download Audio {quality_text} {ext.upper()}{filesize_str}</a>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

# Help section
with st.expander("How to use"):
    st.markdown("""
    1. Paste a video URL from YouTube, Vimeo, or other supported platforms
    2. Click the "Get Download Links" button
    3. Wait for the video information to be fetched
    4. Choose your preferred format and quality
    5. Click the download link to save the video
    """)

# Footer
st.markdown('<div class="footer">Made with ❤️ using Streamlit and yt-dlp | © 2025 Pro Video Downloader</div>', unsafe_allow_html=True)
