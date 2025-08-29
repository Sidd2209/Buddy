# Buddy - Random Video Chat Application

A modern video chat application similar to Omegle, built with React, WebRTC, and Flask. Supports up to 200 concurrent users with optimized performance and real-time user pairing.

## Features

- 🎥 Real-time video chat with strangers
- 🎤 Audio and video controls
- 🔄 Next chat functionality
- 🎨 Modern, responsive UI
- 🔒 Secure peer-to-peer connections
- 👥 Support for 200+ concurrent users
- ⚡ Optimized performance with connection pooling
- 📊 Real-time server monitoring
- 🏷️ Display partner names instead of "Stranger"
- 🛡️ Automatic cleanup of inactive users

## Tech Stack

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Flask + Socket.IO
- **Real-time Communication**: WebRTC + Socket.IO
- **Performance**: Optimized WebRTC config, connection pooling, user management
- **Deployment**: Render

## Performance & Scalability

### Server Capacity
- **Max Concurrent Users**: 200 (configurable via environment variables)
- **Max Active Rooms**: 100 (configurable via environment variables)
- **User Timeout**: 5 minutes of inactivity
- **Automatic Cleanup**: Removes inactive users every minute

### Optimizations
- **WebRTC Optimization**: Bundle policy, RTCP muxing, ICE transport optimization
- **Socket.IO Tuning**: Optimized ping intervals, buffer sizes, and transport settings
- **Thread Safety**: Proper locking mechanisms for user and room management
- **Memory Management**: Automatic cleanup of disconnected users and rooms

### Monitoring
- Real-time server statistics
- Load percentage monitoring
- Room utilization tracking
- Automatic warnings when approaching capacity

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

## Environment Variables

### Backend Configuration
```bash
# Server capacity
MAX_CONCURRENT_USERS=200
MAX_ROOMS=100
USER_TIMEOUT_SECONDS=300

# Socket.IO settings
SOCKET_PING_TIMEOUT=60
SOCKET_PING_INTERVAL=25
SOCKET_MAX_HTTP_BUFFER_SIZE=1000000

# Cleanup intervals
CLEANUP_INTERVAL_SECONDS=60
ROOM_CLEANUP_INTERVAL_SECONDS=300

# Monitoring
ENABLE_MONITORING=true
MONITORING_INTERVAL_SECONDS=30

# Flask settings
SECRET_KEY=your-secret-key-here
PORT=3000
```

### Frontend Configuration
```bash
VITE_BACKEND_URL=http://localhost:3000
```

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
- `MAX_CONCURRENT_USERS`: Maximum number of concurrent users (default: 200)
- `MAX_ROOMS`: Maximum number of active rooms (default: 100)

**Frontend Service:**
- `VITE_BACKEND_URL`: The URL of your backend service

## How It Works

1. Users connect to the backend via Socket.IO with their name
2. The backend manages a queue of users waiting to chat
3. When two users are available, they're paired in a room with their names exchanged
4. WebRTC handles the peer-to-peer video/audio connection
5. The backend only handles signaling (offer/answer exchange)
6. Automatic cleanup removes inactive users and manages server resources

## Performance Monitoring

The application includes built-in performance monitoring:

- **Server Stats Endpoint**: `/status` - Get current server statistics
- **Real-time Monitoring**: Automatic logging of server load and room utilization
- **Capacity Warnings**: Alerts when server approaches capacity limits
- **User Management**: Automatic cleanup of inactive users

## Security Features

- HTTPS required for camera/microphone access
- CORS properly configured
- No data stored on servers
- Peer-to-peer connections
- User timeout protection
- Rate limiting through connection limits

## Browser Support

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

## Troubleshooting

### Common Issues

1. **Multiple users connecting to one user**: Fixed with improved queue management and state tracking
2. **Slow performance**: Optimized with WebRTC configuration and connection pooling
3. **Server crashes with many users**: Implemented user limits and automatic cleanup
4. **Names not showing**: Now properly exchanges and displays partner names

### Debug Endpoints

- `GET /` - Health check
- `GET /status` - Server statistics and performance metrics

## License

ISC

