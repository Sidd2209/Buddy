import { useEffect, useState } from 'react';

const ConnectionMonitor = ({ peerConnection, isConnected }) => {
  const [connectionQuality, setConnectionQuality] = useState('unknown');
  const [stats, setStats] = useState({});

  useEffect(() => {
    if (!peerConnection || !isConnected) {
      setConnectionQuality('unknown');
      return;
    }

    const updateStats = async () => {
      try {
        const stats = await peerConnection.getStats();
        let totalBytesReceived = 0;
        let totalBytesSent = 0;
        let totalPacketsLost = 0;
        let totalRtt = 0;
        let rttCount = 0;

        stats.forEach((report) => {
          if (report.type === 'inbound-rtp' && report.mediaType === 'video') {
            totalBytesReceived += report.bytesReceived || 0;
            totalPacketsLost += report.packetsLost || 0;
          }
          if (report.type === 'outbound-rtp' && report.mediaType === 'video') {
            totalBytesSent += report.bytesSent || 0;
          }
          if (report.type === 'candidate-pair' && report.state === 'succeeded') {
            if (report.currentRoundTripTime) {
              totalRtt += report.currentRoundTripTime;
              rttCount++;
            }
          }
        });

        const avgRtt = rttCount > 0 ? totalRtt / rttCount : 0;
        
        // Determine connection quality based on RTT and packet loss
        let quality = 'excellent';
        if (avgRtt > 200 || totalPacketsLost > 10) {
          quality = 'poor';
        } else if (avgRtt > 100 || totalPacketsLost > 5) {
          quality = 'fair';
        } else if (avgRtt > 50) {
          quality = 'good';
        }

        setConnectionQuality(quality);
        setStats({
          bytesReceived: totalBytesReceived,
          bytesSent: totalBytesSent,
          packetsLost: totalPacketsLost,
          avgRtt: avgRtt
        });
      } catch (error) {
        console.error('Error getting connection stats:', error);
      }
    };

    const interval = setInterval(updateStats, 2000); // Update every 2 seconds
    return () => clearInterval(interval);
  }, [peerConnection, isConnected]);

  const getQualityColor = () => {
    switch (connectionQuality) {
      case 'excellent': return 'text-green-400';
      case 'good': return 'text-yellow-400';
      case 'fair': return 'text-orange-400';
      case 'poor': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getQualityIcon = () => {
    switch (connectionQuality) {
      case 'excellent': return '🟢';
      case 'good': return '🟡';
      case 'fair': return '🟠';
      case 'poor': return '🔴';
      default: return '⚪';
    }
  };

  if (!isConnected) return null;

  return (
    <div className="absolute top-4 right-4 bg-black/50 backdrop-blur-sm rounded-lg p-3 text-white text-sm">
      <div className="flex items-center space-x-2">
        <span>{getQualityIcon()}</span>
        <span className={getQualityColor()}>
          {connectionQuality.charAt(0).toUpperCase() + connectionQuality.slice(1)}
        </span>
      </div>
      {stats.avgRtt > 0 && (
        <div className="text-xs text-gray-300 mt-1">
          RTT: {Math.round(stats.avgRtt)}ms
        </div>
      )}
    </div>
  );
};

export default ConnectionMonitor;
