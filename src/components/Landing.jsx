import { useEffect, useRef, useState } from "react";
import Room from "./Room";

export const Landing = () => {
  const [name, setName] = useState("");
  const [localAudioTrack, setLocalAudioTrack] = useState(null);
  const [localVideoTrack, setLocalVideoTrack] = useState(null);
  const [joined, setJoined] = useState(false);
  const [mediaError, setMediaError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const videoRef = useRef(null);

  const requestMediaAccess = async () => {
    try {
      setIsLoading(true);
      setMediaError(null);
      
      console.log("Requesting camera and microphone permissions...");
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: "user"
        }, 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      
      console.log("Media stream obtained:", stream);
      
      setLocalAudioTrack(stream.getAudioTracks()[0]);
      setLocalVideoTrack(stream.getVideoTracks()[0]);
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      
      setIsLoading(false);
    } catch (e) {
      console.error("Error accessing media devices:", e);
      setMediaError(e.message);
      setIsLoading(false);
      
      if (e.name === 'NotAllowedError') {
        setMediaError("Camera and microphone access was denied. Please allow access and try again.");
      } else if (e.name === 'NotFoundError') {
        setMediaError("No camera or microphone found. Please connect a device and try again.");
      } else if (e.name === 'NotSupportedError') {
        setMediaError("Your browser doesn't support camera/microphone access. Please use a modern browser.");
      } else {
        setMediaError(`Media access error: ${e.message}`);
      }
    }
  };

  const handleJoin = async () => {
    if (!name.trim()) {
      alert("Please enter your name.");
      return;
    }

    if (!localAudioTrack || !localVideoTrack) {
      await requestMediaAccess();
      if (!localAudioTrack || !localVideoTrack) {
        return; // Media access failed
      }
    }

    setJoined(true);
  };

  if (joined) {
    return <Room name={name} localAudioTrack={localAudioTrack} localVideoTrack={localVideoTrack} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center p-4">
      <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 shadow-2xl border border-white/20 max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">FreeTalk</h1>
          <p className="text-gray-300 text-lg">Connect with strangers worldwide</p>
        </div>

        {!localVideoTrack && !isLoading && !mediaError && (
          <div className="mb-6">
            <button
              onClick={requestMediaAccess}
              className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 text-white font-semibold rounded-xl shadow-lg"
            >
              Enable Camera & Microphone
            </button>
          </div>
        )}

        {isLoading && (
          <div className="mb-6 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
            <p className="text-white text-lg">Accessing camera and microphone...</p>
          </div>
        )}

        {mediaError && (
          <div className="mb-6 p-4 bg-red-500/20 border border-red-500/50 rounded-xl">
            <p className="text-red-300 text-sm mb-3">{mediaError}</p>
            <button
              onClick={requestMediaAccess}
              className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm"
            >
              Try Again
            </button>
          </div>
        )}

        {localVideoTrack && (
          <div className="relative w-full aspect-square rounded-2xl overflow-hidden shadow-2xl mb-6 border-2 border-white/20">
            <video autoPlay muted ref={videoRef} className="w-full h-full object-cover" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
            <div className="absolute bottom-4 left-4 bg-black/50 backdrop-blur-sm px-3 py-1 rounded-full text-white text-sm">Camera Preview</div>
          </div>
        )}

        <div className="mb-6">
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter your name"
            className="w-full p-4 text-white bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent placeholder-gray-400 transition-all duration-300"
            onKeyDown={(e) => { if (e.key === 'Enter') handleJoin(); }}
          />
        </div>

        <button
          onClick={handleJoin}
          disabled={!name.trim() || isLoading}
          className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 text-white font-semibold text-lg rounded-xl shadow-lg transform hover:scale-105 active:scale-95"
        >
          Start Chatting
        </button>
      </div>
    </div>
  );
};

export default Landing;
