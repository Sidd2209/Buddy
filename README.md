# Buddy - Random Video Chat Application

A modern video chat application similar to Omegle, built with React, WebRTC, and Flask.

## Features

- 🎥 Real-time video chat with strangers
- 🎤 Audio and video controls
- 🔄 Next chat functionality
- 🎨 Modern, responsive UI
- 🔒 Secure peer-to-peer connections

## Tech Stack

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Flask + Socket.IO
- **Real-time Communication**: WebRTC + Socket.IO
- **Deployment**: Render

## Local Development

### Prerequisites

- Node.js (v16 or higher)
- Python 3.8 or higher
- Modern browser with camera/microphone support

### Setup

1. Clone the repository
2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

4. Start the application:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

5. Open your browser and navigate to `http://localhost:5173`

## Deployment on Render

### Option 1: Using render.yaml (Recommended)

1. Push your code to a Git repository (GitHub, GitLab, etc.)
2. Connect your repository to Render
3. Render will automatically detect the `render.yaml` file and deploy both services

### Option 2: Manual Deployment

#### Backend Service

1. Create a new **Web Service** on Render
2. Connect your Git repository
3. Configure the service:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python wsgi.py`
   - **Environment**: Python

#### Frontend Service

1. Create a new **Static Site** on Render
2. Connect your repository
3. Configure the service:
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
   - **Environment Variable**: 
     - Key: `VITE_BACKEND_URL`
     - Value: Your backend service URL

### Environment Variables

Set these environment variables in your Render services:

**Backend Service:**
- `SECRET_KEY`: A secure random string for Flask sessions
- `PORT`: Port number (Render will set this automatically)

**Frontend Service:**
- `VITE_BACKEND_URL`: The URL of your backend service

## How It Works

1. Users connect to the backend via Socket.IO
2. The backend manages a queue of users waiting to chat
3. When two users are available, they're paired in a room
4. WebRTC handles the peer-to-peer video/audio connection
5. The backend only handles signaling (offer/answer exchange)

## Security Features

- HTTPS required for camera/microphone access
- CORS properly configured
- No data stored on servers
- Peer-to-peer connections

## Browser Support

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

## License

ISC

