import { useEffect, useState } from 'react';

const ConnectionMonitor = ({ peerConnection, isConnected }) => {
  const [connectionQuality, setConnectionQuality] = useState('unknown');

  useEffect(() => {
    if (!peerConnection || !isConnected) {
      setConnectionQuality('unknown');
      return;
    }

    const updateStats = async () => {
      try {
        const stats = await peerConnection.getStats();
        let totalRtt = 0;
        let rttCount = 0;

        stats.forEach((report) => {
          if (report.type === 'candidate-pair' && report.state === 'succeeded') {
            if (report.currentRoundTripTime) {
              totalRtt += report.currentRoundTripTime;
              rttCount++;
            }
          }
        });

        const avgRtt = rttCount > 0 ? totalRtt / rttCount : 0;
        
        // Simple quality based on RTT
        let quality = 'excellent';
        if (avgRtt > 200) {
          quality = 'poor';
        } else if (avgRtt > 100) {
          quality = 'fair';
        } else if (avgRtt > 50) {
          quality = 'good';
        }

        setConnectionQuality(quality);
      } catch (error) {
        console.error('Error getting connection stats:', error);
      }
    };

    const interval = setInterval(updateStats, 3000); // Update every 3 seconds
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
    <div className="absolute top-4 right-4 bg-black/50 backdrop-blur-sm rounded-lg p-2 text-white text-xs">
      <div className="flex items-center space-x-1">
        <span>{getQualityIcon()}</span>
        <span className={getQualityColor()}>
          {connectionQuality.charAt(0).toUpperCase() + connectionQuality.slice(1)}
        </span>
      </div>
    </div>
  );
};

export default ConnectionMonitor;
