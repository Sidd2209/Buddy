import { useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";

// Use localhost for local development
const BACKEND_URL = (import.meta.env.VITE_BACKEND_URL) || "http://localhost:3000";

// Debug logging
console.log("Environment variables:", import.meta.env);
console.log("Backend URL:", BACKEND_URL);
console.log("VITE_BACKEND_URL value:", import.meta.env.VITE_BACKEND_URL);

// WebRTC configuration with STUN servers
const rtcConfiguration = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
    { urls: 'stun:stun2.l.google.com:19302' },
    { urls: 'stun:stun3.l.google.com:19302' },
    { urls: 'stun:stun4.l.google.com:19302' }
  ],
  iceCandidatePoolSize: 10
};

const Room = ({ name, localAudioTrack, localVideoTrack }) => {
  const [lobby, setLobby] = useState(true);
  const [socket, setSocket] = useState(null);
  const [sendingPc, setSendingPc] = useState(null);
  const [receivingPc, setReceivingPc] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState("Connecting...");
  const [error, setError] = useState(null);
  const [partnerDisconnected, setPartnerDisconnected] = useState(false);

  const remoteVideoRef = useRef(null);
  const localVideoRef = useRef(null);

  // Cleanup function for WebRTC connections
  const cleanupConnections = () => {
    if (sendingPc) {
      sendingPc.close();
      setSendingPc(null);
    }
    if (receivingPc) {
      receivingPc.close();
      setReceivingPc(null);
    }
    // Clear remote video stream
    if (remoteVideoRef.current) {
      remoteVideoRef.current.srcObject = null;
    }
  };

  useEffect(() => {
    console.log("Connecting to backend:", BACKEND_URL);
    
    const s = io(BACKEND_URL, { 
      transports: ["websocket", "polling"], 
      forceNew: true,
      timeout: 20000,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    });

    s.on("connect", () => {
      console.log("Connected to server:", s.id);
      setConnectionStatus("Connected to server");
      setPartnerDisconnected(false);
      // Ensure we're in the queue when connected
      s.emit('ready-for-new');
    });

    s.on("connect_error", (error) => {
      console.error("Connection error:", error);
      setError(`Connection failed: ${error.message}`);
      setConnectionStatus("Connection failed");
    });

    s.on("disconnect", (reason) => {
      console.log("Disconnected:", reason);
      setConnectionStatus("Disconnected");
    });

    s.on("partner-disconnected", () => {
      console.log("Partner disconnected");
      setPartnerDisconnected(true);
      setConnectionStatus("Partner disconnected - finding new match...");
      cleanupConnections();
      
      // Immediately queue for a new match
      s.emit('ready-for-new');
      
      // Show message briefly while we wait for server to pair
      setTimeout(() => {
        setPartnerDisconnected(false);
        setLobby(true);
        setConnectionStatus("Finding someone...");
      }, 1200);
    });

    s.on("send-offer", async ({ roomId }) => {
      console.log("Creating offer for room:", roomId);
      setLobby(false);
      setPartnerDisconnected(false);
      setConnectionStatus("Establishing connection...");
      
      try {
        const pc = new RTCPeerConnection(rtcConfiguration);
        setSendingPc(pc);

        // Add local tracks (this peer will be the offerer)
        if (localVideoTrack) {
          console.log("Adding local video track");
          pc.addTrack(localVideoTrack);
        }
        if (localAudioTrack) {
          console.log("Adding local audio track");
          pc.addTrack(localAudioTrack);
        }

        // Prepare a media stream for remote tracks
        if (remoteVideoRef.current && !remoteVideoRef.current.srcObject) {
          remoteVideoRef.current.srcObject = new MediaStream();
        }

        pc.ontrack = (e) => {
          console.log("Received remote track:", e.track.kind);
          const stream = remoteVideoRef.current?.srcObject;
          if (stream && stream.addTrack) {
            stream.addTrack(e.track);
            setConnectionStatus("Connected");
          }
        };

        pc.onicecandidate = (e) => {
          if (e.candidate) {
            console.log("Sending ICE candidate");
            s.emit("add-ice-candidate", { candidate: e.candidate, type: "sender", roomId });
          }
        };

        pc.oniceconnectionstatechange = () => {
          console.log("ICE connection state:", pc.iceConnectionState);
          if (pc.iceConnectionState === 'connected' || pc.iceConnectionState === 'completed') {
            setConnectionStatus("Connected");
          } else if (pc.iceConnectionState === 'failed') {
            setError("Connection failed. Please try again.");
          }
        };

        pc.onnegotiationneeded = async () => {
          try {
            console.log("Creating offer...");
            const sdp = await pc.createOffer();
            await pc.setLocalDescription(sdp);
            console.log("Local description set, signaling state:", pc.signalingState);
            s.emit("offer", { sdp, roomId });
          } catch (err) {
            console.error("Error creating offer:", err);
            setError("Failed to create connection offer");
          }
        };
      } catch (err) {
        console.error("Error setting up peer connection:", err);
        setError("Failed to setup peer connection");
      }
    });

    // New: wait-offer role; prepare PC and only answer once offer arrives
    s.on("wait-offer", async ({ roomId }) => {
      console.log("Waiting for offer in room:", roomId);
      setLobby(false);
      setPartnerDisconnected(false);
      setConnectionStatus("Establishing connection...");

      try {
        const pc = new RTCPeerConnection(rtcConfiguration);

        if (localVideoTrack) {
          pc.addTrack(localVideoTrack);
        }
        if (localAudioTrack) {
          pc.addTrack(localAudioTrack);
        }

        if (remoteVideoRef.current && !remoteVideoRef.current.srcObject) {
          remoteVideoRef.current.srcObject = new MediaStream();
        }

        pc.ontrack = (e) => {
          const stream = remoteVideoRef.current?.srcObject;
          if (stream && stream.addTrack) {
            stream.addTrack(e.track);
            setConnectionStatus("Connected");
          }
        };

        pc.onicecandidate = (e) => {
          if (e.candidate) {
            s.emit("add-ice-candidate", { candidate: e.candidate, type: "receiver", roomId });
          }
        };

        pc.oniceconnectionstatechange = () => {
          if (pc.iceConnectionState === 'connected' || pc.iceConnectionState === 'completed') {
            setConnectionStatus("Connected");
          } else if (pc.iceConnectionState === 'failed') {
            setError("Connection failed. Please try again.");
          }
        };

        // Store this PC as the receiving one; will set remote and answer upon offer event
        setReceivingPc(pc);
      } catch (err) {
        console.error("Error preparing receiver peer connection:", err);
        setError("Failed to prepare connection");
      }
    });

    s.on("offer", async ({ roomId, sdp: remoteSdp }) => {
      console.log("Received offer for room:", roomId);
      setLobby(false);
      setPartnerDisconnected(false);
      setConnectionStatus("Establishing connection...");
      
      try {
        // Use existing receivingPc if present (set by wait-offer), else create
        let pcRef = receivingPc;
        if (!pcRef) {
          pcRef = new RTCPeerConnection(rtcConfiguration);

          if (localVideoTrack) {
            pcRef.addTrack(localVideoTrack);
          }
          if (localAudioTrack) {
            pcRef.addTrack(localAudioTrack);
          }

          if (remoteVideoRef.current && !remoteVideoRef.current.srcObject) {
            remoteVideoRef.current.srcObject = new MediaStream();
          }

          pcRef.ontrack = (e) => {
            const stream = remoteVideoRef.current?.srcObject;
            if (stream && stream.addTrack) {
              stream.addTrack(e.track);
              setConnectionStatus("Connected");
            }
          };

          pcRef.onicecandidate = (e) => {
            if (e.candidate) {
              s.emit("add-ice-candidate", { candidate: e.candidate, type: "receiver", roomId });
            }
          };

          pcRef.oniceconnectionstatechange = () => {
            if (pcRef.iceConnectionState === 'connected' || pcRef.iceConnectionState === 'completed') {
              setConnectionStatus("Connected");
            } else if (pcRef.iceConnectionState === 'failed') {
              setError("Connection failed. Please try again.");
            }
          };

          setReceivingPc(pcRef);
        }

        await pcRef.setRemoteDescription(remoteSdp);
        const sdp = await pcRef.createAnswer();
        await pcRef.setLocalDescription(sdp);

        s.emit("answer", { roomId, sdp });
      } catch (err) {
        console.error("Error handling offer:", err);
        setError("Failed to handle connection offer");
      }
    });

    s.on("answer", ({ sdp: remoteSdp }) => {
      console.log("Received answer");
      setSendingPc((pc) => { 
        if (pc && pc.signalingState !== 'closed') {
          if (pc.signalingState === 'have-local-offer') {
            pc.setRemoteDescription(remoteSdp).catch(err => {
              console.error("Error setting remote description:", err);
            });
          } else {
            setTimeout(() => {
              if (pc.signalingState === 'have-local-offer') {
                pc.setRemoteDescription(remoteSdp).catch(err => {
                  console.error("Error setting remote description (retry):", err);
                });
              }
            }, 100);
          }
        }
        return pc; 
      });
    });

    s.on("lobby", () => {
      console.log("Back in lobby");
      setLobby(true);
      setPartnerDisconnected(false);
      setConnectionStatus("Finding someone...");
    });

    s.on("add-ice-candidate", ({ candidate, type }) => {
      console.log("Received ICE candidate:", type);
      if (type === "sender") {
        setReceivingPc((pc) => { 
          if (pc) {
            pc.addIceCandidate(candidate).catch(err => {
              console.error("Error adding ICE candidate:", err);
            });
          }
          return pc; 
        });
      } else {
        setSendingPc((pc) => { 
          if (pc) {
            pc.addIceCandidate(candidate).catch(err => {
              console.error("Error adding ICE candidate:", err);
            });
          }
          return pc; 
        });
      }
    });

    setSocket(s);
    return () => {
      console.log("Cleaning up socket connection");
      cleanupConnections();
      s.emit('manual-disconnect');
      s.disconnect();
    };
  }, [name, localAudioTrack, localVideoTrack]);

  useEffect(() => {
    if (localVideoRef.current && localVideoTrack) {
      console.log("Setting local video stream");
      localVideoRef.current.srcObject = new MediaStream([localVideoTrack]);
    }
  }, [localVideoTrack]);

  const toggleVideo = () => {
    if (localVideoTrack) {
      localVideoTrack.enabled = !localVideoTrack.enabled;
      console.log("Video toggled:", localVideoTrack.enabled);
    }
  };

  const toggleAudio = () => {
    if (localAudioTrack) {
      localAudioTrack.enabled = !localAudioTrack.enabled;
      console.log("Audio toggled:", localAudioTrack.enabled);
    }
  };

  const nextChat = () => {
    cleanupConnections();
    if (socket) {
      // Use new 'next' flow: server tears down room and requeues both users
      socket.emit('next');
      setLobby(true);
      setPartnerDisconnected(false);
      setConnectionStatus("Finding someone...");
      return;
    }
    window.location.href = "/";
  };

  const quitChat = () => {
    // Fully quit: notify server to remove this user and leave app
    cleanupConnections();
    if (socket) {
      socket.emit('manual-disconnect');
      socket.disconnect();
    }
    window.location.href = "/";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex flex-col">
      <div className="bg-white/10 backdrop-blur-lg border-b border-white/20 p-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-white">Buddy</h1>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${lobby ? 'bg-yellow-400' : partnerDisconnected ? 'bg-red-400' : 'bg-green-400'} animate-pulse`} />
              <span className="text-gray-300 text-sm">{connectionStatus}</span>
            </div>
          </div>
          <div className="text-white text-sm">Welcome, <span className="font-semibold">{name}</span></div>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/20 border border-red-500/50 p-4 text-red-200 text-center">
          {error}
          <button 
            onClick={() => setError(null)}
            className="ml-2 text-red-300 hover:text-red-100"
          >
            ✕
          </button>
        </div>
      )}

      {partnerDisconnected && (
        <div className="bg-orange-500/20 border border-orange-500/50 p-4 text-orange-200 text-center">
          <p>Your partner disconnected. Finding a new match...</p>
        </div>
      )}

      <div className="flex-1 flex items-center justify-center p-4">
        <div className="max-w-6xl w-full">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="relative aspect-video rounded-2xl overflow-hidden shadow-2xl border-2 border-white/20 bg-black/20">
              <video autoPlay muted playsInline ref={localVideoRef} className="w-full h-full object-cover" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
              <div className="absolute bottom-4 left-4 bg-black/50 backdrop-blur-sm px-4 py-2 rounded-full text-white font-medium">You</div>
              {localVideoTrack && !localVideoTrack.enabled && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                  <div className="text-white text-center">
                    <div className="w-16 h-16 mx-auto mb-2 bg-white/20 rounded-full flex items-center justify-center">
                      <span className="text-2xl">📹</span>
                    </div>
                    <p className="text-sm">Video Off</p>
                  </div>
                </div>
              )}
            </div>

            <div className="relative aspect-video rounded-2xl overflow-hidden shadow-2xl border-2 border-white/20 bg-black/20">
              <video autoPlay playsInline ref={remoteVideoRef} className="w-full h-full object-cover" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
              <div className="absolute bottom-4 left-4 bg-black/50 backdrop-blur-sm px-4 py-2 rounded-full text-white font-medium">Stranger</div>
              {(lobby || partnerDisconnected) && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-white text-center">
                    <div className="w-16 h-16 mx-auto mb-4 bg-white/20 rounded-full flex items-center justify-center animate-pulse" />
                    <p className="text-sm">
                      {partnerDisconnected ? "Partner disconnected. Finding new match..." : "Waiting for someone to join..."}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="flex justify-center space-x-4">
            <button
              className="px-8 py-3 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl text-white font-medium hover:bg-white/20 transition-all duration-300"
              onClick={toggleVideo}
            >
              {localVideoTrack?.enabled ? "Turn Off Video" : "Turn On Video"}
            </button>
            <button
              className="px-8 py-3 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl text-white font-medium hover:bg-white/20 transition-all duration-300"
              onClick={toggleAudio}
            >
              {localAudioTrack?.enabled ? "Turn Off Audio" : "Turn On Audio"}
            </button>
            <button
              className={`px-8 py-3 transition-all duration-300 text-white font-medium rounded-xl shadow-lg ${
                lobby || partnerDisconnected 
                  ? 'bg-gray-500 cursor-not-allowed opacity-50' 
                  : 'bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700'
              }`}
              onClick={nextChat}
              disabled={lobby || partnerDisconnected}
            >Next</button>
            <button
              className="px-8 py-3 bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-800 transition-all duration-300 text-white font-medium rounded-xl shadow-lg"
              onClick={quitChat}
            >Quit</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Room;