# Video Downloader API

A Flask-based API for downloading videos from various platforms using yt-dlp.

## Features

- Fetch video information from YouTube and other platforms
- Get download links for different video and audio formats
- API key authentication for security
- CORS support for cross-origin requests

## Installation

1. Clone the repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Starting the API server

```bash
python app.py
```

The API will be available at `http://localhost:5000`.

### Setting an API Key

For security, you should set an API key as an environment variable:

```bash
# On Windows
set VIDEO_DOWNLOADER_API_KEY=your_secure_api_key

# On Linux/Mac
export VIDEO_DOWNLOADER_API_KEY=your_secure_api_key
```

If you don't set an API key, a random one will be generated and printed to the console when the server starts.

## API Endpoints

### GET /

Returns basic information about the API.

### GET /api/get-key

Returns the current API key (for testing only, not for production).

### POST /api/video-info

Fetches detailed information about a video.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=..."
}
```

**Headers:**
```
X-API-Key: your_api_key
```

**Response:**
```json
{
  "id": "video_id",
  "title": "Video Title",
  "thumbnail": "thumbnail_url",
  "duration": "00:05:30",
  "view_count": "1.5M views",
  "uploader": "Channel Name",
  "formats": [
    {
      "format_id": "22",
      "ext": "mp4",
      "height": 720,
      "width": 1280,
      "filesize": 10485760,
      "filesize_formatted": "10.0 MB",
      "vcodec": "avc1.64001F",
      "acodec": "mp4a.40.2",
      "url": "download_url",
      "format_note": "720p",
      "abr": 128
    },
    // ...more formats
  ]
}
```

### POST /api/download-links

Returns organized download links for different video and audio formats.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=..."
}
```

**Headers:**
```
X-API-Key: your_api_key
```

**Response:**
```json
{
  "video_with_audio": [
    {
      "format_id": "22",
      "ext": "mp4",
      "height": 720,
      "filesize": 10485760,
      "filesize_formatted": "10.0 MB",
      "url": "download_url",
      "format_note": "720p",
      "abr": 128,
      "quality": "720p"
    },
    // ...more formats
  ],
  "video_only": [
    // Video-only formats
  ],
  "audio_only": [
    // Audio-only formats
  ]
}
```

## Connecting to a React Frontend

To connect this API to a React frontend:

1. Make sure CORS is enabled (it is by default in this API)
2. Use the API key in your requests from the React app
3. Use fetch or axios to make requests to the API endpoints

Example React code:

```javascript
const API_URL = 'http://localhost:5000';
const API_KEY = 'your_api_key';

async function getVideoInfo(url) {
  try {
    const response = await fetch(`${API_URL}/api/video-info`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      },
      body: JSON.stringify({ url })
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch video info');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching video info:', error);
    throw error;
  }
}
```

## Security Considerations

- Keep your API key secure and don't expose it in client-side code
- For production, consider using environment variables for the API key
- Implement rate limiting for production use
- Consider adding user authentication for a multi-user system
