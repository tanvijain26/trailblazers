import React, { useState } from 'react';
import axios from 'axios';

const ReelUpload = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [videoFile, setVideoFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleVideoChange = (e) => {
    setVideoFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!videoFile) {
      alert('Please select a video file');
      return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('video', videoFile);

    try {
      setLoading(true);
      const response = await axios.post('/api/reels/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setMessage('Reel uploaded successfully!');
      setLoading(false);
      setTitle('');
      setDescription('');
      setVideoFile(null);
    } catch (error) {
      console.error('Error uploading the reel:', error);
      setMessage('Failed to upload reel');
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Upload Reel</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Title:</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Description:</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Video File:</label>
          <input type="file" onChange={handleVideoChange} accept="video/*" required />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Uploading...' : 'Upload Reel'}
        </button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default ReelUpload;