# Video Downloader App

A Python-based video downloader application with a Streamlit frontend UI that uses yt-dlp to extract video and audio download links.

## Features

- Simple UI with a logo, input field for video URL, and download button
- Uses yt-dlp to extract video information and download links
- Displays video details (title, duration, views, uploader) and thumbnail
- Shows download options categorized by video+audio, video-only, and audio-only formats
- Includes quality information and file sizes when available
- Error handling with appropriate error messages

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application locally:
```
streamlit run app.py
```

## Deployment

This application is configured for deployment on Vercel with the included `vercel.json` and `Procfile`.

## Technologies Used

- Streamlit: For the frontend UI
- yt-dlp: For video information extraction and download links
- Python 3.9

## License

MIT
