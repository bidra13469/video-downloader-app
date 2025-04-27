import React, { useState } from 'react';
import axios from 'axios';
import './VideoDownloader.css';

// API configuration
const API_URL = 'http://localhost:5000';
const API_KEY = 'your_api_key'; // Replace with your actual API key

const VideoDownloader = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [videoInfo, setVideoInfo] = useState(null);
  const [downloadLinks, setDownloadLinks] = useState(null);

  const handleUrlChange = (e) => {
    setUrl(e.target.value);
  };

  const fetchVideoInfo = async () => {
    if (!url) {
      setError('Please enter a valid URL');
      return;
    }

    setLoading(true);
    setError(null);
    setVideoInfo(null);
    setDownloadLinks(null);

    try {
      // Fetch video information
      const infoResponse = await axios.post(
        `${API_URL}/api/video-info`,
        { url },
        {
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
          }
        }
      );

      setVideoInfo(infoResponse.data);

      // Fetch download links
      const linksResponse = await axios.post(
        `${API_URL}/api/download-links`,
        { url },
        {
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
          }
        }
      );

      setDownloadLinks(linksResponse.data);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while fetching video information');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="video-downloader">
      <div className="logo-container">
        {/* Your logo SVG here */}
        <h1>Pro Video Downloader</h1>
      </div>

      <div className="input-container">
        <input
          type="text"
          value={url}
          onChange={handleUrlChange}
          placeholder="Enter video URL..."
          disabled={loading}
        />
        <button onClick={fetchVideoInfo} disabled={loading}>
          {loading ? 'Loading...' : 'Get Download Links'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {videoInfo && (
        <div className="video-info">
          <h2>Video Details</h2>
          <div className="video-details">
            {videoInfo.thumbnail && (
              <div className="thumbnail">
                <img src={videoInfo.thumbnail} alt={videoInfo.title} />
              </div>
            )}
            <div className="info">
              <h3>{videoInfo.title}</h3>
              <p><strong>Duration:</strong> {videoInfo.duration}</p>
              <p><strong>Views:</strong> {videoInfo.view_count}</p>
              <p><strong>Uploader:</strong> {videoInfo.uploader}</p>
            </div>
          </div>
        </div>
      )}

      {downloadLinks && (
        <div className="download-options">
          <h2>Download Options</h2>
          
          {downloadLinks.video_with_audio.length > 0 && (
            <div className="format-section">
              <h3>Video with Audio</h3>
              <div className="links-grid">
                {downloadLinks.video_with_audio.map((format, index) => (
                  <a
                    key={`va-${index}`}
                    href={format.url}
                    className="download-link"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {format.quality} {format.ext.toUpperCase()}
                    {format.filesize_formatted && ` - ${format.filesize_formatted}`}
                  </a>
                ))}
              </div>
            </div>
          )}

          {downloadLinks.video_only.length > 0 && (
            <div className="format-section">
              <h3>Video Only (No Audio)</h3>
              <div className="links-grid">
                {downloadLinks.video_only.map((format, index) => (
                  <a
                    key={`vo-${index}`}
                    href={format.url}
                    className="download-link"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {format.quality} {format.ext.toUpperCase()}
                    {format.filesize_formatted && ` - ${format.filesize_formatted}`}
                  </a>
                ))}
              </div>
            </div>
          )}

          {downloadLinks.audio_only.length > 0 && (
            <div className="format-section">
              <h3>Audio Only</h3>
              <div className="links-grid">
                {downloadLinks.audio_only.map((format, index) => (
                  <a
                    key={`ao-${index}`}
                    href={format.url}
                    className="download-link"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Audio {format.quality} {format.ext.toUpperCase()}
                    {format.filesize_formatted && ` - ${format.filesize_formatted}`}
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default VideoDownloader;
