# FreeTalk - Video Chat Application

A modern video chat application built with React frontend and Flask backend, featuring WebRTC for peer-to-peer video communication.

## Features

- 🎥 Real-time video chat with strangers
- 🎤 Audio and video controls
- 🎨 Modern, responsive UI with glass morphism design
- 🔄 Automatic user pairing system
- 📱 Mobile-responsive design
- 🚀 Offline-first architecture

## Tech Stack

### Frontend
- React 18
- Vite
- Tailwind CSS
- Socket.IO Client
- WebRTC

### Backend
- Flask
- Flask-SocketIO
- Python 3.8+

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

## Installation & Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd freeTalk
```

### 2. Backend Setup (Flask)

Navigate to the backend directory:
```bash
cd backend
```

Create a virtual environment:
```bash
python -m venv venv
```

Activate the virtual environment:
- **Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

### 3. Frontend Setup (React)

Navigate to the project root:
```bash
cd ..
```

Install Node.js dependencies:
```bash
npm install
```

## Running the Application

### 1. Start the Flask Backend

In the backend directory (with virtual environment activated):
```bash
python app.py
```

The backend will start on `http://localhost:3000`

### 2. Start the React Frontend

In the project root directory:
```bash
npm run dev
```

The frontend will start on `http://localhost:5173`

### 3. Access the Application

Open your browser and navigate to `http://localhost:5173`

## Usage

1. **Enter Your Name**: On the landing page, enter your name in the input field
2. **Allow Camera Access**: Grant camera and microphone permissions when prompted
3. **Start Chatting**: Click "Start Chatting" to be paired with a random stranger
4. **Video Controls**: Use the control buttons to toggle video/audio or end the call

## Project Structure

```
freeTalk/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── user_manager.py     # User management logic
│   ├── room_manager.py     # Room management logic
│   └── requirements.txt    # Python dependencies
├── src/
│   ├── components/
│   │   ├── Landing.jsx     # Landing page component
│   │   └── Room.jsx        # Video chat room component
│   ├── App.jsx             # Main app component
│   ├── App.css             # Custom styles
│   └── index.css           # Global styles
├── package.json            # Node.js dependencies
└── README.md              # This file
```

## Development

### Backend Development

The Flask backend handles:
- WebSocket connections via Flask-SocketIO
- User pairing and room management
- WebRTC signaling (offer/answer exchange)
- ICE candidate exchange

### Frontend Development

The React frontend provides:
- Modern, responsive UI
- WebRTC peer connections
- Real-time video/audio streaming
- User interface controls

## Troubleshooting

### Common Issues

1. **Camera not working**: Ensure you've granted camera permissions in your browser
2. **Connection issues**: Check that both backend and frontend are running
3. **Port conflicts**: If port 3000 is in use, modify the port in `backend/app.py`

### Browser Compatibility

This application works best with:
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions, please open an issue in the repository.

