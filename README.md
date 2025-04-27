# Video Downloader App

A Python-based video downloader application with both a Streamlit frontend UI and a Flask API backend that uses yt-dlp to extract video and audio download links.

## Features

- Professional UI with a glowing logo, input field for video URL, and download button
- Uses yt-dlp to extract video information and download links
- Displays video details (title, duration, views, uploader) and thumbnail
- Shows download options categorized by video+audio, video-only, and audio-only formats
- Includes quality information and file sizes when available
- Error handling with appropriate error messages
- API backend for integration with custom frontends
- API key authentication for security

## Project Structure

- `/app.py` - Streamlit frontend application
- `/api/` - Flask API backend
  - `/api/app.py` - Flask API server
  - `/api/requirements.txt` - API dependencies
  - `/api/example-react-component.jsx` - Example React component for integration
  - `/api/VideoDownloader.css` - CSS for the React component

## Installation

### Streamlit Frontend

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### API Backend

1. Navigate to the API directory:
   ```
   cd api
   ```
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Running the Streamlit Frontend

```
streamlit run app.py
```

The Streamlit app will be available at `http://localhost:8501`.

### Running the API Backend

```
cd api
python app.py
```

The API will be available at `http://localhost:5000`.

### API Key

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

## Connecting to a React Frontend

See the example React component in `/api/example-react-component.jsx` for a demonstration of how to connect to the API from a React application.

## Deployment

### Streamlit Frontend

This application is configured for deployment on Vercel with the included `vercel.json` and `Procfile`.

### API Backend

The API can be deployed to any platform that supports Python applications, such as:

- Heroku
- AWS Elastic Beanstalk
- Google Cloud Run
- Azure App Service

## Technologies Used

- Streamlit: For the frontend UI
- Flask: For the API backend
- yt-dlp: For video information extraction and download links
- React: For the example frontend integration
- Python 3.9

## License

MIT
