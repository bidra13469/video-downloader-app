import streamlit as st
import yt_dlp
import re
from datetime import timedelta

# Set page configuration
st.set_page_config(
    page_title="Video Downloader",
    page_icon="📹",
    layout="centered"
)

# App title and logo
st.title("📹 Video Downloader")
st.markdown("### Download videos from YouTube and other platforms")
st.markdown("---")

# URL input
url = st.text_input("Enter video URL:", placeholder="https://www.youtube.com/watch?v=...")

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
if st.button("Get Download Links"):
    if not url:
        st.error("Please enter a valid URL")
    else:
        with st.spinner("Fetching video information..."):
            info = get_video_info(url)
            
            if "error" in info:
                st.error(f"Error: {info['error']}")
            else:
                # Display video information
                st.success("Video information retrieved successfully!")
                
                # Video details section
                st.markdown("## Video Details")
                col1, col2 = st.columns([1, 2])
                
                # Thumbnail in column 1
                if 'thumbnail' in info:
                    col1.image(info['thumbnail'], use_column_width=True)
                
                # Video details in column 2
                col2.markdown(f"**Title:** {info['title']}")
                if 'duration' in info:
                    col2.markdown(f"**Duration:** {format_duration(info['duration'])}")
                if 'view_count' in info:
                    col2.markdown(f"**Views:** {format_views(info['view_count'])}")
                if 'uploader' in info:
                    col2.markdown(f"**Uploader:** {info['uploader']}")
                
                # Download links section
                st.markdown("## Download Options")
                
                # Video formats
                video_formats = [f for f in info['formats'] if f.get('vcodec') != 'none' and f.get('acodec') != 'none']
                if video_formats:
                    st.markdown("### Video with Audio")
                    for i, format in enumerate(video_formats):
                        if 'height' in format and format['height']:
                            quality = f"{format['height']}p"
                            ext = format.get('ext', 'mp4')
                            filesize = format.get('filesize')
                            filesize_str = f" - {filesize/1024/1024:.1f} MB" if filesize else ""
                            
                            st.markdown(f"[Download {quality} {ext.upper()}{filesize_str}]({format['url']})")
                
                # Video-only formats
                video_only = [f for f in info['formats'] if f.get('vcodec') != 'none' and f.get('acodec') == 'none']
                if video_only:
                    st.markdown("### Video Only (No Audio)")
                    for i, format in enumerate(video_only[:5]):  # Limit to top 5 formats
                        if 'height' in format and format['height']:
                            quality = f"{format['height']}p"
                            ext = format.get('ext', 'mp4')
                            filesize = format.get('filesize')
                            filesize_str = f" - {filesize/1024/1024:.1f} MB" if filesize else ""
                            
                            st.markdown(f"[Download {quality} {ext.upper()}{filesize_str}]({format['url']})")
                
                # Audio-only formats
                audio_only = [f for f in info['formats'] if f.get('vcodec') == 'none' and f.get('acodec') != 'none']
                if audio_only:
                    st.markdown("### Audio Only")
                    for i, format in enumerate(audio_only[:3]):  # Limit to top 3 formats
                        abr = format.get('abr', '')
                        quality_text = f"{abr}kbps" if abr else "Unknown quality"
                        ext = format.get('ext', 'mp3')
                        filesize = format.get('filesize')
                        filesize_str = f" - {filesize/1024/1024:.1f} MB" if filesize else ""
                        
                        st.markdown(f"[Download Audio {quality_text} {ext.upper()}{filesize_str}]({format['url']})")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and yt-dlp")
